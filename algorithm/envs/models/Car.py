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
                 length: float = 25, width: float = 25):  # TODO: the exact default values need to be confirmed
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
        # print(action)
        action, dir = action[:-1], action[-1]

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
                new_z = (-v * time / radius + z) % (2 * math.pi)
                traj = Entity(
                    x=new_x,
                    y=new_y,
                    z=new_z,
                    length=self.length,
                    width=self.width
                )
                if noise:
                    traj.add_noise()
                traj_list.append(traj)

            sample_rate = 5 / samples
            for i in range(samples+1):
                if i == samples:
                    time = i * sample_rate
                    traj = Entity(
                        x=new_x + round(1 * time * math.cos(new_z)),
                        y=new_y + round(1 * time * math.sin(new_z)),
                        z=new_z,
                        length=self.length,
                        width=self.width
                    )
                else:
                    time = i * sample_rate
                    traj = Entity(
                        x=new_x + (1 * time * math.cos(new_z)),
                        y=new_y + (1 * time * math.sin(new_z)),
                        z=new_z,
                        length=self.length,
                        width=self.width
                    )
                if noise:
                    traj.add_noise()
                traj_list.append(traj)
            # hardcode for the final position
            dir = round(dir / (math.pi / 2))
            if dir == 0: # E
                if action[0] > 0: # forward
                    if action[1] < 0: # right
                        entity = Entity(
                            x=x+30,
                            y=y-45,
                            z=math.pi * 3 / 2,
                            length=self.length,
                            width=self.width
                        )
                    else:
                        entity = Entity(
                            x=x + 30,
                            y=y + 45,
                            z=math.pi / 2,
                            length=self.length,
                            width=self.width
                        )
                else:
                    if action[1] < 0:
                        entity = Entity(
                            x=x-50,
                            y=y-35,
                            z=math.pi / 2,
                            length=self.length,
                            width=self.width
                        )
                    else:
                        entity = Entity(
                            x=x-50,
                            y=y+35,
                            z=math.pi * 3 / 2,
                            length=self.length,
                            width=self.width
                        )
            elif dir == 1: # N
                if action[0] > 0:
                    if action[1] < 0:
                        entity = Entity(
                            x=x+45,
                            y=y+30,
                            z=0,
                            length=self.length,
                            width=self.width
                        )
                    else:
                        entity = Entity(
                            x=x-45,
                            y=y+30,
                            z=math.pi,
                            length=self.length,
                            width=self.width
                        )
                else:
                    if action[1] < 0:
                        entity = Entity(
                            x=x+35,
                            y=y-50,
                            z=math.pi,
                            length=self.length,
                            width=self.width
                        )
                    else:
                        entity = Entity(
                            x=x-35,
                            y=y-50,
                            z=0,
                            length=self.length,
                            width=self.width
                        )
            elif dir == 2: # W
                if action[0] > 0:
                    if action[1] < 0:
                        entity = Entity(
                            x=x-30,
                            y=y+45,
                            z=math.pi/2,
                            length=self.length,
                            width=self.width
                        )
                    else:
                        entity = Entity(
                            x=x-30,
                            y=y-45,
                            z=math.pi * 3 / 2,
                            length=self.length,
                            width=self.width
                        )
                else:
                    if action[1] < 0:
                        entity = Entity(
                            x=x+50,
                            y=y+35,
                            z=math.pi * 3 / 2,
                            length=self.length,
                            width=self.width
                        )
                    else:
                        entity = Entity(
                            x=x+50,
                            y=y-35,
                            z=math.pi / 2,
                            length=self.length,
                            width=self.width
                        )
            elif dir == 3: # S
                if action[0] > 0:
                    if action[1] < 0:
                        entity = Entity(
                            x=x-45,
                            y=y-30,
                            z=math.pi,
                            length=self.length,
                            width=self.width
                        )
                    else:
                        entity = Entity(
                            x=x+45,
                            y=y-30,
                            z=0,
                            length=self.length,
                            width=self.width
                        )
                else:
                    if action[1] < 0:
                        entity = Entity(
                            x=x-35,
                            y=y+50,
                            z=0,
                            length=self.length,
                            width=self.width
                        )
                    else:
                        entity = Entity(
                            x=x+35,
                            y=y+50,
                            z=math.pi,
                            length=self.length,
                            width=self.width
                        )
            traj_list.append(entity)

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
