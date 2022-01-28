import math

import cv2

from envs.models import Entity


def collide_with(a: Entity, b: Entity) -> bool:
    """
    detect if two entities collide with each other
    :param a:
    :param b:
    :return: True if they collide, False otherwise
    """
    def radian_to_degrees(radian):
        """
        convert our angle to cv2 angle
        :param radian:
        :return:
        """
        return ((360 * (2 * math.pi - radian) / (2 * math.pi)) + 270) % 360

    r = cv2.rotatedRectangleIntersection(((a.x, a.y), (a.width, a.length), radian_to_degrees(a.z)),
                                          ((b.x, b.y), (b.width, b.length), radian_to_degrees(b.z)))
    if r == (0, None):
        return False
    return True

# TODO: add some unit test
