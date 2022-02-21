import math

from controllers.BaseController import BaseController
from envs.models import Car


"""
Main points:
1. hamiltonian path planning
2. trip planning and obstacle avoidance, possible virtual obstacle
3. image not found
"""
class MainController(BaseController):
    def act(self, observation, env, target, graph):
        # print("observation: ", observation)
        # print("env:", env)
        # print("sequence: ", seq[1:])    # sequenct to visit

        car = observation[0]
        # target = seq[1]  # node to visit
        # print("car: ", car)
        # print("target: ", target)

        # plan path and decide next action to move
        nodes = 41 * 4
        # id = nodes * y + 4 * x + dir
        car_id = round(4 * car[0] / 5 + nodes * car[1] / 5 + (round((car[2] / (math.pi / 2)))+3) % 4)
        target_id = round(4 * target[0] / 5 + nodes * target[1] / 5 + (target[2] + 2) % 4)

        adjacency_list = graph.getGraph()
        path = adjacency_list.dijkstra(car_id, target_id)
        # print("path: ", path)
        actions = graph.getAction(path)
        # print("actions: ", actions)

        if len(actions) > 0:
            return actions[0]
        else:
            return None
