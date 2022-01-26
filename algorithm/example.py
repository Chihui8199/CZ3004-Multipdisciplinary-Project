import logging

from controllers import RandomController
from envs import make_env


def main():
    controller = RandomController()
    env = make_env("RobotMove-v0")
    env.add_obstacle(x=30, y=30)
    env.set_car(x=15, y=15)
    # TODO: not yet usable; but below is the most simplified way of using it
    obs = env.reset()
    done = False
    while not done:
        action = controller.act(obs)
        obs_, reward, done, other_info = env.step(action)  # not finalized yet, will break here
        logging.info(f"observation: {obs}, action: {action}")
        obs = obs_


if __name__ == '__main__':
    main()
