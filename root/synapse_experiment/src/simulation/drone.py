from .continuous_map import ContinuousMap
from shapely.geometry import Point
import numpy as np

class Drone:
    """
    Represents the drone in the simulation, updated for continuous space and physics.
    Handles movement, energy consumption, and collision checks with dynamic obstacles.
    """
    def __init__(self, start_position: Point):
        self.position = start_position
        self.energy = 2000.0  # Increased energy for more complex scenarios
        self.max_thrust = 2.0 # Maximum force the drone can exert

    def move(self, propulsion_vector: np.ndarray, sim_map: ContinuousMap, time_step: float):
        """
        Moves the drone based on a propulsion vector, affected by wind.
        The drone's final movement is the sum of its own propulsion and environmental wind.
        """
        # Get wind vector at current position
        wind_vector = sim_map.get_wind_at(self.position)
        
        # Ensure propulsion doesn't exceed max thrust
        propulsion_magnitude = np.linalg.norm(propulsion_vector)
        if propulsion_magnitude > self.max_thrust:
            propulsion_vector = (propulsion_vector / propulsion_magnitude) * self.max_thrust
            
        # Final velocity is the sum of propulsion and wind
        final_velocity_vector = propulsion_vector + wind_vector
        
        # Update position
        dx = final_velocity_vector[0] * time_step
        dy = final_velocity_vector[1] * time_step
        self.position = Point(self.position.x + dx, self.position.y + dy)

        # Update energy
        self.energy -= self.calculate_energy_cost(propulsion_vector, time_step)

    def calculate_energy_cost(self, propulsion_vector: np.ndarray, time_step: float) -> float:
        """
        Calculates energy cost for a move.
        Cost is proportional to the square of the thrust magnitude (effort).
        """
        thrust_magnitude = np.linalg.norm(propulsion_vector)
        # Power is proportional to thrust squared (a simplification)
        power = thrust_magnitude**2
        return power * time_step

    def check_collision(self, sim_map: ContinuousMap, time: float) -> bool:
        """
        Checks if the drone's current position is in a collision at a specific time.
        """
        return sim_map.is_collision(self.position, time) 