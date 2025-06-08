from .map import Map

class Drone:
    """
    Represents the drone in the simulation.
    Handles movement, energy consumption, and collision checks.
    """
    def __init__(self, start_position):
        self.position = start_position
        self.energy = 1000.0  # Starting energy

    def move(self, dx: float, dy: float):
        """Moves the drone by a given delta."""
        self.position = (self.position[0] + dx, self.position[1] + dy)
        self.energy -= self.calculate_energy_cost(dx, dy)

    def calculate_energy_cost(self, dx: float, dy: float) -> float:
        """Calculates energy cost for a move. Placeholder logic."""
        return (dx**2 + dy**2)**0.5  # Simple distance-based cost

    def check_collision(self, sim_map: Map) -> bool:
        """Checks if the drone's current position is in a collision."""
        from shapely.geometry import Point
        return sim_map.is_collision(Point(self.position)) 