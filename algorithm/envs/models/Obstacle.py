import logging
import random
from typing import List, Tuple, Union

from envs.models import Direction, Sign, Entity


class Obstacle(Entity):
    ACTUAL_OBS, OBS_LEN = 10, 10
    BEST_VIEW_DISTANCE = 25 - (OBS_LEN - ACTUAL_OBS) / 2

    """
    Represents the robot car
    """

    class Surface:
        def __init__(self, to_be_viewed_at: Direction, is_target: bool = False):
            self.to_be_viewed_at = to_be_viewed_at
            self.sign = Sign.UNKNOWN
            self.gt = Sign.UNKNOWN  # only used in mock
            self.is_target = is_target

    def __init__(self, x: float, y: float, target_face_id: int, length: float = OBS_LEN, width: float = OBS_LEN, mock: bool = False):
        """
        :param x: x coordinate of the center of the obstacle (x-distance in cm to the origin)
        :param y: y coordinate of the center the obstacle (y-distance in cm to the origin)
        :param width: width of the obstacle in cm, default to be 10
        :param length: length of the obstacle in cm, default to be 10
        :param mock: True if to randomly allocate the surfaces
        """
        # TODO: the exact default values need to be confirmed
        super().__init__(x=x, y=y, length=length, width=width)
        self.mock = mock
        self.x_offset = width / 2 + self.BEST_VIEW_DISTANCE
        self.y_offset = length / 2 + self.BEST_VIEW_DISTANCE
        self.explored = False
        """
        surfaces:
                0
            ---------
            |       |
          1 |       |  3
            |       |
            ---------
                2
        """
        self.surfaces = [
            self.Surface(Direction.SOUTH),
            self.Surface(Direction.EAST),
            self.Surface(Direction.NORTH),
            self.Surface(Direction.WEST),
        ]

        self.target_surface_id = target_face_id

        for i, s in enumerate(self.surfaces):
            if i == target_face_id:
                s.is_target = True
            else:
                s.gt = Sign.BULLS_EYE

        self.target_surface = self.surfaces[target_face_id]

    def recognize_face(self, surface_id: int, content: Sign):
        """
        TODO: this is used when a surface is recognized, need to talk to the cv team
        remove? keep?
        :return:
        """
        assert 0 <= surface_id <= 3, "surface id has to be 0, 1, 2 or 3"
        if content not in [Sign.UNKNOWN, Sign.BULLS_EYE]:
            if not self.surfaces[surface_id].is_target:
                logging.warning(f"unexpected sign {content} at surface {surface_id}! skipped...")
                return
            self.explored = True
        self.surfaces[surface_id].sign = content

    def get_best_point_to_visit(self) -> Union[None, List[float]]:
        """
        get the coordinates to go to recognize the target surface
        :return: [x1, y1, to_be_viewed_at]
        e.g.

        |        |
        |obstacle|
        ________
         surface

           car

        to be viewed at "North"
        """
        if self.explored:
            return []  # no more points to be visited
        if self.target_surface_id == 0:
            return [self.x, self.y + self.y_offset, 0]
        elif self.target_surface_id == 1:
            return [self.x - self.x_offset, self.y, 1]
        elif self.target_surface_id == 2:
            return [self.x, self.y - self.y_offset, 2]
        else:
            return [self.x + self.x_offset, self.y, 3]
