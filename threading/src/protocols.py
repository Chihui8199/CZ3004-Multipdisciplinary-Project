"""
Communication protocols.
They are defined so that all subsystems know how to communicate with each other.
"""

NEWLINE = '\n'.encode()

ANDROID_HEADER = 'AND'.encode()
ROBOT_HEADER = 'ROB'.encode()
ALGORITHM_HEADER = 'ALG'.encode()


class AndroidToRobot:
    MOVE_UP = 'Q'.encode()
    MOVE_BACK = 'W'.encode()
    TURN_LEFT = 'E'.encode()
    TURN_RIGHT = 'R'.encode()

    ALL_MESSAGES = [
        MOVE_UP,
        MOVE_BACK,
        TURN_LEFT,
        TURN_RIGHT
    ]


class AndroidToAlgorithm:
    OBSTACLE_INTO = 'T'.encode()


class AlgorithmToAndroid:
    SEND_STATUS = 'P'.encode()
