from envs import make_env
import logging


def get_random_action():
    pass


def main():
    env = make_env("RobotMove-v0")
    # TODO: not yet usable; but below is the most simplified way of using it
    # done = False
    # while not done:
    #     action = get_random_action()
    #     obs, reward, done, other_info = env.step(action)
    #     logging.info(f"action: {action}, observation: {obs}, reward: {reward}")


if __name__ == '__main__':
    main()
