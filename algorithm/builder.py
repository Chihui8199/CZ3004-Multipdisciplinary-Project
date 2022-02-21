from envs import make_env

from graph import GraphBuilder

env = make_env("RobotMove-v0")
env.set_car(x=15, y=15)
env.add_obstacle(x=100, y=100, target_face_id=0)

obs = env.reset()
# graph = GraphBuilder(obs, env)
# graph.createGraph()

# adjacency_matrix = graph.getGraph()
# graph = DijkstraPathFinder.Graph()

graph = GraphBuilder(obs, env)
graph.createGraph()
adjacency_list = graph.getGraph()
path = adjacency_list.dijkstra(504, 668)
actions = graph.getAction(path)

# print(path)
# print(actions)

# id = nodes*y + 4*x+dir nodes=41*4
# graph.dijkstra(adjacency_matrix, 504, 668)

# >>> 504, 668 (3,4,0,False)
# >>> 504, 1179 (7,7,3,True)
# >>> 505, 509 (4,3,1,False)
# >>> 505, 1178 (7,7,2,True)
# >>> 506, 670 (3,4,2,False)
# >>> 506, 1177 (7,7,1,True)