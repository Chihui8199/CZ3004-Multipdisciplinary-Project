import math
from typing import List, Tuple

import torch

from envs.models import Entity, Direction


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
    TIME_UP = 3

    def __init__(self, rectification_model: torch.nn.Module = None,
                 x: float = 15, y: float = 15,
                 z: float = Direction.NORTH.value,
                 length: float = 21, width: float = 22):  # TODO: the exact default values need to be confirmed
        """
        :param rectification_model: model used to rectify the position of the car after moving
        """
        super().__init__(x=x, y=y, z=z, length=length, width=width)
        self.length = length
        self.width = width
        self.rectification_model = rectification_model

    def get_traj(self, action, sample_rate: float = 0.01) -> Tuple[List[Entity], float]:
        """
        simulate the traj as if no obstacles, no boundaries; and calculate length of the traj
        TODO: not yet sure how/what to record, essentially we need this to do the collision detection
        the simplest way is to return a list of sampled positions (as entities)
        """
        # traj is a array of car positions, cost is the length of the path
        v, angle, t = action[0], action[1], action[2]
        # traj should be divided into samples with a sample rate # TODO: default value to be confirmed
        traj_list = []
        samples = math.floor(t / sample_rate)  # TODO: confirm if to round up or down
        if samples == 0:  # time too short, consider it as 1 sample
            samples = 1
            sample_rate = t
        cost = abs(v) * t

        # whether car rotating
        if math.fabs(angle) < pow(10, -3):
            # no rotation
            for i in range(samples):
                time = i * sample_rate
                traj = Entity(
                    x=self.x + v * time * math.cos(math.pi/2+self.z),
                    y=self.y + v * time * math.sin(math.pi/2+self.z),
                    z=self.z,
                    length=self.length,
                    width=self.width
                )
                traj_list.append(traj)
        else:
            radius = self.length / (2 * math.sin(angle))
            for i in range(samples):
                time = i * sample_rate
                x = self.x - radius * math.cos(angle) + radius * math.cos(v * time / radius + angle)
                y = self.y - radius * math.sin(angle) + radius * math.sin(v * time / radius + angle)
                traj = Entity(
                    x=x,
                    y=y,
                    z=math.atan2(math.sin(v * time / radius + angle), math.cos(v * time / radius + angle)),
                    length=self.length,
                    width=self.width
                )
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
