import logging
import time
import pickle
import os.path

from controllers import MainController

from envs import make_env
from envs.models import Car

from graph import GraphBuilder

from helpers import ShortestHamiltonianPathFinder

def round_to_two(l: list):
    return ['%.2f' % elem for elem in l]

def main():
    env = make_env("RobotMove-v0")
    env.set_car(x=15, y=15)
    # 6 0 up
    # 2 19 down
    # 17 16 left
    # 13 4 left
    # 9 13 right
    env.add_obstacle(x=6*10+5, y=0*10+5, target_face_id=0)
    env.add_obstacle(x=2*10+5, y=19*10+5, target_face_id=2)
    env.add_obstacle(x=17*10+5, y=16*10+5, target_face_id=1)
    env.add_obstacle(x=13*10+5, y=4*10+5, target_face_id=1)
    env.add_obstacle(x=9*10+5, y=13*10+5, target_face_id=3)
    obs = env.reset()

    file_path = 'graph.pickle'
    os.path.exists(file_path)
    graph = None

    overwrite = False

    try:
        if os.path.exists(file_path) and not overwrite:
            with open(file_path, 'rb') as f:
                graph = pickle.load(f)
        else:
            with open(file_path, 'wb') as f:
                start = time.time()
                graph = GraphBuilder(obs, env)
                graph.createGraph()
                pickle.dump(graph, f)
                print("building time: ", time.time() - start)
    except:
        with open(file_path, 'wb') as f:
            start = time.time()
            graph = GraphBuilder(obs, env)
            graph.createGraph()
            pickle.dump(graph, f)
            print("building time: ", time.time() - start)

    # graph.revert()  # reset graph

    controller = MainController()
    env.path = ShortestHamiltonianPathFinder.get_visit_sequence(env)[0]
    seq = ShortestHamiltonianPathFinder.get_visit_sequence(env)[0][1:]
    obs_seq = ShortestHamiltonianPathFinder.get_visit_sequence(env)[1]
    print(obs_seq)
    print(seq)

    env.render()

    prev_action = None

    while len(seq) > 0:
        # print(seq)
        action = controller.act(observation=obs, env=env, target=seq[0], graph=graph)

        if action is None:
            del seq[0]
            continue

    # for action in actions:
        obs_, cost, done, _ = env.step(action)

        if done:
            if env.completed:
                logging.info("task completed!")
                break
            logging.debug(f"collision detected for act: {round_to_two(action)}, retrying...")
            continue  # means the act is not valid, just get another one

        env.clear_sensor_data()  # clear old data
        # something like: robot.do(action)
        # inside robot.do, call env.record_sensor_data(...) whenever appropriate
        time.sleep(0.1)  # as if it's done, we get some sensor_data

        # transfer the status of the env aft
        # here just use the simulated pos (as if it's perfect simulation)
        env.update(rectified_car_pos=Car(x=obs_[0][0], y=obs_[0][1], z=obs_[0][2]))

        # update the latest obs at the end of one step
        obs_ = env.get_current_obs()

        # this is just an adhoc print to let you know what's going on
        logging.info(f"\n\n"
                     f"car position: {round_to_two(obs[0])},\n"
                     f"action: {round_to_two(action)},\n"
                     f"cost: {round_to_two([cost])[0]},\n"
                     f"updated car position: {round_to_two(obs_[0])}\n\n")

        obs = obs_
        # prev_action = action


if __name__ == '__main__':
    main()