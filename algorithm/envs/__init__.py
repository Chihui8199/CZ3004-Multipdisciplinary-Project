"""
This is the package for simulating the car-moving problem
The problem is formulated as a Markov Decision Process (MDP)

TODO: more intro here
"""
import gym
from gym.envs.registration import register

register(
    id='RobotMove-v0',
    entry_point='envs.ImageRecognitionEnv:ImageRecognitionEnv',
)

register(
    id='RobotMove-v1',
    entry_point='envs.FastestMovementEnv:FastestMovementEnv',
)


def make_env(id: str, **kwargs):
    env = gym.make(id, **kwargs)
    env.reset()
    return env
