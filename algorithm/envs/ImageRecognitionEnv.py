import logging
import math
import random
from threading import Thread
import time
from collections import deque
from typing import List, Union, Tuple
from itertools import chain

import gym
import numpy as np

from envs.models import *


class ImageRecognitionEnv(gym.Env):
    """
    This is the env for the autonomous image recognition task
    """

    def __init__(self, mock: bool = False, rl_mode: bool = False, width: float = 200, length: float = 200):
        """
        create the env
        :param mock: when set to mock, random obstacles will be added, with noise added to the movement
        :param mock: true if is training using rl, the obs content will change
        :param width: width of the map in cm, default to be 200
        :param length: length of the map in cm, default to be 200
        """
        self.mock = mock
        self.rl_mode = rl_mode

        # below attributes only used in mock
        self.steps = 0
        self.points_to_visit = 0

        self.completed = False
        self.width = width
        self.length = length
        self.walls = []
        self.obstacles = []
        self.car = None
        self.sensor_data = deque([], maxlen=1000)  # the point is, not need to keep too much old data
        self._add_walls()
        self.path = None

        if self.rl_mode:
            self.action_space = gym.spaces.Box(low=np.array([-1.] * 3),  # TODO: norm not implemented yet
                                               high=np.array([1.] * 3),
                                               dtype=np.float32)
            self.observation_space = gym.spaces.Box(low=np.array([0.] * 38),
                                                    high=np.array([200.] * 38),
                                                    dtype=np.float32)

    def _add_walls(self):
            """
            something like this:

                        ===========
                        |         |
                        |         |
                        ===========
            """
            self.walls.append(Entity(x=-1, y=self.length / 2, length=self.length, width=2))
            self.walls.append(Entity(x=self.width + 1, y=self.length / 2, length=self.length, width=2))
            self.walls.append(Entity(x=self.width / 2, y=-1, length=2, width=self.width + 4))
            self.walls.append(Entity(x=self.width / 2, y=self.length + 1, length=2, width=self.width + 4))

    def add_obstacle(self, **kwargs) -> int:
        """
        create and maintain a new obstacle
        return the id, -1 for not successful
        """
        # TODO: check collision
        obstacle = Obstacle(**kwargs)

        # collision = self._check_collision([obstacle],
        #                                   include_current_car=True)
        collision = False

        if collision:
            logging.warning(f"attempting to add an collided obstacle! {kwargs}")
            return -1
        idx = len(self.obstacles)
        self.obstacles.append(obstacle)
        return idx

    def set_car(self, **kwargs):
        self.car = Car(**kwargs)

    def check_collision(self, traj: List[Entity], include_current_car: bool = False):
        """
        Check if the passed-in entity collide with any exisiting entity
        :param traj: list of entities to test collision
        :return: True if they do collide
        """
        for shadow in traj:  # meh, a bit ugly, can use map() later
            for wall in self.walls:
                if wall.collide_with(shadow):
                    return True
            for obstacle in self.obstacles:
                if obstacle.collide_with(shadow):
                    return True
            if include_current_car and self.car is not None:
                if self.car.collide_with(shadow):
                    return True
        return False

    def _get_obs_from_car_pos(self, pos: Entity):
        """
        This is a helper function, pos doesn't need to be the exact car position
        :param pos:
        :return:
        """
        # the obs is firstly about the position of the car
        obs = [pos.get_positioning_status()]

        # then is about the obstacle [is_explored, x, y, one-hot encoding of target surface]
        for obstacle in self.obstacles:
            obs.append([obstacle.surfaces[obstacle.target_surface_id].sign.value] +
                       [obstacle.x, obstacle.y] +
                       [1 if s.is_target else 0 for s in obstacle.surfaces])

        if self.rl_mode:
            # we need to flat the observation into 1d
            obs = list(chain.from_iterable(obs))

            # and there is no need for the agent to know the exact sign content
            for i in range(3, len(obs), 7):
                obs[i] = 0 if obs[i] == -1 else 1

        # TODO: may add more
        return obs

    def _get_car_pos_from_obs(self, obs) -> Car:
        """
        This is for the step function, to extract the car pos from the observation
        (if the obs is more than just the car pos)
        :param obs:
        :return:
        """
        if self.rl_mode:
            x = obs[0]
            y = obs[1]
            z = obs[2]
        else:
            x = obs[0][0]
            y = obs[0][1]
            z = obs[0][2]
        return Car(x=x, y=y, z=z, length=self.car.length, width=self.car.width)

    def _calculate_reward(self, obs, act, path_cost, ):
        path_factor = -1

        speed_factor = -5
        speed_cost = abs(act[0])

        time_factor = -1
        time_cost = 0  # the time of driving, TODO: disabled for now

        distances = []
        recog_distances = []
        recog_distances_discount_factor = 0.5
        distances_discount_factor = 0.5
        recognition_factor = 50.  # TODO: magic number
        points_to_visit = 0
        for obstacle in self.obstacles:
            if not obstacle.explored:  # the obstacle has not been finished yet
                points_to_visit += 1
                distances.append(self.car.get_euclidean_distance(obstacle))
            else:
                recog_distances.append(self.car.get_euclidean_distance(obstacle))
        recognition_reward = self.points_to_visit - points_to_visit
        self.points_to_visit = points_to_visit
        if recognition_reward != 0:
            # should add a verbose setting so that can disable the logging
            logging.info(f"new faces solved! {recognition_reward}")

        # stay close to the unexplored/unsolved obstacles
        distance_factor = -5e-2
        distance_cost = 0.
        sorted(distances)
        for d in distances:
            distance_cost += d * distances_discount_factor
            distances_discount_factor **= 2

        # stay away from the explored obstacles
        recog_distance_factor = 5e-2
        recog_distance_reward = 0.
        for d in recog_distances:
            recog_distance_reward += d * recog_distances_discount_factor
            recog_distances_discount_factor **= 2

        # TODO: investigating if we need this
        ep_len_factor = -1.
        ep_len_reward = 0 if self.steps == 0 else math.log(self.steps)

        reward = path_factor * path_cost + speed_factor * speed_cost + time_factor * time_cost + \
                 distance_factor * distance_cost + recog_distance_factor * recog_distance_reward + \
                 recognition_factor * recognition_reward + ep_len_factor * ep_len_reward

        # TODO: adhoc copy paste here, very ugly, will remove later (or refactor)
        logging.debug(f"reward: {reward} = {path_factor * path_cost} + "
                      f"{speed_factor * speed_cost} + {time_factor * time_cost} + "
                      f"{distance_factor * distance_cost} + {recog_distance_factor * recog_distance_reward} + "
                      f"{recognition_factor * recognition_reward} + { ep_len_factor * ep_len_reward}")

        return reward

    def _denorm_actions(self, normed_action):
        if not self.rl_mode:
            logging.warning("you are not supposed to used norm actions in non-rl env")
        return [
            (self.car.VELOCITY_UP - self.car.VELOCITY_LB) * ((normed_action[0] + 1) / 2) + self.car.VELOCITY_LB,
            (self.car.ANGLE_UB - self.car.ANGLE_LB) * ((normed_action[1] + 1) / 2) + self.car.ANGLE_LB,
            (self.car.TIME_UP - self.car.TIME_LB) * ((normed_action[2] + 1) / 2) + self.car.TIME_LB,
        ]

    def step(self, action: Union[List, Tuple]):
        """
        if we shall use it as a simulator, so the env must can trail and error
        so instead of directly step, we can have a try_step function
        :param action: the action you wish to execute;
        [0]: velocity, negative for move backwards; [1]: angle; [2]: time to move
        :return: obs: position status of the car
        done: false if the action is feasible
        cost: the length of the path
        """
        if self.rl_mode:
            action = self._denorm_actions(action)
        if self.mock:
            logging.debug(f"action: {action}")

        traj, path_cost = self.car.get_traj(self.car.x, self.car.y, self.car.z, action)
        for i, t in enumerate(traj):
            if i % 10 == 0:
                self.set_car(x=t.x, y=t.y, z=t.z)
                time.sleep(0.01)
        collision = self.check_collision(traj)
        if collision:
            return None, -100, True, True  # obs, reward, done, additional info (collision info for now)
        else:
            if self.mock:
                self.car.set(traj[-1].x, traj[-1].y, traj[-1].z)  # no need to set separately in mock
                self.steps += 1
                for o in self.obstacles:  # check if it has any chance of recognizing one obstacle
                    if o.explored:
                        continue
                    p = o.get_best_point_to_visit()
                    if ((p[0] - self.car.x) ** 2 + (p[1] - self.car.y) ** 2) ** 0.5 < 20. and \
                            min((2 * math.pi) - abs(p[2] - self.car.z), abs(p[2] - self.car.z)) < 0.5:
                        # means tha car is close enough to recognize
                        logging.info("the car has arrived at a proper position")
                        # mock target img sign as the specific value is not important
                        o.recognize_face(o.target_surface_id, Sign.ALPHA_A)
                obs = self.get_current_obs()
            else:
                obs = self._get_obs_from_car_pos(traj[-1])

            is_done = True
            for o in self.obstacles:
                is_done &= o.explored  # All explored

            if is_done:
                self.completed = True
                logging.info("successfully completed one ep with no collision!")

            return obs, self._calculate_reward(obs, action, path_cost), is_done, False

    def update(self, rectified_car_pos: Car):
        """
        update the status of the env by putting the car in position
        :param rectified_car_pos:
        :return:
        """
        # TODO: below is just a scratch, representing the general workflow
        if self.mock:
            logging.warning("you should not use update in a mock env")
        self.steps += 1
        # if self.check_collision([rectified_car_pos]):
        #     # ideally this should not happen, but we need to handle it
        #     # TODO: in case the position is really not valid, we should have a fallback strategy
        #     raise ValueError(f"invalid car position! x: {rectified_car_pos.get_positioning_status()};\n ")
        self.car.set(rectified_car_pos.x, rectified_car_pos.y, rectified_car_pos.z)

    def get_current_obs(self):
        return self._get_obs_from_car_pos(self.car)

    def clear_sensor_data(self):
        """
        remove outdated sensor data
        :return:
        """
        self.sensor_data.clear()

    def record_sensor_data(self, data):
        """
        Record sensor data, format to be confirmed with the robot team
        note that this api can be async called, any time, whenever received a sensor data
        :param data:
        :return:
        """
        self.sensor_data.append((time.time(), data))  # TODO: timestamp may not be needed, but I just leave it here for now

    def get_sensor_data(self):
        return list(self.sensor_data)

    def recognize(self, vision_x: int, sign: Sign):
        """
        this is to be used when the car recognized something (bull eye / float)
        this should be called async (i.e. upon detecting something), and once when the car stopped moving
        :param vision_x: the x position of the recognized sign in the image, ranging from [0, 600]
        :param sign:
        :return: None
        """
        # TODO: not yet sure of how to represent this, this part need to partner with the vision team (ds not confirmed)

        # For now:
        # for simplicity, we only consider one as recognized when it's right in front of the car:
        if vision_x <= 250 or vision_x >= 350:
            pass
        # identify which obstacle and surface is it recognizing
        # then call recognize_face(...) of that obstacle

        """
        Q: why is it so hard?
        A: 
        1. multiple signs seen, which is which? important for path planing
        2. important for rectify the position of the car as well!
        
        It may be the easiest by do experiments and measure by hand, rather than try to do it mathematically
        unless you do know the camera lens well, like how it bends (p.s. I know nothing abt it -- Xinyi)
        """

    def reset(self):
        """
        this is not really used as we don't really reset the car after moving
        :return:
        """
        if self.mock:
            logging.debug("env reset")
            # TODO: randomly place the car, so that it's not so easy to hit the wall at the begining
            self.set_car(x=random.uniform(30, self.width - 30), y=random.uniform(30, self.length - 30))
            self.obstacles = []
            for i in range(5):
                while self.add_obstacle(x=random.randint(30, int(self.width - 30)),
                                        y=random.randint(30, int(self.length - 30)),
                                        target_face_id=random.randint(0, 3),
                                        mock=True) == -1:
                    continue  # TODO: actually this may make the obstacles too close to each other
            self.steps = 0
            self.points_to_visit = 5
        self.completed = False
        return self._get_obs_from_car_pos(self.car)

    def render(self, mode="human"):
        """
        display (optional)
        :param mode:
        :return:
        """
        ui_thread = Thread(target=self._render)
        ui_thread.start()

    def _render(self):
        import os

        from matplotlib.animation import FuncAnimation
        import matplotlib.pyplot as plt
        import matplotlib as mpl
        from svgpathtools import svg2paths
        from svgpath2mpl import parse_path
        from res import RES_PATH

        def _update(*args):
            nonlocal car_marker
            obstacles_x = []
            obstacles_y = []
            points_x = []
            points_y = []
            for o in self.obstacles:
                point = o.get_best_point_to_visit()
                obstacles_x.append(o.x)
                obstacles_y.append(o.y)
                if len(point) > 0:
                    points_x.append(point[0])
                    points_y.append(point[1])
            obstacles.set_data(obstacles_x, obstacles_y)
            nodes.set_data(points_x, points_y)
            car, = ax.plot([self.car.x], [self.car.y],
                           marker=car_marker.transformed(mpl.transforms.Affine2D().rotate_deg(math.degrees(self.car.z - math.pi / 2))),
                           ls="", markersize=36, color='black')
            if self.path:
                path.set_data([i[0] for i in self.path], [i[1] for i in self.path])
            info.set_text("x: {:.2f} y: {:.2f} angle: {:.1f}".format(self.car.x, self.car.y, self.car.z),)

            return info, obstacles, nodes, car,

        fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
        # figure()
        ax.grid()

        ax.set_xlim(0, 200)
        ax.set_xticks(list(range(0, 201, 10)))
        ax.set_ylim(0, 200)
        ax.set_yticks(list(range(0, 201, 10)))

        car_path, attributes = svg2paths(os.path.join(RES_PATH, "car-top-view-svgrepo-com.svg"))
        car_marker = parse_path(attributes[0]['d'])
        car_marker.vertices -= car_marker.vertices.mean(axis=0)
        car_marker = car_marker.transformed(mpl.transforms.Affine2D().scale(1.5, 1).rotate_deg(180))

        info = ax.text(5, 5, "")
        path, = ax.plot([], [])
        obstacles, = ax.plot([], [], marker="s", ls="", markersize=18.5)
        nodes, = ax.plot([], [], marker="o", ls="")

        anim = FuncAnimation(fig, _update, interval=100, blit=True)
        fig.tight_layout()
        plt.show()
