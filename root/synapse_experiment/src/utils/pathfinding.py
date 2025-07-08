import heapq
from ..simulation.map import Map
import random
import numpy as np
from shapely.geometry import Point, LineString
from ..simulation.continuous_map import ContinuousMap
from .geometry import euclidean_distance

def astar_search(problem_map: Map, start: tuple[int, int], end: tuple[int, int], heuristic_func, k: int = 1) -> list:
    """
    Performs A* search to find up to k-shortest paths.
    For k=1, it's a standard A*. For k>1, it finds alternative paths.
    This is a simplified version of Yen's algorithm logic.

    Returns:
        A list of paths. Each path is a list of coordinates.
    """
    found_paths = []
    
    # Keep track of costs to avoid re-exploring same high-cost paths
    g_score_history = {}

    while len(found_paths) < k:
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        
        # Avoid paths we already found by making their nodes "unwalkable" temporarily
        nodes_to_ignore = set()
        for path in found_paths:
            for node in path[:-1]: # Exclude the goal
                nodes_to_ignore.add(node)

        path_found_this_iteration = False
        while open_set:
            _, current_pos = heapq.heappop(open_set)

            if current_pos == end:
                path = []
                temp = current_pos
                while temp in came_from:
                    path.append(temp)
                    temp = came_from[temp]
                path.append(start)
                path.reverse()
                found_paths.append(path)
                path_found_this_iteration = True
                break

            if current_pos in nodes_to_ignore:
                continue

            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0: continue

                    neighbor_pos = (current_pos[0] + dx, current_pos[1] + dy)
                    
                    from shapely.geometry import Point
                    if problem_map.is_collision(Point(neighbor_pos)): continue

                    move_cost = 1.414 if abs(dx) == 1 and abs(dy) == 1 else 1.0
                    tentative_g_score = g_score.get(current_pos, float('inf')) + move_cost

                    if tentative_g_score < g_score.get(neighbor_pos, float('inf')):
                        # Check against history to prune search space
                        if tentative_g_score >= g_score_history.get(neighbor_pos, float('inf')):
                           continue
                        
                        g_score_history[neighbor_pos] = tentative_g_score
                        came_from[neighbor_pos] = current_pos
                        g_score[neighbor_pos] = tentative_g_score
                        f_score = tentative_g_score + heuristic_func(neighbor_pos, end)
                        heapq.heappush(open_set, (f_score, neighbor_pos))
        
        if not path_found_this_iteration:
            break # No more paths can be found

    return found_paths 

def is_edge_colliding(start_node: Point, end_node: Point, sim_map: ContinuousMap, traversal_start_time: float, travel_time: float) -> bool:
    """
    Checks if an edge between two nodes is valid, considering dynamic obstacles.
    We check for collisions at the start, middle, and end of the traversal.
    """
    edge = LineString([start_node, end_node])
    
    # 1. Check against static obstacles
    for obs in sim_map.static_obstacles:
        if edge.intersects(obs):
            return True
            
    # 2. Check against dynamic obstacles over the travel time
    num_time_steps = 5 # Check at 5 points in time for this edge traversal
    for i in range(num_time_steps + 1):
        # This is the fraction of the edge traversal duration
        time_fraction = i / num_time_steps
        # This is the absolute mission time to check for collision
        absolute_time = traversal_start_time + (time_fraction * travel_time)
        point_on_edge = edge.interpolate(time_fraction, normalized=True)
        
        if sim_map.is_collision(point_on_edge, time=absolute_time):
            return True
            
    return False

def find_path_continuous(
    sim_map: ContinuousMap,
    start_pos: Point,
    end_pos: Point,
    num_samples: int = 150,
    drone_speed: float = 2.0,
    seed: int = None
) -> list:
    """
    Finds a path in a continuous map using a visibility graph and A*.
    Handles dynamic obstacles by incorporating time into the state.
    """
    # Set seed for reproducibility
    if seed is not None:
        random.seed(seed)

    # 1. Generate a set of sample nodes + start and end
    nodes = {start_pos, end_pos}
    w, h = sim_map.dimensions
    while len(nodes) < num_samples:
        p = Point(random.uniform(0, w), random.uniform(0, h))
        if not sim_map.is_collision(p, time=0): # Check initial pos of dynamic obstacles
            nodes.add(p)
    
    nodes = list(nodes)
    node_map = {p: i for i, p in enumerate(nodes)}
    start_idx = node_map[start_pos]
    end_idx = node_map[end_pos]

    # A* state: (f_score, g_time, entry_count, current_idx, path_list)
    # entry_count is a tie-breaker to prevent comparing Point objects.
    entry_count = 0
    open_set = [(euclidean_distance((start_pos.x, start_pos.y), (end_pos.x, end_pos.y)), 0.0, entry_count, start_idx, [start_pos])]
    closed_set = set() # Stores visited (node_idx, time_discretized) tuples

    print(f"[Pathfinder] Starting continuous search with {len(nodes)} nodes...")

    while open_set:
        f_score, g_time, _, current_idx, path = heapq.heappop(open_set)

        current_pos = nodes[current_idx]
        
        # Discretize time for the closed set to avoid infinite states
        time_key = (current_idx, round(g_time, 1))
        if time_key in closed_set:
            continue
        closed_set.add(time_key)

        if current_idx == end_idx:
            print(f"[Pathfinder] Path found with time: {g_time:.2f}s")
            return path

        # 2. Explore neighbors (all other nodes in the visibility graph)
        for neighbor_idx, neighbor_pos in enumerate(nodes):
            if neighbor_idx == current_idx:
                continue

            dist = current_pos.distance(neighbor_pos)
            if dist == 0: continue

            # Estimate travel time (ignoring wind for now for edge building)
            # A more advanced version would account for wind here.
            travel_time = dist / drone_speed 
            
            # 3. Check for collisions along the edge
            if not is_edge_colliding(current_pos, neighbor_pos, sim_map, traversal_start_time=g_time, travel_time=travel_time):
                
                new_g_time = g_time + travel_time
                heuristic = euclidean_distance((neighbor_pos.x, neighbor_pos.y), (end_pos.x, end_pos.y))
                new_f_score = new_g_time + (heuristic / drone_speed) # Heuristic in terms of time

                new_path = path + [neighbor_pos]
                entry_count += 1
                heapq.heappush(open_set, (new_f_score, new_g_time, entry_count, neighbor_idx, new_path))
    
    print("[Pathfinder] No path found.")
    return [] 