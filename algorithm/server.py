import logging
import math
import socket
import time
from multiprocessing.dummy import Process
from typing import Union
from image_rec.img_rec import detect
from image_rec.img_rec import stitch


from controllers import MainController
from envs import make_env
from envs.models import Car
from graph import GraphBuilder
from helpers import ShortestHamiltonianPathFinder

RPI_IP = '192.168.16.16'
RPI_PORT = 8080
HOST_PORT = 8080
logging.getLogger().setLevel(logging.DEBUG)


# noinspection PyBroadException
class Server:
    def __init__(self):
        self.host = ''
        self.port = HOST_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._connect()

        self.env = make_env("RobotMove-v0")
        self.env.set_car(x=100, y=20)
        self.controller = MainController()
        self.graph = None
        self.graph_building_thread = None
        self.target_points = None
        self.current_target_idx = None
        self.ideal_position = None
        # TODO: include
        #  1. controllers
        #  2. graph builders
        #  3. cv module

        self.incoming_msg_handlers = {
            "F": self._plan_and_act,
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

    @staticmethod
    def _parse_2d_list(msg):
        return eval(msg.strip())  # well this is dangerous, but quite useful...

    def _handle_add_obstacles_msg(self, msg: str):
        def _generate_graph():
            self.target_points = ShortestHamiltonianPathFinder.get_visit_sequence(self.env)[1:]
            self.current_target_idx = 0
            # self.graph = GraphBuilder(self.env.reset(), self.env)
            # self.graph.createGraph()
            file_path = './graph_server_test.pickle'

            import os
            import pickle

            # os.path.exists(file_path)
            # graph = None

            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    self.graph = pickle.load(f)
                self.env.reset()
            else:
                with open(file_path, 'wb') as f:
                    self.graph = GraphBuilder(self.env.reset(), self.env)
                    self.graph.createGraph()
                    pickle.dump(self.graph, f)
            # self.graph.revert()
            print("<<<")

        print(">>>>>>>>")
        parsed_message = self._parse_2d_list(msg)
        for obs in parsed_message:
            self.env.add_obstacle(x=obs[0], y=obs[1], target_face_id=obs[2])
        self.graph_building_thread = Process(target=_generate_graph)
        self.graph_building_thread.start()

    def _handle_end_of_step_msg(self, msg: str):
        # TODO:
        #  1. parse sensor data
        #  2. record env sensor data
        #  3. ask cv module to take pic (recognize)
        #  4. rectify position and confirm if pass and what's the next point to visit
        #  5. send obs to android (RPI)
        #  6. clear env sensor data
        #  7. call _plan_and_act
        # TODO: now just use the ideal one
        object_name, object_id, dist, angle = detect()
        if object_id != 0:
            stitch()
            exit(0)

        self.env.update(rectified_car_pos=Car(x=self.ideal_position[0][0], y=self.ideal_position[0][1],
                                              z=self.ideal_position[0][2]))
        self._plan_and_act(None)

    def _plan_and_act(self, msg: str):
        if self.graph_building_thread is not None:
            self.graph_building_thread.join()
            self.graph_building_thread = None
        while True:
            action = self.controller.act(observation=self.env.get_current_obs(),
                                         env=self.env,
                                         target=self.target_points[self.current_target_idx],
                                         graph=self.graph)
            
            if action is None:
                self.current_target_idx += 1
                if self.current_target_idx == len(self.target_points):
                    print("done")
                    exit(0)
                continue
            self.ideal_position, _, _, _ = self.env.step(action)


            # FIXME: [0] cuz at this moment its a series of actions, need to be changed after
            msg = ''
            if action[0] > 0:
                msg += 'f0001000'
                if action[1] < 0:
                    msg += '210'
                elif action[1] == 0:
                    msg += '149'
                else:
                    msg += '109'
            else:
                msg += 'b0001000'
                if action[1] < 0:
                    msg += '200'
                elif action[1] == 0:
                    msg += '149'
                else:
                    msg += '114'

            self.write("I" + msg)
            break

    def _handle_end_msg(self, msg: str):
        assert msg is None, "Eng message should not contain any body"
        self.socket.close()
        self.terminated = True


if __name__ == '__main__':
    Server().listen()
