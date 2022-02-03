import logging
from typing import List

import gym

from envs.models import *


class ImageRecognitionEnv(gym.Env):
    """
    This is the env for the autonomous image recognition task
    """

    def __init__(self, width: float = 200, length: float = 200):
        """
        create the env
        :param width: width of the map in cm, default to be 200
        :param length: length of the map in cm, default to be 200
        """
        self.width = width
        self.length = length
        self.walls = []
        # TODO: there should be better way to store obstacles other than keeping a list
        self.obstacles = []
        self.car = None
        self._add_walls()

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
        collision = self._check_collision([obstacle],
                                          include_current_car=True)
        if collision:
            logging.warning(f"attempting to add an collided obstacle! {kwargs}")
            return -1
        idx = len(self.obstacles)
        self.obstacles.append(obstacle)
        return idx

    def set_car(self, **kwargs):
        self.car = Car(**kwargs)

    def _check_collision(self, traj: List[Entity], include_current_car: bool = False):
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
        # the obs is firstly about the position of the car, [0:3]
        obs = [pos.get_positioning_status()]

        # later is the points to go for
        for obstacle in self.obstacles:
            obs += obstacle.get_points_to_visit()

        # TODO: may add more
        return obs

    def _get_car_pos_from_obs(self, obs) -> Entity:
        """
        This is for the step function, to extract the car pos from the observation
        (if the obs is more than just the car pos)
        :param obs:
        :return:
        """
        return Entity(x=obs[0][0], y=obs[0][1], z=obs[0][2], length=self.car.length, width=self.car.width)

    def step(self, action):
        """
        if we shall use it as a simulator, so the env must can trail and error
        so instead of directly step, we can have a try_step function
        :param action: the action you wish to execute;
        [0]: velocity, negative for move backwards; [1]: angle; [2]: time to move
        :return: obs: position status of the car
        done: false if the action is feasible
        cost: the length of the path
        """
        traj, cost = self.car.get_traj(action)
        collision = self._check_collision(traj)
        if collision:
            return None, float('inf'), True, None  # obs, cost, done, additional info (None for now)
        else:
            obs = self._get_obs_from_car_pos(traj[-1])
            return obs, cost, False, None

    def update(self, rectified_car_pos: Car):
        """
        update the status of the env by putting the car in position
        :param rectified_car_pos:
        :return:
        """
        # TODO: below is just a scratch, representing the general workflow
        if self._check_collision([rectified_car_pos]):
            # ideally this should not happen, but we need to handle it
            # TODO: in case the position is really not valid, we should have a fallback strategy
            raise ValueError(f"invalid car position! x: {rectified_car_pos.get_positioning_status()};\n ")
        self.car.set(rectified_car_pos.x, rectified_car_pos.y, rectified_car_pos.z)

    def get_current_obs(self):
        return self._get_obs_from_car_pos(self.car)

    def recognize(self, vision_x: int, sign: Sign):
        """
        this is to be used when the car recognized something (bull eye / float)
        ideally this should only be called after stepping
        :param vision_x: the x position of the recognized sign in the image, ranging from [0, 600]
        :param sign:
        :return: True if all tasks are completed TODO: to be discussed
        """
        # TODO: not yet sure of how to represent this, this part need to partner with the vision team (ds not confirmed)
        # we need to confirm which exact surface of which obstacle is it recognizing
        pass

    def reset(self):
        """
        clear the board and reset the car position
        :return:
        """
        return self._get_obs_from_car_pos(self.car)

    def render(self, mode="human"):
        """
        display (optional)
        :param mode:
        :return:
        """
        pass
