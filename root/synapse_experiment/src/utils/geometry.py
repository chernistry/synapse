import math

def euclidean_distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Calculates the Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_angle(p1: tuple, p2: tuple, p3: tuple) -> float:
    """
    Calculates the angle (in degrees) at vertex p2 for the path segment p1-p2-p3.
    Returns 180 for straight lines.
    """
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    
    mag_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag_v2 = math.sqrt(v2[0]**2 + v2[1]**2)
    
    if mag_v1 == 0 or mag_v2 == 0:
        return 180.0 # Straight line if a point is repeated

    cos_angle = dot_product / (mag_v1 * mag_v2)
    
    # Clamp to avoid floating point errors with acos
    cos_angle = max(-1.0, min(1.0, cos_angle))
    
    return math.degrees(math.acos(cos_angle)) 