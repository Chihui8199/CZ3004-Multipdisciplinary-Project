import logging
import time

from controllers import RandomController
from envs import make_env
from envs.models import Car


def round_to_two(l: list):
    return ['%.2f' % elem for elem in l]


def main():
    # choose one controller
    controller = RandomController()

    # set up simulator
    env = make_env("RobotMove-v0")
    env.set_car(x=15, y=15, rectification_model=None)
    env.add_obstacle(x=100, y=100, target_face_id=0)

    # start simulating
    obs = env.reset()
    while True:  # TODO: will caught in inf loop, but this is just for workflow demo
        # len(obs) > 1 means there are still points to visit

        # get an action based on the current obs
        action = controller.act(obs)

        # see if the action is feasible
        obs_, cost, done, _ = env.step(action)

        if done:
            if env.completed:
                logging.info("task completed!")
                break
            logging.debug(f"collision detected for act: {round_to_two(action)}, retrying...")
            continue  # means the act is not valid, just get another one

        # TODO: actually execute the command, need to talk to the robot team
        env.clear_sensor_data()  # clear old data
        # something like: robot.do(action)
        # inside robot.do, call env.record_sensor_data(...) whenever appropriate
        time.sleep(action[-1])  # as if it's done, we get some sensor_data

        # TODO: rectify the position through the sensor data posted back by the robot team
        # either do this manually or use the rectification_model
        # something like: rectified_car_pos = model.rectify(obs, action, env.get_sensor_data())

        # transfer the status of the env aft
        # here just use the simulated pos (as if it's perfect simulation)
        env.update(rectified_car_pos=Car(x=obs_[0][0], y=obs_[0][1], z=obs_[0][2]))

        # TODO: try recognize something and call env.recognize(...) not finalized yet
        # if all sign recognized, set completed = True
        # do image recognition
        # if recognized:
        #   env.recognize(..., ...)

        # update the latest obs at the end of one step
        obs_ = env.get_current_obs()

        # this is just an adhoc print to let you know what's going on
        logging.info(f"\n\n"
                     f"car position: {round_to_two(obs[0])},\n"
                     f"action: {round_to_two(action)},\n"
                     f"cost: {round_to_two([cost])[0]},\n"
                     f"updated car position: {round_to_two(obs_[0])}\n\n")

        obs = obs_


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    main()
