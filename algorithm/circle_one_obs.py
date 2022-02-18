import os
import pickle
import time

from controllers import MainController
from envs import make_env
from envs.models import Car
from graph import GraphBuilder
from helpers import ShortestHamiltonianPathFinder

# logging.getLogger().setLevel(logging.DEBUG)


if __name__ == '__main__':
    env = make_env("RobotMove-v0")
    env.set_car(x=100, y=20)
    env.add_obstacle(x=100, y=100, target_face_id=0)
    env.add_obstacle(x=100, y=100, target_face_id=1)
    env.add_obstacle(x=100, y=100, target_face_id=2)
    env.add_obstacle(x=100, y=100, target_face_id=3)
    obs = env.reset()

    file_path = './graph-one-obs.pickle'

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            graph = pickle.load(f)
    else:
        with open(file_path, 'wb') as f:
            graph = GraphBuilder(obs, env)
            graph.createGraph()
            pickle.dump(graph, f)

    graph.revert()

    controller = MainController()
    env.path = ShortestHamiltonianPathFinder.get_visit_sequence(env)
    seq = ShortestHamiltonianPathFinder.get_visit_sequence(env)[1:]

    env.render()
    while len(seq) > 0:
        actions = controller.act(observation=obs, env=env, target=seq[0], graph=graph)

        for action in actions:
            obs_, cost, done, _ = env.step(action)
            time.sleep(0.05)  # as if it's done, we get some sensor_data

            # transfer the status of the env aft
            # here just use the simulated pos (as if it's perfect simulation)
            env.update(rectified_car_pos=Car(x=obs_[0][0], y=obs_[0][1], z=obs_[0][2]))

            # update the latest obs at the end of one step
            obs_ = env.get_current_obs()

            obs = obs_
        del seq[0]


if __name__ == '__main__':
    main()
