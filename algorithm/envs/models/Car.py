import math
from typing import List, Tuple

import torch

from envs.models import Entity


class Car(Entity):
    """
    Represents the robot car
    """
    # TODO: these bounds are just placeholders, the numbers/units are unclear
    VELOCITY_LB = -10
    VELOCITY_UP = 10
    ANGLE_LB = - math.pi / 2
    ANGLE_UB = math.pi / 2
    TIME_LB = 0
    TIME_UP = 10

    def __init__(self, rectification_model: torch.nn.Module = None,
                 x: float = 15, y: float = 15,
                 length: float = 21, width: float = 22):  # TODO: the exact default values need to be confirmed
        """
        :param rectification_model: model used to rectify the position of the car after moving
        """
        super().__init__(x=x, y=y, length=length, width=width)
        self.rectification_model = rectification_model

    def get_traj(self, action) -> Tuple[List[Entity], float]:
        """
        simulate the traj as if no obstacles, no boundaries; and calculate length of the traj
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
