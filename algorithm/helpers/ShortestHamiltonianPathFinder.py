import numpy as np
from python_tsp.exact import solve_tsp_dynamic_programming
from python_tsp.distances import euclidean_distance_matrix


class ShortestHamiltonianPathFinder:
    @staticmethod
    def get_visit_sequence(env):
        """
        get the sequence of nodes/points to visit for the shortest hamiltonian path

        .. warning:: note that it ignores the facing direction requirement (a.k.a abstract all entities into points)
        :param env: the env(simulator) itself
        :return: places to visit in sequence
        """
        points = [[env.car.x, env.car.y]]
        for o in env.obstacles:
            if not o.explored:
                points.append(o.get_best_point_to_visit()[:2])
        if len(points) == 1:
            return []  # nothing to be visited, just/even no starting point
        distance_matrix = euclidean_distance_matrix(np.array(points))
        permutation, _ = solve_tsp_dynamic_programming(distance_matrix)
        return [points[idx] for idx in permutation[1:]]


if __name__ == '__main__':
    """
    A quick demo of how to use this module
    """
    from envs import make_env

    env = make_env("RobotMove-v0")
    env.set_car()
    env.add_obstacle(x=100, y=100, target_face_id=0)
    env.add_obstacle(x=40, y=40, target_face_id=3)
    env.add_obstacle(x=100, y=40, target_face_id=0)
    env.reset()
    print("nodes to visit in sequence: ", ShortestHamiltonianPathFinder.get_visit_sequence(env))