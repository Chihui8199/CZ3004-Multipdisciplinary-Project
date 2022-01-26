import gym
import logging


def get_random_action():
    pass


def main():
    env = gym.make("RobotMove-v0")
    done = False
    while not done:
        action = get_random_action()
        obs, reward, done, other_info = env.step(action)
        logging.info(f"action: {action}, observation: {obs}, reward: {reward}")


if __name__ == '__main__':
    main()