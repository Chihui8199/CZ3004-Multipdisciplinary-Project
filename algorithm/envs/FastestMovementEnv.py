import gym
import numpy as np


class FastestMovementEnv(gym.Env):
    """
    This is the env for the fastest robot movement task
    """
    def step(self, action: np.array):
        """
        move the robot
        :param action: [0]: velocity, negative for move backwards; [1]: angle; [2]: time to move
        :return: observation: np.array; TODO: add more return
        """
        pass

    def reset(self):
        pass

    def render(self, mode="human"):
        pass
