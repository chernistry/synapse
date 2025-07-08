from typing import List, Tuple
from shapely.geometry import Polygon, Point
import numpy as np

class DynamicObstacle:
    """Represents an obstacle that can move over time."""
    def __init__(self, initial_polygon: Polygon, velocity: Tuple[float, float]):
        self.polygon = initial_polygon
        self.velocity = velocity  # (vx, vy)

    def at_time(self, t: float) -> Polygon:
        """
        Calculates the obstacle's position at a given time t.
        
        Note: This is a simplified linear translation. More complex movements
        (e.g., rotations) would require `shapely.affinity.translate`.
        """
        from shapely.affinity import translate
        dx = self.velocity[0] * t
        dy = self.velocity[1] * t
        return translate(self.polygon, xoff=dx, yoff=dy)

    def __repr__(self) -> str:
        return f"DynamicObstacle(polygon={self.polygon}, velocity={self.velocity})"


class ContinuousMap:
    """
    Represents a continuous 2D environment with static and dynamic obstacles,
    and environmental effects like wind.
    """
    def __init__(
        self,
        dimensions: Tuple[float, float],
        static_obstacles: List[Polygon],
        dynamic_obstacles: List[DynamicObstacle],
        start: Point,
        end: Point,
        wind_field: np.ndarray,
    ):
        self.dimensions = dimensions
        self.static_obstacles = static_obstacles
        self.dynamic_obstacles = dynamic_obstacles
        self.start = start
        self.end = end
        self.wind_field = wind_field  # A 2D vector field (e.g., a grid of wind vectors)

    def is_collision(self, point: Point, time: float = 0.0) -> bool:
        """
        Checks if a point collides with any obstacle at a given time.
        """
        # Check map boundaries
        if not (0 <= point.x < self.dimensions[0] and 0 <= point.y < self.dimensions[1]):
            return True

        # Check static obstacles
        for obs in self.static_obstacles:
            if obs.contains(point):
                return True

        # Check dynamic obstacles at the given time
        for dyn_obs in self.dynamic_obstacles:
            if dyn_obs.at_time(time).contains(point):
                return True

        return False

    def get_wind_at(self, point: Point) -> np.ndarray:
        """
        Gets the wind vector at a specific point.
        This implementation uses nearest-neighbor lookup on the wind grid.
        """
        grid_h, grid_w, _ = self.wind_field.shape
        map_w, map_h = self.dimensions

        # Normalize coordinates to grid indices
        x_idx = int((point.x / map_w) * (grid_w - 1))
        y_idx = int((point.y / map_h) * (grid_h - 1))
        
        # Clamp indices to be within bounds
        x_idx = max(0, min(grid_w - 1, x_idx))
        y_idx = max(0, min(grid_h - 1, y_idx))

        return self.wind_field[y_idx, x_idx]

def generate_continuous_scenario(params: dict) -> ContinuousMap:
    """
    Generates a deterministic continuous map scenario.
    """
    dimensions = params.get('dimensions', (100.0, 100.0))
    start_pos = Point(params.get('start', (5.0, 50.0)))
    end_pos = Point(params.get('end', (95.0, 50.0)))
    scenario_type = params.get('type', 'dynamic_wind')

    print(f"Generating a CONTINUOUS {dimensions} map of type '{scenario_type}'...")

    static_obstacles = []
    dynamic_obstacles = []
    
    # Example: A simple wind field blowing from left to right, stronger in the middle
    grid_res = 10
    wind_field = np.zeros((grid_res, grid_res, 2))
    for y in range(grid_res):
        # Parabolic wind profile: weak at top/bottom, strong in center
        strength = 1.5 * (1 - ((y - grid_res / 2)**2) / (grid_res / 2)**2)
        wind_field[y, :, 0] = strength # Wind blows along the x-axis

    if scenario_type == 'dynamic_wind':
        # A few static obstacles
        static_obstacles.append(Polygon([(20, 20), (25, 20), (25, 80), (20, 80)]))
        
        # A moving obstacle
        moving_poly = Polygon([(45, 40), (50, 40), (50, 60), (45, 60)])
        # Moves vertically, from bottom to top and back
        dynamic_obstacles.append(DynamicObstacle(moving_poly, velocity=(0, 5.0))) 
    
    return ContinuousMap(
        dimensions,
        static_obstacles,
        dynamic_obstacles,
        start_pos,
        end_pos,
        wind_field
    ) 