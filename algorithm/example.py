import logging

from controllers import RandomController
from envs import make_env


def main():
    controller = RandomController()
    env = make_env("RobotMove-v0")
    env.add_obstacle(x=30, y=30)
    env.add_obstacle(x=31, y=31)  # this will give you an warning, cuz this is not a valid pos
    env.set_car(x=15, y=15)
    # TODO: not yet usable; but below is the most simplified way of using it
    obs = env.reset()
    completed = False
    while not completed:  # FIXME: don't run this yet, will caught in inf loop
        # get an action based on the current obs
        action = controller.act(obs)

        # see if the action is feasible
        obs_, cost, done = env.try_step(action)

        if done:
            continue  # means the act is not valid, just get another one

        # transfer the status of the env
        env.step(obs_)

        logging.info(f"observation: {obs}, action: {action}, cost: {cost}")

        # update the obs
        obs = obs_

        # TODO: try recognize something and call env.recognize(...) not finalized yet
        # if all sign recognized, set completed = True
        

if __name__ == '__main__':
    main()
