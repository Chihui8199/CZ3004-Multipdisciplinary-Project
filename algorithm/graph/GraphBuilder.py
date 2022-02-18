import collections
import math
import time

from envs.models import Car, Entity
from helpers import collide_with
from graph import Dijkstra

step_count = 5
side_len = 200
nodes = (side_len // step_count + 1) * 4   # 41 * 4 directions
# graph = [[0] * pow(nodes, 2) for i in range(pow(nodes, 2))]     # initialize graph


class GraphBuilder:
    def __init__(self, observation, env):
        self.observation = observation  # [[car_x, car_y, angle], obstacles([x, y, Facing])]
        self.env = env
        self._env = env
        self.graph = Dijkstra.Graph(pow(nodes, 2))
        self.action_map = {}

    def checkValidAction(self, action, current, target, x, y, new_x, new_y, dir, new_dir, rotation=False):
        self.env.set_car(x=x*5, y=y*5, z=((dir+1)*math.pi/2)%(2*math.pi))
        self.env.reset()
        obs_, cost, done, collision = self.env.step(action)
        # self.env.update(rectified_car_pos=Car(x=obs_[0][0], y=obs_[0][1], z=obs_[0][2]))
        if collision is False:
            # print(f">>> {current}, {target} ({new_x},{new_y},{new_dir},{rotation})")
            # print(f"<{current}->{target}>")
            if rotation:
                self.graph.addEdge(current, target, 10 * math.pi)
            else:
                self.graph.addEdge(current, target, 10)
            self.action_map[f'{current}_{target}'] = action

    def createGraph(self):
        # the node to consider: format is like (1, 1, N) -> "11N"
        # we will try to convert the format to adjacency matrix
        # assume car's movement is always at the grid nodes
        # car using the button left corner to represent the point
        # car: 20*20, estimate the turning radius < 10*3 cm, i.e. turning over 3*3 grid for 90 degrees
        # -> degrees: 33.69 degrees
        # list all obstacles
        obstacles = self.observation[1:]
        # conversion rule from position to adjacency matrix will be like
        # "00N" -> 0+0+0=0 "10N" -> 0+1*4+0=4 "01W" -> 21*4+0+1=85 "xyA" -> 21*4*y+4*x+A
        print("building graph...")
        for y in range(3, side_len//step_count+2-3):
            print("y: ", y)
            for x in range(3, side_len//step_count+2-3):
                # print(f"node: ({x}, {y})")
                for dir in range(4): # N W S E
                    id = nodes*y + 4*x+dir
                    # traverse all possible points around, judge collision
                    # if collision occurs, then set the edge as invalid
                    angle = 5/36*math.pi # rotation angle to achieve r=20 theoretically
                    if dir == 0: # N
                        # judge over collision using helper check validation by sampling the trajectory
                        # 6 possible directions in one move
                        # move in straight line
                        self.checkValidAction([1, 0, 5], id, nodes * (y + 1) + 4 * x + dir, x, y, x, y+1, dir, dir)
                        self.checkValidAction([-1, 0, 5], id, nodes * (y - 1) + 4 * x + dir, x, y, x, y-1, dir, dir)
                        # rotation
                        self.checkValidAction([2 * math.pi, -angle, 5], id, nodes * (y + 4) + 4 * (x + 4) + 3, x, y, x+4, y+4, dir, 3, rotation=True)
                        self.checkValidAction([2 * math.pi, angle, 5], id, nodes * (y + 4) + 4 * (x - 4) + 1, x, y, x-4, y+4, dir, 1, rotation=True)
                        self.checkValidAction([-2 * math.pi, -angle, 5], id, nodes * (y - 4) + 4 * (x + 4) + 1, x, y, x+4, y-4, dir, 1, rotation=True)
                        self.checkValidAction([-2 * math.pi, angle, 5], id, nodes * (y - 4) + 4 * (x - 4) + 3, x, y, x-4, y-4, dir, 3, rotation=True)

                    # similarly
                    elif dir == 1:
                        self.checkValidAction([1, 0, 5], id, nodes * y + 4 * (x-1) + dir, x, y, x-1, y, dir, dir)
                        self.checkValidAction([-1, 0, 5], id, nodes * y + 4 * (x+1) + dir, x, y, x+1, y, dir, dir)

                        self.checkValidAction([2 * math.pi, -angle, 5], id, nodes * (y + 4) + 4 * (x - 4) + 0, x, y, x-4, y+4, dir, 0, rotation=True)
                        self.checkValidAction([2 * math.pi, angle, 5], id, nodes * (y - 4) + 4 * (x - 4) + 2, x, y, x-4, y-4, dir, 2, rotation=True)
                        self.checkValidAction([-2 * math.pi, -angle, 5], id, nodes * (y + 4) + 4 * (x + 4) + 2, x, y, x+4, y+4, dir, 2, rotation=True)
                        self.checkValidAction([-2 * math.pi, angle, 5], id, nodes * (y - 4) + 4 * (x + 4) + 0, x, y, x+4, y-4, dir, 0, rotation=True)

                    elif dir == 2:
                        self.checkValidAction([1, 0, 5], id, nodes * (y - 1) + 4 * x + dir, x, y, x, y-1, dir, dir)
                        self.checkValidAction([-1, 0, 5], id, nodes * (y + 1) + 4 * x + dir, x, y, x, y+1, dir, dir)

                        self.checkValidAction([2 * math.pi, -angle, 5], id, nodes * (y - 4) + 4 * (x - 4) + 1, x, y, x-4, y-4, dir, 1, rotation=True)
                        self.checkValidAction([2 * math.pi, angle, 5], id, nodes * (y - 4) + 4 * (x + 4) + 3, x, y, x+4, y-4, dir, 3, rotation=True)
                        self.checkValidAction([-2 * math.pi, -angle, 5], id, nodes * (y + 4) + 4 * (x - 4) + 3, x, y, x-4, y+4, dir, 3, rotation=True)
                        self.checkValidAction([-2 * math.pi, angle, 5], id, nodes * (y + 4) + 4 * (x + 4) + 1, x, y, x+4, y+4, dir, 1, rotation=True)

                    elif dir == 3:
                        self.checkValidAction([1, 0, 5], id, nodes * y + 4 * (x + 1) + dir, x, y, x+1, y, dir, dir)
                        self.checkValidAction([-1, 0, 5], id, nodes * y + 4 * (x - 1) + dir, x, y, x-1, y, dir, dir)

                        self.checkValidAction([2 * math.pi, -angle, 5], id, nodes * (y - 4) + 4 * (x + 4) + 2, x, y, x+4, y-4, dir, 2, rotation=True)
                        self.checkValidAction([2 * math.pi, angle, 5], id, nodes * (y + 4) + 4 * (x + 4) + 0, x, y, x+4, y+4, dir, 0, rotation=True)
                        self.checkValidAction([-2 * math.pi, -angle, 5], id, nodes * (y - 4) + 4 * (x - 4) + 0, x, y, x-4, y-4, dir, 0, rotation=True)
                        self.checkValidAction([-2 * math.pi, angle, 5], id, nodes * (y + 4) + 4 * (x - 4) + 2, x, y, x-4, y+4, dir, 2, rotation=True)
        print("done")

    def getGraph(self):
        # self.graph.dijkstra(504)
        return self.graph

    def getAction(self, path):
        arr = []
        if len(path) < 2:
            return arr

        for i in range(len(path)-1):
            print(self.action_map[f'{path[i]}_{path[i+1]}'])
            arr.append(self.action_map[f'{path[i]}_{path[i+1]}'])
        return arr

    def revert(self):
        self.env.set_car(x=100, y=20)

