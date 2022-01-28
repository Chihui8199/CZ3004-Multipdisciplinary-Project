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
        self.walls.append(Entity(-1, self.length / 2, self.length, 2))
        self.walls.append(Entity(self.width + 1, self.length / 2, self.length, 2))
        self.walls.append(Entity(self.width / 2, -1, 2, self.width + 4))
        self.walls.append(Entity(self.width / 2, self.length + 1, 2, self.width + 4))

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

    def _get_obs_from_car_pos(self, pos):
        """
        This is a helper function, pos doesn't need to be the exact car position
        :param pos:
        :return:
        """
        pass

    def _get_car_pos_from_obs(self, obs) -> Entity:
        """
        This is for the step function, to extract the car pos from the observation
        (if the obs is more than just the car pos)
        :param obs:
        :return:
        """
        pass

    def try_step(self, action):
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
            cost = float('inf')
            pass  # TODO: do something
        else:
            pass

    def step(self, obs):
        """
        update the status of the env by putting the car in position
        :param obs: result[0] from try_step
        :return: None; if not feasible, an exception will be thrown
        """
        # TODO: below is just a scratch, representing the general workflow
        final_pos = self._get_car_pos_from_obs(obs)
        if self._check_collision([final_pos]):
            # ideally this should not happen
            raise ValueError(f"invalid car position! Observation: {obs};\n "
                             f"you should run try_step() first, and do not call step() if done=True")
        self.car.set(final_pos.x, final_pos.y, final_pos.z)
        # TODO: may have more to be done

    def recognize(self, ):
        """
        this is to be used when the car recognized something (bull eye / float)
        ideally this should only be called after stepping
        :return: True if all tasks are completed TODO: to be discussed
        """
        # TODO: not yet sure of how to represent this, this part need to partner with the vision team (ds not confirmed)
        pass

    def reset(self):
        """
        clear the board and reset the car position
        :return:
        """
        pass

    def render(self, mode="human"):
        """
        display (optional)
        :param mode:
        :return:
        """
        pass
