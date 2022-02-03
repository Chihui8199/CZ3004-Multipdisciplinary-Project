import numpy as np
from python_tsp.exact import solve_tsp_dynamic_programming
from python_tsp.distances import euclidean_distance_matrix


class ShortestHamiltonianPathFinder:
    @staticmethod
    def get_visit_sequence(obs):
        """
        get the sequence of nodes to visit for the shortest hamiltonian path

        .. warning:: note that it ignores the facing direction requirement (a.k.a abstract all entities into points)
        :param obs: the obs got from env
        :return: places to visit in sequence
        """
        sources = np.array([point[:2] for point in obs])
        distance_matrix = euclidean_distance_matrix(sources)
        permutation, _ = solve_tsp_dynamic_programming(distance_matrix)
        return [obs[idx] for idx in permutation[1:]]


if __name__ == '__main__':
    """
    A quick demo of how to use this module
    """
    from envs import make_env

    env = make_env("RobotMove-v0")
    env.set_car()
    env.add_obstacle(x=100, y=100)
    env.add_obstacle(x=40, y=40)
    env.add_obstacle(x=100, y=40)
    print("nodes to visit in sequence: ", ShortestHamiltonianPathFinder.get_visit_sequence(env.reset()))