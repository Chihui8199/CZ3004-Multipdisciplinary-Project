from typing import List, Tuple

from envs.models import Direction, Sign, Entity


class Obstacle(Entity):
    BEST_VIEW_DISTANCE = 20
    """
    Represents the robot car
    """

    class Surface:
        def __init__(self, to_be_viewed_at: Direction):
            self.to_be_viewed_at = to_be_viewed_at
            self.sign = Sign.UNKNOWN

    def __init__(self, x: float, y: float, length: float = 10, width: float = 10):
        """
        :param x: x coordinate of the center of the obstacle (x-distance in cm to the origin)
        :param y: y coordinate of the center the obstacle (y-distance in cm to the origin)
        :param width: width of the obstacle in cm, default to be 10
        :param length: length of the obstacle in cm, default to be 10
        """
        # TODO: the exact default values need to be confirmed
        super().__init__(x=x, y=y, length=length, width=width)
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

    def recognize_face(self, surface_id: int, content: Sign):
        """
        TODO: this is used when a surface is recognized, need to talk to the cv team
        remove? keep?
        :return:
        """
        assert 0 <= surface_id <= 3, "surface id has to be 0, 1, 2 or 3"
        self.surfaces[surface_id].sign = content
        if content not in [Sign.UNKNOWN, Sign.BULLS_EYE]:
            self.explored = True

    def get_points_to_visit(self) -> List[Tuple[float, float, float]]:
        """
        get the coordinates to go to recognize the remaining surfaces
        :return:
        e.g.:
        [
            [x1, y1, z1],
            [x2, y2, z2],
            ...
        ]
        """
        coords = []
        if self.explored:
            return coords  # no more points to be visites
        for i, surface in enumerate(self.surfaces):
            if surface.sign == Sign.UNKNOWN:  # not visited
                if i == 0:
                    coords.append((self.x, self.y + self.y_offset, surface.to_be_viewed_at.value))
                elif i == 1:
                    coords.append((self.x - self.x_offset, self.y, surface.to_be_viewed_at.value))
                elif i == 2:
                    coords.append((self.x, self.y - self.y_offset, surface.to_be_viewed_at.value))
                else:
                    coords.append((self.x + self.x_offset, self.y, surface.to_be_viewed_at.value))
        return coords
