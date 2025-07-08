from .base_agent import BaseAgent
from ..simulation.continuous_map import ContinuousMap
from ..utils.pathfinding import find_path_continuous
from typing import Dict, Any

class StaticAgent(BaseAgent):
    """
    Represents the Control Group agent. It uses a static, predefined
    approach to solve the pathfinding problem in a continuous environment.
    """
    def __init__(self):
        super().__init__("StaticAgent")
        # These weights are now conceptual, as the pathfinding is more direct.
        # They might be used later for a post-mortem analysis.
        self.weights = {'time': 0.5, 'energy': 0.3, 'safety': 0.2}

    def solve(self, problem_map: ContinuousMap) -> list:
        """
        Solves the pathfinding problem by finding a single, viable path.
        """
        print(f"[{self.name}] Solving map with static parameters...")

        # The new pathfinder finds a single, good path directly.
        # The complexity of choosing between multiple paths is removed for the static agent.
        path = find_path_continuous(
            sim_map=problem_map,
            start_pos=problem_map.start,
            end_pos=problem_map.end
        )
        
        if not path:
            print(f"[{self.name}] No path found.")
            return []

        print(f"[{self.name}] Path found with {len(path)} waypoints.")
        return path

    def adapt(self, context: Dict[str, Any]):
        """
        The StaticAgent does not adapt. This method is a no-op.
        """
        # print(f"[{self.name}] Received adaptation context, but choosing not to adapt.")
        pass 