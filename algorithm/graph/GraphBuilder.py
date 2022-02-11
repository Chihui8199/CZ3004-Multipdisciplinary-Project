import collections
import math

from envs.models import Car, Entity
from helpers import collide_with

class GraphBuilder:
    def __init__(self, observation, env):
        self.observation = observation # [[car_x, car_y, angle], obstacles([x, y, Facing])]
        self.env = env
        self.grid_size = 20
        self.nodes = (self.grid_size+1)*4
        # initialize graph
        self.graph = [[0] * pow(self.nodes, 2) for i in range(pow(self.nodes, 2))]

    def checkValidAction(self, action, current, target, rotation=False):
        obs_, cost, done, _ = self.env.step(action)

        if done:
            print(f">>>> {current}, {target}")
            if rotation:
                self.graph[current][target] = 15 * math.pi
            else:
                self.graph[current][target] = 10

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
        for x in range(self.grid_size+1):
            for y in range(self.grid_size+1):
                print(f"node: ({x}, {y})")
                for dir in range(4): # N W S E
                    id = self.nodes*y + 4*x + 1
                    # traverse all possible points around, judge collision
                    # if collision occurs, then set the edge as invalid
                    angle = math.atan2(20, 30) # rotation angle to achieve r=30 theoretically
                    if dir == 0: # N
                        # judge over collision using helper check validation by sampling the trajectory
                        # 6 possible directions in one move
                        # move in straight line
                        self.checkValidAction([2, 0, 5], id, self.nodes * (y + 1) + 4 * x + dir)
                        self.checkValidAction([-2, 0, 5], id, self.nodes * (y - 1) + 4 * x + dir)
                        # rotation
                        self.checkValidAction([math.pi, angle, 15], id, self.nodes * (y + 2) + 4 * (x - 2) + 3)
                        self.checkValidAction([math.pi, -angle, 15], id, self.nodes * (y + 2) + 4 * (x + 2) + 1)
                        self.checkValidAction([-math.pi, angle, 15], id, self.nodes * (y - 2) + 4 * (x + 2) + 1)
                        self.checkValidAction([-math.pi, -angle, 15], id, self.nodes * (y - 2) + 4 * (x - 2) + 3)

                    # similarly
                    elif dir == 1:
                        self.checkValidAction([2, 0, 5], id, self.nodes * y + 4 * (x-1) + dir)
                        self.checkValidAction([-2, 0, 5], id, self.nodes * y + 4 * (x+1) + dir)

                        self.checkValidAction([math.pi, angle, 15], id, self.nodes * (y + 2) + 4 * (x - 2) + 0)
                        self.checkValidAction([math.pi, -angle, 15], id, self.nodes * (y - 2) + 4 * (x - 2) + 2)
                        self.checkValidAction([-math.pi, angle, 15], id, self.nodes * (y + 2) + 4 * (x + 2) + 2)
                        self.checkValidAction([-math.pi, -angle, 15], id, self.nodes * (y - 2) + 4 * (x + 2) + 0)

                    elif dir == 2:
                        self.checkValidAction([2, 0, 5], id, self.nodes * (y - 1) + 4 * x + dir)
                        self.checkValidAction([-2, 0, 5], id, self.nodes * (y + 1) + 4 * x + dir)

                        self.checkValidAction([math.pi, angle, 15], id, self.nodes * (y - 2) + 4 * (x - 2) + 1)
                        self.checkValidAction([math.pi, -angle, 15], id, self.nodes * (y - 2) + 4 * (x + 2) + 3)
                        self.checkValidAction([-math.pi, angle, 15], id, self.nodes * (y + 2) + 4 * (x - 2) + 3)
                        self.checkValidAction([-math.pi, -angle, 15], id, self.nodes * (y + 2) + 4 * (x + 2) + 1)

                    elif dir == 3:
                        self.checkValidAction([2, 0, 5], id, self.nodes * y + 4 * (x + 1) + dir)
                        self.checkValidAction([-2, 0, 5], id, self.nodes * y + 4 * (x - 1) + dir)

                        self.checkValidAction([math.pi, angle, 15], id, self.nodes * (y - 2) + 4 * (x + 2) + 2)
                        self.checkValidAction([math.pi, -angle, 15], id, self.nodes * (y + 2) + 4 * (x + 2) + 0)
                        self.checkValidAction([-math.pi, angle, 15], id, self.nodes * (y - 2) + 4 * (x - 2) + 0)
                        self.checkValidAction([-math.pi, -angle, 15], id, self.nodes * (y + 2) + 4 * (x - 2) + 2)

    def getGraph(self):
        return self.graph