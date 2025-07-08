import numpy as np
from shapely.geometry import Polygon, Point, LineString

class Map:
    """
    Represents a single scenario map with obstacles.
    """
    def __init__(self, dimensions, obstacles, start, end):
        self.dimensions = dimensions
        self.obstacles = obstacles
        self.start = start
        self.end = end

    def is_collision(self, point: Point) -> bool:
        """Checks if a point collides with any obstacle."""
        # Check bounds first
        if not (0 <= point.x < self.dimensions[0] and 0 <= point.y < self.dimensions[1]):
            return True
        # Check obstacle polygons
        for obs in self.obstacles:
            if obs.contains(point):
                return True
        return False

def generate_scenario(params: dict) -> Map:
    """
    Generates a deterministic map scenario based on the specified type.
    This removes randomness to ensure reproducible and clear results for the paper.
    """
    dimensions = params.get('dimensions', (50, 50))
    start_pos = Point(params.get('start', (5, 5)))
    end_pos = Point(params.get('end', (45, 45)))
    scenario_type = params.get('type', 'deterministic_low_risk')
    
    print(f"Generating a DETERMINISTIC {dimensions} map of type '{scenario_type}'...")

    obstacles = []
    wall_thickness = 1
    w, h = dimensions

    if scenario_type == 'deterministic_trap':
        start_pos = Point(5, h // 2)
        end_pos = Point(w - 5, h // 2)
        
        # Path 1 (Bottom): Long and Safe
        # No obstacles on the bottom part
        
        # Path 2 (Middle): Short and Very Dangerous
        corridor_y = h // 2
        for i in range(10, w - 10, 2): # Very dense obstacles
            obstacles.append(Polygon([(i, corridor_y - 2), (i+wall_thickness, corridor_y - 2), (i+wall_thickness, corridor_y + 2), (i, corridor_y+2)]))

        # Path 3 (Top): Medium length and Medium risk
        for i in range(5, w - 5, 8): # Less dense obstacles
            obstacles.append(Polygon([(i, 5), (i+wall_thickness, 5), (i+wall_thickness, 15), (i, 15)]))

        # Walls to separate the paths
        obstacles.append(Polygon([(0, h - 20), (w, h - 20), (w, h-19), (0, h-19)])) # Separator for Path 1
        obstacles.append(Polygon([(0, 20), (w, 20), (w, 21), (0, 21)])) # Separator for Path 3


    elif scenario_type == 'deterministic_high_risk':
        # A maze-like structure that forces a long, complex path
        for i in range(0, w, 8):
            if i % 16 == 0:
                obstacles.append(Polygon([(i, 0), (i + wall_thickness, 0), (i + wall_thickness, h - 10), (i, h - 10)]))
            else:
                obstacles.append(Polygon([(i, 10), (i + wall_thickness, 10), (i + wall_thickness, h), (i, h)]))
    
    else: # deterministic_low_risk
        # A few simple obstacles away from the main path
        obstacles.append(Polygon([(15,15), (20,15), (20,20), (15,20)]))
        obstacles.append(Polygon([(30,30), (35,30), (35,35), (30,35)]))

    return Map(dimensions, obstacles, start_pos, end_pos) 