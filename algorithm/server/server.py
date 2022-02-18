import logging
import socket
import time
from typing import Union

from envs import make_env
from server import *


# noinspection PyBroadException
class Server:
    def __init__(self):
        self.host = ''
        self.port = HOST_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._connect()

        self.env = make_env("RobotMove-v0")
        # TODO: include
        #  1. controllers
        #  2. graph builders
        #  3. cv module

        self.incoming_msg_handlers = {
            "T": self._handle_add_obstacles_msg,
            "Y": self._handle_end_of_step_msg,
            "D": self._handle_end_msg
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

    def _handle_add_obstacles_msg(self, msg: str):
        # TODO:
        #  1. parse the message based on the format
        #  2. set obstacle in env
        #  3. start generating graph
        #   (IN ANOTHER THEAD!!! OTHERWISE WILL MISS THE OTHER INCOMING MESSAGE!)

        # now is just a test stub
        parsed_message = [[100, 100, 2], [40, 80, 0]]
        for obs in parsed_message:
            self.env.add_obstacle(x=obs[0], y=obs[1], target_face_id=obs[2])
        # TODO: start generating graph

    def _handle_end_of_step_msg(self, msg: str):
        # TODO:
        #  1. parse sensor data
        #  2. record env sensor data
        #  3. ask cv module to take pic (recognize)
        #  4. rectify position
        #  5. send obs to android (RPI)
        #  6. clear env sensor data
        #  7. plan path
        #  8. send action to robot (RPI)
        pass

    def _handle_end_msg(self, msg: str):
        assert msg is None, "Eng message should not contain any body"
        self.socket.close()
        self.terminated = True


if __name__ == '__main__':
    Server().listen()
