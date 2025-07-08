from .base_agent import BaseAgent
from ..simulation.continuous_map import ContinuousMap
from ..utils.pathfinding import find_path_continuous
from ..analysis.path_analyzer import analyze_path_continuous
from ..llm.llama_adapter import LlamaAdapter
from typing import Dict, Any, List
from shapely.geometry import Point, LineString
import numpy as np

class SYNAPSEAgent(BaseAgent):
    """
    The SYNAPSE agent. It dynamically adapts its decision-making criteria
    by querying an LLM and evaluates multiple path options to find an
    optimal solution in complex, continuous environments.
    """
    def __init__(self):
        super().__init__("SYNAPSEAgent")
        self.weights = {'time': 0.4, 'energy': 0.3, 'safety': 0.3, 'payload_integrity': 0.1}
        self.llama_adapter = LlamaAdapter()
        self.last_metrics = {}

    def adapt(self, context: Dict[str, Any]):
        """
        Uses the LLM to adapt the metric weights based on the provided context.
        """
        print(f"[{self.name}] Adaptation triggered.")
        summary = self._create_context_summary(context)
        
        # Add previous run's metrics to give the LLM more context
        if self.last_metrics:
            summary['last_run_performance'] = self.last_metrics
            
        new_weights = self.llama_adapter.generate_metric_profile(summary)
        
        # We only update the weights relevant to path evaluation
        self.weights['time'] = new_weights.get('time', self.weights['time'])
        self.weights['energy'] = new_weights.get('energy', self.weights['energy'])
        self.weights['safety'] = new_weights.get('safety', self.weights['safety'])
        print(f"[{self.name}] Adapted weights: {self.weights}")

    def _create_context_summary(self, context: Dict[str, Any]) -> Dict:
        """Creates a summary of the environment for the LLM."""
        sim_map: ContinuousMap = context.get("problem_map")
        map_area = sim_map.dimensions[0] * sim_map.dimensions[1]
        
        static_obstacle_area = sum(o.area for o in sim_map.static_obstacles)
        dynamic_obstacle_area = sum(o.polygon.area for o in sim_map.dynamic_obstacles)
        total_obstacle_area = static_obstacle_area + dynamic_obstacle_area
        
        obstacle_density = total_obstacle_area / map_area if map_area > 0 else 0
        
        # Analyze wind intensity
        wind_magnitudes = np.linalg.norm(sim_map.wind_field, axis=2)
        
        summary = {
            "scenario_id": context.get("scenario_id"),
            "map_dimensions": sim_map.dimensions,
            "obstacle_density": round(obstacle_density, 3),
            "num_dynamic_obstacles": len(sim_map.dynamic_obstacles),
            "avg_wind_speed": round(np.mean(wind_magnitudes), 2),
            "max_wind_speed": round(np.max(wind_magnitudes), 2),
        }
        return summary

    def _evaluate_path(self, path: List[Point], sim_map: ContinuousMap) -> (float, Dict):
        """Evaluates a single path based on the agent's dynamic weights."""
        raw_metrics = analyze_path_continuous(path, sim_map)
        
        # Normalize scores for evaluation. This is a critical step.
        # For now, we use the raw values, but a real implementation would
        # normalize against a baseline or historical data.
        # Note: 'safety' is a risk (higher is worse), so we use it as is.
        # Lower for other metrics is better.
        score = (self.weights['time'] * raw_metrics['time'] +
                 self.weights['energy'] * raw_metrics['energy'] +
                 self.weights['safety'] * raw_metrics['safety'] +
                 self.weights['payload_integrity'] * raw_metrics['payload_integrity'])
        
        return score, raw_metrics

    def solve(self, problem_map: ContinuousMap) -> list:
        """
        Generates multiple candidate paths and chooses the best one based on dynamic evaluation.
        """
        print(f"[{self.name}] Solving map with dynamic weights: {self.weights}")

        # 1. Generate N candidate paths by using different seeds
        candidate_paths = []
        num_candidates = 3
        for i in range(num_candidates):
            path = find_path_continuous(
                sim_map=problem_map,
                start_pos=problem_map.start,
                end_pos=problem_map.end,
                seed=i # Use loop index as seed for different samples
            )
            if path:
                candidate_paths.append(path)
        
        if not candidate_paths:
            print(f"[{self.name}] No paths found.")
            return []
            
        print(f"[{self.name}] Found {len(candidate_paths)} candidate paths. Evaluating...")

        best_path = None
        best_score = float('inf')
        best_metrics = {}

        for i, path in enumerate(candidate_paths):
            score, raw_metrics = self._evaluate_path(path, problem_map)
            print(f"  - Path {i+1}: Score = {score:.2f}, Metrics = { {k: round(v, 2) for k, v in raw_metrics.items()} }")
            if score < best_score:
                best_score = score
                best_path = path
                best_metrics = raw_metrics

        self.last_metrics = best_metrics # Save for next adaptation cycle
        print(f"[{self.name}] Selected path with score {best_score:.2f}.")
        return best_path 