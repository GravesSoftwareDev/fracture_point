from __future__ import annotations

import numpy as np
import tcod

from fracture_point.game_map import GameMap

def compute_path(game_map: GameMap, start: tuple[int, int], goal: tuple[int, int])-> list[tuple[int, int]]:
    """
    A* path from start to goal, walls-only cost (doesn't account for other entities standing in the way since "blocked by a monster" should probably mean "attack it" or "wait" rather than reroute).

    Returns a list of (x, y) steps, NOT including the start tile.
    Empty list if no path exists.
    """

    cost = np.where(game_map.tiles, 1, 0).astype(np.int8)

    graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
    pathfinder = tcod.path.Pathfinder(graph)
    pathfinder.add_root(start)

    path = pathfinder.path_to(goal).tolist()
    return path[1:]