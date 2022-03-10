import logging
import math
import socket
import time
from typing import Union

RPI_IP = '192.168.16.16'
RPI_PORT = 8080
HOST_PORT = 8080
logging.getLogger().setLevel(logging.DEBUG)

SPEED_SET = {
    "HighSpeed": "",
    "MediumSpeed": "",
    "SlowSpeed": "",
}

DIRECTION_SET = {
    "Forward": "f",
    "Backward": "b",
}

DISTANCE_SET = {
    1: "",
    5: "",
    10: "",
    20: "",
    30: "",
}

ANGLE_SET = {
    "Left": '111',
    "Right": '199',
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
        self.candidate_distance_list = sorted(list(DISTANCE_SET.keys()))

        # current status
        self.current_distance_to_front = None
        self.current_distance_to_garage = None
        self.current_distance_to_obstacle = None
        self.has_thing_at_left = None
        self.has_thing_at_right = None

        self.horizontal_shift = 0.
        self.moved = 0.
        self.found_the_obs_at_side = None

        self.left_turn_command = 'f12601000111'
        self.right_turn_command = 'f19801000215'

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
            msg = self.read()
            if not msg:
                continue

            try:
                msg_type, actual_msg = msg[0], msg[1:] if len(msg) > 1 else None
                if msg_type not in self.incoming_msg_handlers:
                    raise ValueError(f"Unexpected msg type {msg_type}! msg: {msg}")
                self.incoming_msg_handlers[msg_type](msg=actual_msg)
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
    def _form_command(direction, distance, speed, angle="Straight"):
        return DIRECTION_SET[direction] + DISTANCE_SET[distance] + SPEED_SET[speed] + ANGLE_SET[angle]

    @staticmethod
    def _parse_sensor_data(msg: str):
        pass

    def _handle_end_of_step_msg(self, msg: str):
        # TODO:
        #  1. parse sensor data
        #  2. get distance to the obstacle / see if obstacle at the side
        #  3. (optional at stage 3) ask cv module to take pic, see if bulls eyes
        #  4. call _plan_and_act
        # Step 1 & 2
        distance_to_front, self.has_thing_at_left, self.has_thing_at_right = self._parse_sensor_data(msg)
        self.current_distance_to_front = distance_to_front
        if self.stage in [0, 1]:
            self.current_distance_to_obstacle = distance_to_front
        elif self.stage in [3, 7]:
            self.current_distance_to_left_side_wall = distance_to_front
        elif self.stage == 5:
            self.current_distance_to_right_side_wall = distance_to_front
        elif self.stage == 8:
            self.current_distance_to_garage = distance_to_front

        if self.stage == 0:
            # first impression abt the environment
            self.obstacle_distance = distance_to_front + 1
            # 1 is hardcoded as there is a blind instruction of moving forward 1 com

        # Step 3
        if self.stage in [0, 1]:
            # id, distance, angle = detectbullseye()
            # if angle is small, means right in front of the car, flip the strategy
            pass

        # Step 4
        self._act()

    def _get_biggest_smaller_dist(self, target):
        for c in self.candidate_distance_list[::-1]:
            if c <= target:
                return c

    def _act(self, msg: str = None):
        # TODO: based on the current stage and status, choose action
        cmd = None
        if self.stage == 0:
            if self.current_distance_to_front is None:
                # never moves
                # slowly move 1 cm forward
                # return
                cmd = self._form_command("f", 5, "SlowSpeed")
            if abs(self.current_distance_to_front - 200) > 15:
                # moved but the obstacle is not in front of the car
                # move back and force?
                logging.critical("Didn't find obstacle in front!")
                exit(-1)
        if self.stage in [0, 1]:
            if abs(self.current_distance_to_obstacle - 75) < 5:  # already can make the turn
                self.stage = 3
                # make left turn
                cmd = self.left_turn_command
            else:
                self.stage = 1
                buffer_dist = self.current_distance_to_obstacle - 75
                dist = self._get_biggest_smaller_dist(buffer_dist)
                # determine speed based on dist
                # form command
                cmd = self._form_command("f", dist, "HighSpeed")
        elif self.stage == 2:
            # if self.current_distance_to_left_side_wall < 55:
            #     # reverse slowly by 5
            #     pass
            # if abs(self.current_distance_to_left_side_wall - 55) < 5:
            #     self.stage = 4
            #     # make 90 right turn
            #     pass
            if self.has_thing_at_right is None:
                self.found_the_obs_at_side = self.has_thing_at_right
            if self.has_thing_at_right != self.found_the_obs_at_side:
                self.stage = 3
                # (originally no, now just found the edge), or (originally yes, after driving forward, now no)
                # anyways it's now at the edge
                # reverse 10 cm to make the turn
                cmd = self._form_command("b", 10, "MediumSpeed")
            else:
                if self.has_thing_at_right is True:
                    # move slowly forward 5 cm
                    self.horizontal_shift -= 5
                    cmd = self._form_command("f", 5, "SlowSpeed")
                    pass
                else:
                    # move slowly backward 5 cm
                    self.horizontal_shift += 5
                    cmd = self._form_command("b", 5, "SlowSpeed")
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
            cmd = self._form_command("f", 30, "HighSpeed")
        elif self.stage == 6:
            self.stage = 7
            # make right turn
            cmd = self.right_turn_command
        elif self.stage == 7:
            if abs(self.current_distance_to_front - (self.obstacle_distance + 50)) < 2:  # garage right in front
                self.stage = 10
                self.current_distance_to_garage = self.current_distance_to_front
                # stage 10 logic
                movable_dist = self.current_distance_to_garage - 20  # car's length / 2 with buffer
                dist = self._get_biggest_smaller_dist(movable_dist)
                # fast forward + biggest movable_dist
                cmd = self._form_command("f", dist, "HighSpeed")
            else:
                self.stage = 8
                # make 90 right turn
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
            y = -67.5 - self.horizontal_shift + self.moved
            if abs(y) < 5:
                self.stage = 10
                cmd = self.left_turn_command
            else:
                movable_dist = self._get_biggest_smaller_dist(abs(y))
                if y < 0:
                    # mid move fwd movable_dist
                    self.moved -= movable_dist
                    cmd = self._form_command("f", movable_dist, "MediumSpeed")
                else:
                    # mid move back movable_dist
                    self.moved += movable_dist
                    cmd = self._form_command("b", movable_dist, "MediumSpeed")
        # elif self.stage == 9:
        #     self.stage = 10
        #     # make left turn
        #     cmd = self.left_turn_command
        elif self.stage == 10:
            movable_dist = self.current_distance_to_garage - 20  # car's length / 2 with buffer
            if movable_dist < 5:
                self.stage = 11
                self.terminated = True
                return  # end of task
            dist = self._get_biggest_smaller_dist(movable_dist)
            # fast forward + biggest movable_dist
            cmd = self._form_command("f", dist, "HighSpeed")

        self.write(message="I" + cmd)


if __name__ == '__main__':
    Server().listen()
