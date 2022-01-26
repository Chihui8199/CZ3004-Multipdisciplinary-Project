import random

from controllers.BaseController import BaseController
from envs.models import Car


class RandomController(BaseController):
    def act(self, observation):
        return (random.uniform(Car.VELOCITY_LB, Car.VELOCITY_UP),
                random.uniform(Car.ANGLE_LB, Car.ANGLE_UB),
                random.uniform(Car.TIME_LB, Car.TIME_UP))
