import math

import cv2

from envs.models import Entity


def collide_with(a: Entity, b: Entity) -> bool:
    """
    detect if two entities collide with each other
    reference:
    https://cfonheart.github.io/2018/09/11/%E8%AE%A1%E7%AE%97%E6%97%8B%E8%BD%AC%E7%9F%A9%E5%BD%A2%E7%9B%B8%E4%BA%A4%E9%9D%A2%E7%A7%AF/
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
        return ((360 * radian / (2 * math.pi)) - 90) % 360

    r = cv2.rotatedRectangleIntersection(
        ((a.x, a.y), (a.width,
                      a.length), radian_to_degrees(a.z)),
        ((b.x, b.y), (b.width, b.length), radian_to_degrees(b.z)))
    if r == (0, None):
        return False
    return True

# TODO: add some unit test
