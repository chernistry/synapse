from ..simulation.map import Map
from ..simulation.continuous_map import ContinuousMap
from ..utils.geometry import euclidean_distance, calculate_angle
from shapely.geometry import Point, LineString
import numpy as np

def analyze_path(path: list, problem_map: Map) -> dict:
    """Calculates raw performance scores for a given path."""
    if not path or len(path) < 2:
        return {'time': float('inf'), 'energy': float('inf'), 'safety': float('inf'), 'payload_integrity': float('inf')}

    path_length = sum(euclidean_distance(path[i], path[i+1]) for i in range(len(path)-1))
    
    safety_risk = 0
    for pos in path:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0: continue
                if problem_map.is_collision(Point(pos[0] + dx, pos[1] + dy)):
                    safety_risk += 1
                    break

    sharp_turns = 0
    if len(path) > 2:
        for i in range(len(path) - 2):
            angle = calculate_angle(path[i], path[i+1], path[i+2])
            if angle < 120:
                sharp_turns += 1

    return {
        'time': path_length,
        'energy': path_length,
        'safety': safety_risk,
        'payload_integrity': sharp_turns
    }

def analyze_path_continuous(path: list, sim_map: ContinuousMap, drone_speed: float = 2.0) -> dict:
    """Calculates raw performance scores for a path in a continuous map."""
    if not path or len(path) < 2:
        return {'time': float('inf'), 'energy': float('inf'), 'safety': 0.0, 'payload_integrity': float('inf')}

    # 1. Time and Path Length
    path_segments = [LineString([path[i], path[i+1]]) for i in range(len(path)-1)]
    path_length = sum(seg.length for seg in path_segments)
    estimated_time = path_length / drone_speed

    # 2. Energy Estimation (propulsion against wind)
    total_energy_effort = 0
    for seg in path_segments:
        mid_point = seg.interpolate(0.5, normalized=True)
        wind_vector = sim_map.get_wind_at(mid_point)
        
        path_vector = np.array([seg.coords[1][0] - seg.coords[0][0], seg.coords[1][1] - seg.coords[0][1]])
        path_direction = path_vector / np.linalg.norm(path_vector)
        
        # Project wind vector onto path direction
        wind_component = np.dot(wind_vector, path_direction)
        
        # Energy is higher if moving against the wind
        effort = (drone_speed - wind_component)**2
        total_energy_effort += effort * seg.length
    
    # 3. Safety (inverse of min distance to an obstacle)
    # A higher score means less safe.
    min_dist_to_obstacle = float('inf')
    path_line = LineString(path)
    
    all_obstacles = sim_map.static_obstacles
    # For simplicity, we check dynamic obstacles at their starting positions.
    # A full analysis would require checking over time.
    all_obstacles += [obs.polygon for obs in sim_map.dynamic_obstacles]
    
    for obs in all_obstacles:
        min_dist_to_obstacle = min(min_dist_to_obstacle, path_line.distance(obs))

    # Safety score: higher is worse. We use 1/(dist+epsilon) to avoid division by zero.
    safety_risk = 1 / (min_dist_to_obstacle + 1e-6)

    # 4. Payload Integrity (sharp turns)
    sharp_turns = 0
    if len(path) > 2:
        for i in range(len(path) - 2):
            # The points are shapely Points, need to convert to tuples for calculate_angle
            p1 = (path[i].x, path[i].y)
            p2 = (path[i+1].x, path[i+1].y)
            p3 = (path[i+2].x, path[i+2].y)
            angle = calculate_angle(p1, p2, p3)
            if angle < 135: # Stricter angle for continuous space
                sharp_turns += 1
    
    return {
        'time': estimated_time,
        'energy': total_energy_effort,
        'safety': safety_risk,
        'payload_integrity': sharp_turns
    } 