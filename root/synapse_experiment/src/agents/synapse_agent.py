from .base_agent import BaseAgent
from ..simulation.map import Map
from ..utils.pathfinding import astar_search
from ..utils.geometry import euclidean_distance
from shapely.geometry import Point, LineString
from ..analysis.path_analyzer import analyze_path

class SYNAPSEAgent(BaseAgent):
    """
    Represents the Experimental Group agent. It gets a list of possible
    paths, dynamically determines the best evaluation metric, and then
    chooses the optimal path.
    """
    def __init__(self):
        super().__init__("SYNAPSEAgent")

    def _select_metric_profile(self, problem_map: Map) -> dict:
        """Dynamically selects a metric profile based on map characteristics."""
        w, h = problem_map.dimensions
        map_area = w * h
        obstacle_area = sum(obs.area for obs in problem_map.obstacles)
        central_corridor = LineString([problem_map.start, problem_map.end]).buffer(8)
        
        clutter_in_corridor = sum(1 for obs in problem_map.obstacles if central_corridor.intersects(obs))
        obstacle_density = obstacle_area / map_area
        is_high_risk = obstacle_density > 0.08 or clutter_in_corridor > 2

        if is_high_risk:
            print(f"[{self.name}] High risk detected (Density: {obstacle_density:.2f}, Clutter: {clutter_in_corridor}). Prioritizing safety.")
            return {'time': 0.1, 'energy': 0.1, 'safety': 0.8}
        else:
            print(f"[{self.name}] Low risk detected (Density: {obstacle_density:.2f}, Clutter: {clutter_in_corridor}). Prioritizing efficiency.")
            return {'time': 0.5, 'energy': 0.4, 'safety': 0.1}

    def _heuristic(self, pos: tuple[int, int], end: tuple[int, int], problem_map: Map, weights: dict) -> float:
        """
        The heuristic function for A* pathfinding. It's risk-aware.
        It combines distance to the goal with a penalty for proximity to obstacles.
        """
        dist_to_end = euclidean_distance(pos, end)
        
        # Risk-aware component
        safety_weight = weights.get('safety', 0.1)
        min_dist_to_obstacle = float('inf')
        
        current_point = Point(pos)
        for obs in problem_map.obstacles:
            min_dist_to_obstacle = min(min_dist_to_obstacle, current_point.distance(obs))
            
        # Add a penalty for being too close to obstacles.
        # The penalty is higher when the safety weight is higher.
        proximity_penalty = 0
        if min_dist_to_obstacle < 5: # 5 units is the "danger zone"
            proximity_penalty = (5 - min_dist_to_obstacle) * 10 * safety_weight

        return dist_to_end + proximity_penalty
        
    def _evaluate_path(self, path: list, problem_map: Map, weights: dict) -> float:
        """Evaluates a single path based on the agent's dynamic weights."""
        raw_metrics = analyze_path(path, problem_map)
        score = (weights['time'] * raw_metrics['time'] +
                 weights['energy'] * raw_metrics['energy'] +
                 weights['safety'] * raw_metrics['safety'] * 20)
        return score

    def solve(self, problem_map: Map) -> list:
        """
        Gets multiple paths and chooses the best one based on a dynamic evaluation.
        """
        # 1. Dynamic Metric Selection (SYNAPSE core feature)
        dynamic_weights = self._select_metric_profile(problem_map)
        print(f"[{self.name}] Solving map with dynamic weights: {dynamic_weights}")

        start_pos = (int(problem_map.start.x), int(problem_map.start.y))
        end_pos = (int(problem_map.end.x), int(problem_map.end.y))
        heuristic = lambda pos, end: self._heuristic(pos, end, problem_map, dynamic_weights)

        candidate_paths = astar_search(problem_map, start_pos, end_pos, heuristic, k=3)
        
        if not candidate_paths:
            print(f"[{self.name}] No paths found.")
            return []
            
        print(f"[{self.name}] Found {len(candidate_paths)} candidate paths. Evaluating...")

        best_path = None
        best_score = float('inf')

        for i, path in enumerate(candidate_paths):
            score = self._evaluate_path(path, problem_map, dynamic_weights)
            print(f"  - Path {i+1}: Score = {score:.2f}")
            if score < best_score:
                best_score = score
                best_path = path

        print(f"[{self.name}] Selected path with score {best_score:.2f}.")
        return best_path 