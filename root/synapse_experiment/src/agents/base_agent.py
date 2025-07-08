from abc import ABC, abstractmethod
from ..simulation.continuous_map import ContinuousMap
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Abstract Base Class for all agents in the experiment.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def solve(self, problem_map: ContinuousMap) -> list:
        """
        Solves the pathfinding problem on a given map.

        Args:
            problem_map (ContinuousMap): The map object representing the problem.

        Returns:
            list: A list of points representing the calculated path.
        """
        pass

    @abstractmethod
    def adapt(self, context: Dict[str, Any]):
        """
        Adapts the agent's internal parameters based on the provided context.
        For example, updating metric weights based on performance or environment.

        Args:
            context (Dict[str, Any]): A dictionary containing simulation state or metrics.
        """
        pass 