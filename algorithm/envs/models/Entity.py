from envs.models import Direction
from envs.helpers import collide_with


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

    def get_positioning_status(self):
        """
        get the positioning status of the entity in a serialized way
        :return: [x, y, z]
        """
        return [self.x, self.y, self.z]
