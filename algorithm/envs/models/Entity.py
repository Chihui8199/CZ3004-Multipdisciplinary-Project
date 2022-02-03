import numpy as np

from envs.models import Direction
from helpers import collide_with


class Entity:
    """
    This is a physical entity that may collide with each other
    Serves as the base class for car and obstacle
    Also can be used to represent wall
    """

    def __init__(self, x: float, y: float,
                 z: float = Direction.NORTH.value,
                 length: float = 0., width: float = 0.):
        """
        :param x: x coordinate of the entity center
        :param y: y coordinate of the entity center
        :param z: angle of the entity of [0, 2 * pi), default to be pointing north
        :param length: length of the entity in cm, default to be 0 (fallback to be a dot)
        :param width: width of the entity in cm, default to be 0
        """
        self.x = x
        self.y = y
        self.z = z
        self.length = length
        self.width = width

    def collide_with(self, other: 'Entity') -> bool:
        """
        check if the current entity collide with the other entity
        :param other:
        :return:
        """
        return collide_with(self, other)

    def get_euclidean_distance(self, other: 'Entity') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def get_positioning_status(self):
        """
        get the positioning status of the entity in a serialized way
        :return: [x, y, z]
        """
        return [self.x, self.y, self.z]

    def add_noise(self, pos_mean: float = 0., pos_std: float = 0.1, dir_mean: float = 0., dir_std: float = 0.05):
        """
        used for mock, add gaussian noise to the status of the object
        :param pos_mean:
        :param pos_std:
        :param dir_mean:
        :param dir_std:
        :return:
        """
        self.x += float(np.random.normal(pos_mean, pos_std))
        self.y += float(np.random.normal(pos_mean, pos_std))
        self.z += float(np.random.normal(dir_mean, dir_std))
