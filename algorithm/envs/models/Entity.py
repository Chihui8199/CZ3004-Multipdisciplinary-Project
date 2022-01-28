from envs.models import Direction
from envs.helpers import collide_with

class Entity:
    """
    This is a physical entity that may collide with each other
    Serves as the base class for car and obstacle
    Also can be used to represent wall
    """

    def __init__(self, x: float, y: float,
                 length: float, width: float,
                 z: float = Direction.NORTH.value):
        """
        :param x: x coordinate of the entity center
        :param y: y coordinate of the entity center
        :param z: angle of the entity of [0, 2 * pi), default to be pointing north
        :param length: length of the entity in cm
        :param width: width of the entity in cm
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
