from graph import GraphBuilder
from envs import make_env

env = make_env("RobotMove-v0")
env.set_car(x=15, y=15, z=0, rectification_model=None)
env.add_obstacle(x=100, y=100, target_face_id=0)

obs = env.reset()
graph = GraphBuilder(obs, env)
graph.createGraph()

print(graph.getGraph())
