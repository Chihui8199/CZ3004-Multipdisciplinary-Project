import logging
import math
import socket
import time
from typing import Union
from image_rec.img_rec import detectbullseye


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

        self.horizontal_distance_to_cover = 0.

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
            id, distance, angle = detectbullseye()
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
        cmd = ""
        if self.stage == 0:
            if self.current_distance_to_front is None:
                # never moves
                # slowly move 1 cm forward
                # return
                pass
            if abs(self.current_distance_to_front - 200) > 15:
                # moved but the obstacle is not in front of the car
                # move back and force?
                logging.critical("Didn't find obstacle in front!")
                pass
        if self.stage in [0, 1]:
            if abs(self.current_distance_to_obstacle - 75) < 5:  # already can make the turn
                self.stage = 3
                # make left turn
            else:
                self.stage = 1
                buffer_dist = self.current_distance_to_obstacle - 75
                dist = self._get_biggest_smaller_dist(buffer_dist)
                # determine speed based on dist
                # form command
        elif self.stage == 2:
            if self.current_distance_to_left_side_wall < 55:
                # reverse slowly by 5
                pass
            if abs(self.current_distance_to_left_side_wall - 55) < 5:
                self.stage = 4
                # make 90 right turn
                pass
            if not self.has_thing_at_right:
                self.stage = 3
                # reverse 10 cm to make the turn
                pass
            else:
                # move slowly forward 5 cm
                pass
        elif self.stage == 3:
            self.stage = 4
            # make 90 degree right turn
        elif self.stage == 4:
            self.stage = 5
            # make 90 right turn
        elif self.stage == 5:
            # calculate the distance to the ideal turning position
            # fast move towards it
            self.stage = 6
        elif self.stage == 6:
            self.stage = 7
            # make right turn
        elif self.stage == 7:
            if abs(self.current_distance_to_front - (self.obstacle_distance + 50)) < 2: # garage right in front
                self.stage = 10
                self.current_distance_to_garage = self.current_distance_to_front
                # stage 10 logic
                movable_dist = self.current_distance_to_garage - 20  # car's length / 2 with buffer
                dist = self._get_biggest_smaller_dist(movable_dist)
                # fast forward + biggest movable_dist
            else:
                self.stage = 8
                # make 90 right turn
        elif self.stage == 8:
            # calculate the distance to move based on previously moved distance
            # if distance = 0, reached, then to stage 9
            # else move slowly forward  # not gonna be far
            pass
        elif self.stage == 9:
            self.stage = 10
            # make left turn
        elif self.stage == 10:
            movable_dist = self.current_distance_to_garage - 20  # car's length / 2 with buffer
            if movable_dist < 5:
                self.stage = 11
                self.terminated = True
                return  # end of task
            dist = self._get_biggest_smaller_dist(movable_dist)
            # fast forward + biggest movable_dist

        self.write(message="I" + cmd)


if __name__ == '__main__':
    Server().listen()
