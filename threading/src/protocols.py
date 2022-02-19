"""
Communication protocols.
They are defined so that all subsystems know how to communicate with each other.
"""

ANDROID_HEADER = 'AND'.encode()
ROBOT_HEADER = 'ROB'.encode()
ALGORITHM_HEADER = 'ALG'.encode()


class AndroidToRobot:
    MOVE_UP = 'Q'.encode()
    MOVE_BACK = 'W'.encode()
    TURN_LEFT = 'E'.encode()
    TURN_RIGHT = 'R'.encode()


class AndroidToAlgorithm:
    OBSTACLE_INTO = 'T'.encode()


class AndroidToRpi:
    START = 'G'.encode()


class AlgorithmToRobot:
    SEND_COMMAND = 'I'.encode()


class AlgorithmToAndroid:
    SEND_STATUS = 'P'.encode()


class RpiToAlgorithm:
    TIME_UP = 'D'.encode()
    START = 'F'.encode()


class RobotToRpi:
    ROBOT_STOP = 'H'.encode()