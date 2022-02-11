import math
import time

from envs import make_env
from envs.models import Car
from helpers import ShortestHamiltonianPathFinder

env = make_env("RobotMove-v0")
env.set_car(x=100, y=20)
env.add_obstacle(x=175, y=80, target_face_id=1)
# env.add_obstacle(x=40, y=40, target_face_id=3)
# env.add_obstacle(x=75, y=75, target_face_id=1)
# env.add_obstacle(x=150, y=150, target_face_id=1)
# env.add_obstacle(x=40, y=100, target_face_id=2)
env.reset()
env.render()
action = [1, 0, 1]
while True:
    obs_, cost, done, _ = env.step(action)
    time.sleep(0.05)
    if done:
        break
    if obs_[0][1] > 100:
        action[1] = 0.7
    env.update(rectified_car_pos=Car(x=obs_[0][0], y=obs_[0][1], z=obs_[0][2]))
