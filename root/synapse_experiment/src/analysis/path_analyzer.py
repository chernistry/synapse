from ..simulation.map import Map
from ..utils.geometry import euclidean_distance, calculate_angle
from shapely.geometry import Point

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