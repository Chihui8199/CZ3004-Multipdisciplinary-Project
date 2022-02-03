import logging

import numpy as np

from stable_baselines3.ddpg.policies import MlpPolicy
from stable_baselines3.common.noise import OrnsteinUhlenbeckActionNoise
from stable_baselines3 import DDPG

from envs import make_env

def round_to_two(l: list):
    return ['%.2f' % elem for elem in l]

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

env = make_env("RobotMove-v0", mock=True, rl_mode=True)

# the noise objects for DDPG
n_actions = 3
param_noise = None
action_noise = OrnsteinUhlenbeckActionNoise(mean=np.zeros(n_actions), sigma=float(0.5) * np.ones(n_actions))

model = DDPG(MlpPolicy, env, verbose=1, action_noise=action_noise)
model.learn(total_timesteps=400000)
model.save("ddpg")

del model # remove to demonstrate saving and loading

model = DDPG.load("ddpg")

obs = env.reset()
done = False
while not done:
    action, _states = model.predict(obs)
    obs_, rewards, done, info = env.step(action)
    logging.info(f"\n\n"
                 f"car position: {round_to_two(obs[0])},\n"
                 f"action: {round_to_two(action)},\n"
                 f"reward: {round_to_two([rewards])[0]},\n"
                 f"updated car position: {round_to_two(obs_[0])}\n\n")
    obs = obs_
