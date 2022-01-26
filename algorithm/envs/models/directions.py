import math
from enum import Enum


class Direction(Enum):
    EAST = 0
    NORTH = math.pi * 0.5
    WEST = math.pi
    SOUTH = math.pi * 1.5
