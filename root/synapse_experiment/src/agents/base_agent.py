from abc import ABC, abstractmethod
from ..simulation.map import Map

class BaseAgent(ABC):
    """
    Abstract Base Class for all agents in the experiment.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def solve(self, problem_map: Map) -> list:
        """
        Solves the pathfinding problem on a given map.

        Args:
            problem_map (Map): The map object representing the problem.

        Returns:
            list: A list of points representing the calculated path.
        """
        pass 