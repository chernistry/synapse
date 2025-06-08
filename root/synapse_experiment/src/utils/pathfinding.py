import heapq
from ..simulation.map import Map

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