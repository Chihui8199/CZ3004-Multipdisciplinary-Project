from typing import List

import torch

from envs.models import Entity


class Car(Entity):
    """
    Represents the robot car
    """

    def __init__(self, rectification_model: torch.nn.Module = None,
                 x: float = 15, y: float = 15,
                 length: float = 21, width: float = 22):  # TODO: the exact default values need to be confirmed
        """
        :param rectification_model: model used to rectify the position of the car after moving
        """
        super(Car, self).__init__(x, y, length, width)
        self.rectification_model = rectification_model

    def get_traj(self, action) -> List[Entity]:
        """
        simulate the traj as if no obstacles, no boundaries
        TODO: not yet sure how/what to record, essentially we need this to do the collision detection
        the simplest way is to return a list of sampled positions (as entities)
        """
        pass

    def set(self, x, y, z):
        """
        set the new position of the car (as if pick up the car and put it down directly)
        :param x:
        :param y:
        :param z:
        :return:
        """
        self.x = x
        self.y = y
        self.z = z
