import logging
import socket
import time
from typing import Union

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S',
                    level=logging.DEBUG)

MAGIC_NUMBER_WHEN_RETURNING_FROM_BACK = 65
MAGIC_NUMBER_WHEN_RUNNING_AT_BACK = 20
DISTANCE_TO_START_TURN = 60

RPI_IP = '192.168.16.16'
RPI_PORT = 8080
HOST_PORT = 8080
logging.getLogger().setLevel(logging.DEBUG)

SPEED_SET = {
    "HighSpeed": "5000",
    "MediumSpeed": "2500",
    "SlowSpeed": "1000",
}

DISTANCE_SET = {
    "HighSpeed": {
        1: "0099",
        5: "0015",
        10: "0090",
        20: "0260",
        30: "0580",
        40: "0900",
        50: "1150",
        60: "1450",
        70: "1750",
        80: "2000",
        90: "2350",
        100: "2630",
    },
    "MediumSpeed": {
        1: "0099",
        5: "0107",
        10: "0150",
        20: "0340",
        30: "0660",
    },
    "SlowSpeed": {
        1: "0099",
        5: "0107",
        10: "0150",
        20: "0420",
        30: "0660",
    }
}

DIRECTION_SET = {
    "f": "f",
    "b": "b",
}

ANGLE_SET = {
    "Left": '111',
    "Right": '215',
    "Straight": '149',
}


# straight line commands: direction + speed + distance
# turn 90 degree right and left as in task 1

# noinspection PyBroadException
class Server:
    def __init__(self):
        self.host = ''
        self.port = HOST_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._connect()

        # env settings
        self.obstacle_size = 60
        self.obstacle_distance = None
        self.candidate_distance_list = dict()

        for k in DISTANCE_SET.keys():
            self.candidate_distance_list[k] = sorted(list(DISTANCE_SET[k].keys()))

        # current status
        self.current_distance_to_front = None
        self.prev_distance_to_front = None
        self.prev_moved_dist = None
        self.current_distance_to_garage = None
        self.current_distance_to_obstacle = None
        self.has_thing_at_left = None
        self.has_thing_at_right = None

        self.horizontal_shift = 0.
        self.moved = 0.
        self.found_the_obs_at_side = None

        self.left_turn_command = 'f1650500011100'
        self.left_turn_with_ir_command = 'f1650500011101'
        self.right_turn_command = 'f1900500021500'
        self.right_turn_with_us_command = 'f1900500021510'

        # path planning related
        self.flipped = False  # default to be clockwise turn

        """
        stages:
        0: no sensor data received; obstacle distance, size unknown;
        1: obstacle distance located, otw to it
        2: adjusting position, parallel to the obstacle front, to find the edge
        3: reversed a bit from the edge. ready to make right turn
        4: half way passing the obstacle, need another 90 degree right turn to go to the back of obs
        5: at the back of the obstacle, heading to the position for another right turn (dist known)
        6: ready to make right turn from the back
        7: half way passing the obstacle, check if garage in front
        8: adjusting position, parallel to the obstacle front

        (stage 9 is actually unreachable, as is handled by 8)
        9: ready to make the left turn to face the garage 

        10: on the way to the garage
        11: stopped
        """
        self.stage = 0

        self.incoming_msg_handlers = {
            "F": self._act,
            "Y": self._handle_end_of_step_msg,
        }

        self.terminated = False

    def _connect(self):
        while True:
            try:
                logging.info('Establishing connection with RPI')
                self.socket.connect((RPI_IP, RPI_PORT))
                logging.info('Successfully connected with RPI')
                break
            except:
                logging.exception('Connection with RPI failed')
            logging.info("Retrying RPI connection...")
            time.sleep(1)

    def listen(self):
        while not self.terminated:
            logging.info("Listening msg from RPI...")
            msg = self.read()
            if not msg:
                continue

            try:
                msg_type, actual_msg = msg[0], msg[1:] if len(msg) > 1 else None
                if msg_type not in self.incoming_msg_handlers:
                    raise ValueError(f"Unexpected msg type {msg_type}! msg: {msg}")
                logging.info("Start handling message...")
                self.incoming_msg_handlers[msg_type](msg=actual_msg)
                logging.info("Done handling message...")
            except:
                logging.exception("Failed to handle incoming message")

    def read(self) -> Union[None, str]:
        try:
            message = self.socket.recv(2048).strip()

            if len(message) > 0:
                message = message.decode()
                logging.info(f'From RPI: {message}')
                return message

            return None
        except:
            logging.exception('RPI read failed')

    def write(self, message):
        try:
            logging.info(f'To RPI: {message}')
            self.socket.send(message.encode())
        except Exception as error:
            logging.exception('Algorithm write failed')

    @staticmethod
    def _form_command(direction, distance, speed, angle="Straight", take_us: bool = False, take_ir: bool = False):
        # print(direction, distance, speed)
        return DIRECTION_SET[direction] + DISTANCE_SET[speed][distance] + SPEED_SET[speed] + ANGLE_SET[angle] + \
               ("1" if take_us else "0") + ("1" if take_ir else "0")

    @staticmethod
    def _parse_sensor_data(msg: str):
        """
        H200,False
        :param msg:
        :return:
        """
        us, ir = msg.split(",")
        try:
            ir = eval(ir)
        except Exception:
            ir = False
        return int(us), ir

    def _handle_end_of_step_msg(self, msg: str):
        # TODO:
        #  1. parse sensor data
        #  2. get distance to the obstacle / see if obstacle at the side
        #  3. (optional at stage 3) ask cv module to take pic, see if bulls eyes
        #  4. call _plan_and_act
        # Step 1 & 2
        distance_to_front, self.has_thing_at_right = self._parse_sensor_data(msg)
        if distance_to_front != 0:  # when it has a valid reading
            self.current_distance_to_front = distance_to_front
            if self.stage in [0, 1]:
                self.current_distance_to_obstacle = distance_to_front
            # elif self.stage in [3, 7]:
            #     self.current_distance_to_left_side_wall = distance_to_front
            # elif self.stage == 5:
            #     self.current_distance_to_right_side_wall = distance_to_front
            elif self.stage == 10:
                self.current_distance_to_garage = distance_to_front

        if self.obstacle_distance is None:
            self.obstacle_distance = distance_to_front + 5
            # 1 is hardcoded as there is a blind instruction of moving forward 1 com

        # Step 3
        if self.stage in [0, 1]:
            # id, distance, angle = detectbullseye()
            # if angle is small, means right in front of the car, flip the strategy
            pass

        # Step 4
        self._act()

    def _get_biggest_smaller_dist(self, cat, target):
        for c in self.candidate_distance_list[cat][::-1]:
            if c <= target:
                return c
        return self.candidate_distance_list[cat][0]

    def _act(self, msg: str = None):
        # TODO: based on the current stage and status, choose action
        cmd = None
        if self.stage == 0:
            self.stage = 1
            cmd = self._form_command("f", 5, "SlowSpeed", take_us=True)
        elif self.stage == 1:
            # FIXME: logic problem and untested
            # if self.prev_distance_to_front is not None and self.current_distance_to_obstacle < self.prev_distance_to_front:
            #     self.current_distance_to_obstacle = self.prev_distance_to_front - self.prev_moved_dist
            if (self.current_distance_to_obstacle - DISTANCE_TO_START_TURN) < 5:  # already can make the turn
                self.stage = 2
                # make left turn
                cmd = self.left_turn_with_ir_command
                self.prev_distance_to_front = None
            else:
                buffer_dist = self.current_distance_to_obstacle - DISTANCE_TO_START_TURN
                dist = self._get_biggest_smaller_dist("HighSpeed", buffer_dist)
                # determine speed based on dist
                # form command
                cmd = self._form_command("f", dist, "HighSpeed", take_us=True)
                # self.prev_distance_to_front = self.current_distance_to_obstacle
                # self.prev_moved_dist = dist
        elif self.stage == 2:
            if self.found_the_obs_at_side is None:
                self.found_the_obs_at_side = self.has_thing_at_right
            if self.has_thing_at_right != self.found_the_obs_at_side:
                self.stage = 3
                # (originally no, now just found the edge), or (originally yes, after driving forward, now no)
                # anyways it's now at the edge
                # reverse 10 cm to make the turn
                self.horizontal_shift += 5
                cmd = self._form_command("b", 5, "HighSpeed")
            else:
                if self.has_thing_at_right is True:
                    # move slowly forward 5 cm
                    self.horizontal_shift -= 5
                    cmd = self._form_command("f", 5, "HighSpeed", take_ir=True)
                    pass
                else:
                    # move slowly backward 5 cm
                    self.horizontal_shift += 5
                    cmd = self._form_command("b", 5, "HighSpeed", take_ir=True)
                    pass
        elif self.stage == 3:
            self.stage = 4
            # make 90 degree right turn
            cmd = self.right_turn_command
        elif self.stage == 4:
            self.stage = 5
            # make 90 right turn
            cmd = self.right_turn_command
        elif self.stage == 5:
            # calculate the distance to the ideal turning position
            self.stage = 6
            # fast move towards it
            cmd = self._form_command("f", MAGIC_NUMBER_WHEN_RUNNING_AT_BACK, "HighSpeed")
        elif self.stage == 6:
            self.stage = 7
            # make right turn
            #             cmd = self.right_turn_with_us_command
            cmd = self.right_turn_command
        elif self.stage == 7:
            #             if abs(self.current_distance_to_front - (self.obstacle_distance + 50)) < 2:  # garage right in front
            #                 self.stage = 10
            #                 self.current_distance_to_garage = self.current_distance_to_front
            #                 # stage 10 logic
            #                 movable_dist = self.current_distance_to_garage - 20  # car's length / 2 with buffer
            #                 dist = self._get_biggest_smaller_dist("HighSpeed", movable_dist)
            #                 # fast forward + biggest movable_dist
            #                 cmd = self._form_command("f", dist, "HighSpeed", take_us=True)
            #             else:
            #                 self.stage = 8
            #                 # make 90 right turn
            #                 cmd = self.right_turn_command
            self.stage = 8
            cmd = self.right_turn_command
        elif self.stage == 8:
            """
            calculate the distance to move based on previously moved distance
            if distance = 0, reached, then to stage 9
            else move slowly forward  # not gonna be far

            original position after the 1st turn: x
            x + self.horizontal_shift = 10 ~ 15, moving right is +, moving left is -, take obstacle left end as 0
            now the car is estimated to be at x0 after coming back from the back of the obstacle
            x0 = 40
            we want it to move distance y s.t.
            x0 + y = x - 40 (the position that when making one left turn, it is exactly on the coming way)

            we have:
            x0 + y = (10 ~ 15) - self.horizontal_shift - 40
            y = (10 ~ 15) - self.horizontal_shift - x0 - 40

            since x0 should roughly be 40
            so:

            y = (-65 ~ -70) - self.horizontal_shift

            if y < 0, move left abs(y)
            if y > 0, move right abs(y)
            """
            # ideally should be
            y = MAGIC_NUMBER_WHEN_RETURNING_FROM_BACK - self.horizontal_shift + self.moved
            if abs(y) < 5:
                self.stage = 10
                cmd = self.left_turn_command
            else:
                movable_dist = self._get_biggest_smaller_dist("HighSpeed", abs(y))
                if y < 0:
                    # mid move fwd movable_dist
                    self.moved += movable_dist
                    cmd = self._form_command("f", movable_dist, "HighSpeed")
                else:
                    # mid move back movable_dist
                    self.moved -= movable_dist
                    cmd = self._form_command("b", movable_dist, "HighSpeed")
        # elif self.stage == 9:
        #     self.stage = 10
        #     # make left turn
        #     cmd = self.left_turn_command
        elif self.stage == 10:
            # if self.prev_distance_to_front is not None and self.current_distance_to_obstacle < self.prev_distance_to_front:
            #     self.current_distance_to_obstacle = self.prev_distance_to_front - self.prev_moved_dist
            movable_dist = self.current_distance_to_front - 15  # car's length / 2 with buffer
            if movable_dist < 5:
                self.stage = 11
                self.terminated = True
                return  # end of task
            dist = self._get_biggest_smaller_dist("HighSpeed", movable_dist)
            # fast forward + biggest movable_dist
            cmd = self._form_command("f", dist, "HighSpeed", take_us=True)
            # self.prev_distance_to_front = self.current_distance_to_obstacle
            # self.prev_moved_dist = dist

        # print(self.stage)
        self.write(message="I" + cmd)


if __name__ == '__main__':
    Server().listen()
