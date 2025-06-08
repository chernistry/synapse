from .base_agent import BaseAgent
from ..simulation.map import Map
from ..utils.pathfinding import astar_search
from ..utils.geometry import euclidean_distance
from shapely.geometry import Point
from ..analysis.path_analyzer import analyze_path

class StaticAgent(BaseAgent):
    """
    Represents the Control Group agent. It gets a list of possible
    paths and chooses the best one based on a static, predefined heuristic.
    """
    def __init__(self):
        super().__init__("StaticAgent")
        # Fixed weights for path evaluation
        self.weights = {'time': 0.4, 'energy': 0.2, 'safety': 0.4}

    def _heuristic(self, pos: tuple[int, int], end: tuple[int, int], problem_map: Map) -> float:
        """The heuristic function for A* pathfinding (not for final choice)."""
        return euclidean_distance(pos, end)

    def _evaluate_path(self, path: list, problem_map: Map) -> float:
        """Evaluates a single path based on the agent's static weights."""
        raw_metrics = analyze_path(path, problem_map)
        
        # Normalize scores for evaluation. This is a local normalization just for this agent's choice.
        # A simple normalization: lower is better, so we use the raw values directly.
        # The agent doesn't know the global min/max, it just evaluates its options.
        score = (self.weights['time'] * raw_metrics['time'] +
                 self.weights['energy'] * raw_metrics['energy'] +
                 self.weights['safety'] * raw_metrics['safety'] * 20) # Safety risk is more impactful
        
        return score

    def solve(self, problem_map: Map) -> list:
        """
        Gets multiple paths from A* and chooses the best one based on a static evaluation.
        """
        print(f"[{self.name}] Solving map with static weights: {self.weights}")
        
        start_pos = (int(problem_map.start.x), int(problem_map.start.y))
        end_pos = (int(problem_map.end.x), int(problem_map.end.y))

        heuristic = lambda pos, end: self._heuristic(pos, end, problem_map)

        # Get top 3 potential paths
        candidate_paths = astar_search(problem_map, start_pos, end_pos, heuristic, k=3)
        
        if not candidate_paths:
            print(f"[{self.name}] No paths found.")
            return []

        print(f"[{self.name}] Found {len(candidate_paths)} candidate paths. Evaluating...")

        best_path = None
        best_score = float('inf')

        for i, path in enumerate(candidate_paths):
            score = self._evaluate_path(path, problem_map)
            print(f"  - Path {i+1}: Score = {score:.2f}")
            if score < best_score:
                best_score = score
                best_path = path

        print(f"[{self.name}] Selected path with score {best_score:.2f}.")
        return best_path 