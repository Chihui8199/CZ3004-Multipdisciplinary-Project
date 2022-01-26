import gym
from numbers import Number

import torch


class ImageRecognitionEnv(gym.Env):
    """
    This is the env for the autonomous image recognition task
    """
    def __init__(self, rectification_model: torch.nn.Module = None,
                 width: Number = 200, length: Number = 200):
        """
        create the env
        :param rectification_model: model used to rectify the position of the car after moving
        :param width: width of the map in cm, default to be 200
        :param length: length of the map in cm, default to be 200
        """
        self.rectification_model = rectification_model
        self.width = width
        self.length = length
        # TODO: there should be better way to store obstacles other than keeping a list
        self.obstacles = []  # TODO: abstract obstacle to a type of object
        self.car = None  # TODO: abstract car to a type of object

    def add_obstacle(self, x: Number, y: Number, width: Number = 10, length: Number = 10) -> bool:
        """
        create and maintain a new obstacle
        :param x: x coordinate of the center of the obstacle (x-distance in cm to the origin)
        :param y: y coordinate of the center the obstacle (y-distance in cm to the origin)
        :param width: width of the obstacle in cm, default to be 10
        :param length: length of the obstacle in cm, default to be 10
        :return: true if the obstacle is added; false otherwise (typical reason: clash with car/wall/other obstacle)
        """
        # TODO:
        pass

    def step(self, action):
        """
        move the car
        :param action: [0]: velocity, negative for move backwards; [1]: angle; [2]: time to move
        :return: observation: np.array; TODO: add more return and determine observation format
        """
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
