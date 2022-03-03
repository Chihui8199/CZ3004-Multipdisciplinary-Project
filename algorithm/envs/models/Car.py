import math
from typing import List, Tuple

import torch
import numpy as np

from envs.models import Entity, Direction


class Car(Entity):
    """
    Represents the robot car
    """
    # TODO: these bounds are just placeholders, the numbers/units are unclear
    # VELOCITY_LB = -2
    # VELOCITY_UP = 2
    # ANGLE_LB = -0.73
    # ANGLE_UB = 0.73
    # TIME_LB = 0.5
    # TIME_UP = 2

    TURNING_RADIUS = 40     # multiple of 5

    def __init__(self, rectification_model: torch.nn.Module = None,
                 x: float = 15, y: float = 15,
                 z: float = Direction.NORTH.value,
                 length: float = 19, width: float = 19):  # TODO: the exact default values need to be confirmed
        """
        :param rectification_model: model used to rectify the position of the car after moving
        """
        super().__init__(x=x, y=y, z=z, length=length, width=width)
        self.length = length
        self.width = width
        self.rectification_model = rectification_model

    def get_traj(self, x, y, z, action, sample_rate: float = 0.1, noise: bool = False) -> Tuple[List[Entity], float]:
        """
        simulate the traj as if no obstacles, no boundaries; and calculate length of the traj
        TODO: not yet sure how/what to record, essentially we need this to do the collision detection
        the simplest way is to return a list of sampled positions (as entities)
        """
        # traj is a array of car positions, cost is the length of the path
        v, angle, t = action[0], action[1], action[2]
        # traj should be divided into samples with a sample rate # TODO: default value to be confirmed
        traj_list = []
        samples = max(1, math.floor(t / sample_rate))  # if time too short, consider it as 1 sample
        sample_rate = t / samples
        cost = abs(v) * t

        # whether car rotating
        if math.fabs(angle) < pow(10, -3):
            # no rotation
            for i in range(samples+1):
                if i == samples:
                    time = i * sample_rate
                    traj = Entity(
                        x=x + round(v * time * math.cos(z)),
                        y=y + round(v * time * math.sin(z)),
                        z=z,
                        length=self.length,
                        width=self.width
                    )
                else:
                    time = i * sample_rate
                    traj = Entity(
                        x=x + (v * time * math.cos(z)),
                        y=y + (v * time * math.sin(z)),
                        z=z,
                        length=self.length,
                        width=self.width
                    )
                if noise:
                    traj.add_noise()
                traj_list.append(traj)
        else:
            # hardcode
            if angle > 0:
                radius = -Car.TURNING_RADIUS
            else:
                radius = Car.TURNING_RADIUS

            for i in range(samples + 1):
                time = i * sample_rate
                if i == samples:
                    new_x = round(x - radius * math.cos(z + math.pi / 2) + radius * math.cos(
                        -v * time / radius + z + math.pi / 2))
                    new_y = round(y - radius * math.sin(z + math.pi / 2) + radius * math.sin(
                        -v * time / radius + z + math.pi / 2))
                else:
                    new_x = x - radius * math.cos(z + math.pi / 2) + radius * math.cos(
                        -v * time / radius + z + math.pi / 2)
                    new_y = y - radius * math.sin(z + math.pi / 2) + radius * math.sin(
                        -v * time / radius + z + math.pi / 2)
                traj = Entity(
                    x=new_x,
                    y=new_y,
                    z=(-v * time / radius + z),
                    length=self.length,
                    width=self.width
                )
                if noise:
                    traj.add_noise()
                traj_list.append(traj)

        return traj_list, cost

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
