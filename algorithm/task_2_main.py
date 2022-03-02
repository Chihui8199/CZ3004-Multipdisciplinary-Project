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
    "5cm": "",
    "10cm": "",
    "20cm": "",
    "30cm": "",
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
        self.obstacle_size = None
        self.obstacle_distance = None
        self.left_side_wall_distance = None
        self.right_side_wall_distance = None

        # current status
        self.current_distance_to_garage = None
        self.current_distance_to_obstacle = None
        self.current_distance_to_left_side_wall = None
        self.current_distance_to_right_side_wall = None
        self.has_thing_at_left = None
        self.has_thing_at_right = None

        """
        stages:
        0: no sensor data received; obstacle distance, size unknown;
        1: obstacle distance located, otw to it
        3: adjusting position, parallel to the obstacle, to make right turn and pass obstacle
        4: half way passing the obstacle, need another 90 degree right turn to go to the back of obs
        5: at the back of the obstacle, heading to the position for another right turn
        6: half way passing the obstacle, need another 90 degree right turn to return from the back of obs
        7: adjusting position, parallel to the obstacle, to make left turn to head to garage
        8: on the way to the garage
        9: stopped
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
        #  3. ask cv module to take pic, see if bulls eyes
        #  4. calculate / correct the size of obstacle
        #  5. call _plan_and_act
        # Step 1 & 2
        distance_to_front, self.has_thing_at_left, self.has_thing_at_right = self._parse_sensor_data(msg)
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
            self.obstacle_distance = distance_to_front + 5
            # 5 is hardcoded as there is a blind instruction of moving forward 5 com
        # TODO more parsing

        # Step 3 & 4
        object_distance, object_size = detectbullseye()
        if object_size != -1:
            if self.obstacle_size is not None:
                # TODO: handle multiple measurement
                pass
            else:
                self.obstacle_size = object_size
        if object_distance != -1:
            # TODO: handle distance different from ultrasonic sensor
            pass

        # Step 5
        self._act()

    def _act(self, msg: str = None):
        # TODO: based on the current stage and status, choose action
        #  e.g.
        #   if init, slow move 5 cm forward to get sensor data
        #   if still quite far from the obstacle, move faster 20/30 cm
        #   if closer and about to take turn, move with medium speed and shorter distance
        #   if closer enough to the obs, turn; if too close then reverse a bit
        #   if
        if self.stage == 0:
            pass
        elif self.stage == 1:
            pass
        elif self.stage == 2:
            pass
        elif self.stage == 3:
            pass
        # TODO: more to be done


if __name__ == '__main__':
    Server().listen()
