import gym

from envs.models import *


class ImageRecognitionEnv(gym.Env):
    """
    This is the env for the autonomous image recognition task
    """

    def __init__(self, width: float = 200, length: float = 200):
        """
        create the env
        :param width: width of the map in cm, default to be 200
        :param length: length of the map in cm, default to be 200
        """
        self.width = width
        self.length = length
        self.walls = []
        # TODO: there should be better way to store obstacles other than keeping a list
        self.obstacles = []
        self.car = None
        self._add_walls()

    def _add_walls(self):
        """
        something like this:

                    ===========
                    |         |
                    |         |
                    ===========
        """
        self.walls.append(Entity(-1, self.length / 2, Direction.NORTH.value, 2, self.length))
        self.walls.append(Entity(self.width + 1, self.length / 2, Direction.NORTH.value, 2, self.length))
        self.walls.append(Entity(self.width / 2, -1, Direction.NORTH.value, self.width + 4, 2))
        self.walls.append(Entity(self.width / 2, self.length + 1, Direction.NORTH.value, self.width + 4, 2))

    def add_obstacle(self, **kwargs) -> int:
        """
        create and maintain a new obstacle
        return the id, -1 for not successful
        """
        # TODO: check collision
        # self.obstacles.append(Obstacle(**kwargs))
        pass

    def set_car(self, **kwargs):
        self.car = Car(**kwargs)

    def step(self, action):
        """
        move the car
        :param action: [0]: velocity, negative for move backwards; [1]: angle; [2]: time to move
        :return: observation: np.array; TODO: add more return and determine observation format
        """
        # TODO: below is just a scratch, representing the general workflow
        done = False
        traj = self.car.get_traj(action)
        for shadow in traj:
            for wall in self.walls:
                if wall.collide_with(shadow):
                    done = True
                    break
            for obstacle in self.obstacles:
                if obstacle.collide_with(shadow):
                    done = True
                    break
        if done:
            # TODO: do something if there is a collide
            pass
        # TODO: do something if the action is doable
        # e.g. put the car to its new pos
        final_pos = traj[-1]
        self.car.set(final_pos.x, final_pos.y, final_pos.z)
        pass

    def recognize(self, ):
        """
        this is to be used when the car recognized something (bull eye / float)
        ideally this should only be called after stepping
        :return:
        """
        # TODO: not yet sure of how to represent this, this part need to partner with the vision team (ds not confirmed)
        pass

    def reset(self):
        """
        clear the board and reset the car position
        :return:
        """
        pass

    def render(self, mode="human"):
        """
        display (optional)
        :param mode:
        :return:
        """
        pass
