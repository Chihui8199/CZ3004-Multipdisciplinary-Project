import logging
import math
import socket
import time
from multiprocessing.dummy import Process
from typing import Union
from image_rec.img_rec import conf_level, detect, stitch_save
from image_rec.img_rec import stitch


from controllers import MainController
from envs import make_env
from envs.models import Car, Obstacle, Sign
from graph import GraphBuilder
from helpers import ShortestHamiltonianPathFinder
from image_rec.img_rec import sync

RPI_IP = '192.168.16.16'
RPI_PORT = 8080
HOST_PORT = 8080
logging.getLogger().setLevel(logging.DEBUG)


# noinspection PyBroadException
class Server:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = HOST_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._connect()

        self.env = make_env("RobotMove-v0")
        self.env.set_car(x=15, y=15)
        self.controller = MainController()
        self.graph = None
        self.graph_building_thread = None
        self.target_points = None
        self.current_target_idx = None
        self.ideal_position = None
        self.obs_seq = None
        # TODO: include
        #  1. controllers
        #  2. graph builders
        #  3. cv module
        self.detection = None
        self.sync = sync()
        self.conf_level = conf_level()
        self.sensor_data = None
        self.detect_array = [0]*45

        self.incoming_msg_handlers = {
            "F": self._plan_and_act,
            "T": self._handle_add_obstacles_msg,
            "Y": self._handle_end_of_step_msg,
            "D": self._handle_end_msg,
            "US": self._handle_arrive_obstacles_msg
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
            self.target_points = ShortestHamiltonianPathFinder.get_visit_sequence(self.env)[0][1:]
            self.obs_seq = ShortestHamiltonianPathFinder.get_visit_sequence(self.env)[1]
            self.current_target_idx = 0
            # self.graph = GraphBuilder(self.env.reset(), self.env)
            # self.graph.createGraph()
            file_path = './graph_server_test.pickle'

            import os
            import pickle

            # os.path.exists(file_path)
            # graph = None

            overwrite = False

            try:
                if os.path.exists(file_path) and not overwrite:
                    with open(file_path, 'rb') as f:
                        self.graph = pickle.load(f)
                    self.env.reset()
                else:
                    with open(file_path, 'wb') as f:
                        self.graph = GraphBuilder(self.env.reset(), self.env)
                        self.graph.createGraph()
                        pickle.dump(self.graph, f)
            except:
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
        # object_name, object_id, dist, angle = detect()
        # if object_id != 0:
        #     stitch()
        #     exit(0)

        self.write('P' + str(self.env.get_current_obs()))   # send the observation
        self.env.clear_sensor_data()
        self.env.update(rectified_car_pos=Car(x=self.ideal_position[0][0], y=self.ideal_position[0][1],
                                              z=self.ideal_position[0][2]))
        self._plan_and_act(None)

    def _plan_and_act(self, msg: str):
        thread = self.sync.start_async(self.conf_level)
        if self.graph_building_thread is not None:
            self.graph_building_thread.join()
            self.graph_building_thread = None
        while True:
            action = self.controller.act(observation=self.env.get_current_obs(),
                                         env=self.env,
                                         target=self.target_points[self.current_target_idx],
                                         graph=self.graph)
            
            if action is None:
                # handle error, to confirm usage
                self.sync.stop_async(thread=thread)
                # call detect in algo
                self.sync.detect_sem.acquire()
                id, id_num, dist, angle,conf = detect(self.conf_level)  # distance got ±3cm diff
                stitch_save()
                if(id_num != 0 and id_num!=-1):
                    self.detect_array[id_num] = 1
                if(id_num ==0 or id_num == -1):
                    if(self.sync.id_prev != 0 and self.sync.id_prev!= -1 and self.detect_array[self.sync.id_prev]==0):
                        id_num = self.sync.id_prev
                        self.detect_array[id_num] = 1
                self.sync.detect_sem.release()
                self.env.obstacles[self.obs_seq[self.current_target_idx]]\
                    .recognize_face(self.target_points[self.current_target_idx][-1], Sign(id_num))
                self.write('P' + str(self.env.get_current_obs()))
                # if id != 0:
                #     stitch()
                #     exit(0)
                # fetch sensor data from rpi
                # ultra_msg = 'u' + '00000000000'
                # self.write(ultra_msg)

                # while self.sensor_data is None:
                #     pass

                # picture_dist = dist + Obstacle.OBS_LEN // 2
                # ultra_dist = self.sensor_data

                # compare with camera dist and ultrasonic sensor distance
                # if the difference is too big, then we choose the picture taken distance instead of ultra_dist

                # diff = dist - Obstacle.BEST_VIEW_DISTANCE
                #
                # if diff > 0:
                #     # msg move forward
                #     msg += 'f00220350149'
                #     self.write("I" + msg)
                #     pass
                # else:
                #     # msg move backward
                #     msg += 'b00220350149'
                #     self.write("I" + msg)
                #     pass


                self.current_target_idx += 1
                if self.current_target_idx == len(self.target_points):
                    stitch()
                    print("done")
                    exit(0)

                self.sensor_data = None # reset sensor data
                continue
            action_ = action[:]
            action_.append(self.env.get_current_obs()[0][-1])
            self.ideal_position, _, _, _ = self.env.step(action_)


            # FIXME: [0] cuz at this moment its a series of actions, need to be changed after
            # instruction sent to robot team
            # forward 5cm: f01071000149
            # fr: f19501000215
            # fl: f13301000111
            # bl: b15201000116
            # br: b21301000199
            # f1cm: f00220350149
            # outside
            fr, fl, bl, br = 'f19801000215', 'f12801000111', 'b15401000116', 'b22001000199'
            f5, b5, f1, b1 = 'f01071000149', 'b01071000149', 'f00220350149', 'b00220350149'
            # # # inside
            # fr, fl, bl, br = 'f20301000215', 'f13601000111', 'b15301000116', 'b22001000199'
            # f5, b5, f1, b1 = 'f01071000149', 'b01071000149', 'f00220350149', 'b00220350149'
            # if action[0] > 0:
            #     if action[1] < 0:
            #         msg_set = [f1, fr, b1]
            #     elif action[1] == 0:
            #         msg_set = [f5]
            #     else:
            #         msg_set = [f1, fl]
            # else:
            #     if action[1] < 0:
            #         msg_set = [f1, br, b1, b1]
            #     elif action[1] == 0:
            #         msg_set = [b5]
            #     else:
            #         msg_set = [bl, b1, b1]
            if action[0] > 0:
                if action[1] < 0:
                    msg_set = [fr]
                elif action[1] == 0:
                    msg_set = [f5]
                else:
                    msg_set = [fl]
            else:
                if action[1] < 0:
                    msg_set = [br]
                elif action[1] == 0:
                    msg_set = [b5]
                else:
                    msg_set = [bl]

            if len(msg_set) == 1:
                self.write("I" + msg_set[0])
            else:
                for msg in msg_set:
                    self.write("I" + msg)
                    time.sleep(1)
            break

    def _handle_end_msg(self, msg: str):
        assert msg is None, "Eng message should not contain any body"
        self.socket.close()
        self.terminated = True

    def _handle_arrive_obstacles_msg(self, msg: str):
        # with self.socket as s:
        #     s.bind((self.host, self.port))
        #     s.listen()
        #     conn, addr = s.accept()
        #     data = conn.recv(2048)
        #
        #     data = data.decode('utf-8')
        #     self.sensor_data = eval(data)
        self.sensor_data = eval(msg)


if __name__ == '__main__':
    Server().listen()
