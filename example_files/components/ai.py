"""Monster AI. Phase 1 only has one behavior; phase 2 adds roaming/fleeing/ranged
as separate classes with the same `take_turn` interface, so the engine never
needs to know which kind of AI a monster has -- it just calls `entity.ai.take_turn(...)`.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
# tcod is a roguelike/game-dev library; tcod.path holds pathfinding algorithms (A* etc.)
import tcod.path

# Only imported for type hints, not at runtime -- avoids circular imports with entity.py
# and game_map.py, which likely import this module too.
if TYPE_CHECKING:
    from example_files.entity import Entity
    from example_files.game_map import GameMap


class HostileAI:
    """Chase the target once seen, attack once adjacent.

    Note: pathfinding uses cardinal-only movement (diagonal=0) to match the
    player's movement keys, but attacking uses Chebyshev (8-directional)
    adjacency -- a monster can still swing at a diagonal neighbor even though
    it can't walk there directly. That's a deliberate simplification; tighten
    it later if it looks wrong in play.
    """

    def __init__(self) -> None:
        self.owner: Entity | None = None  # set by Entity.__init__

    def take_turn(self, target: "Entity", game_map: "GameMap", entities: list["Entity"]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        assert self.owner is not None
        monster = self.owner

        # game_map.visible is a 2D numpy bool array (one entry per tile) tracking the
        # player's current field of view; index it like a grid with [x, y].
        if not game_map.visible[monster.x, monster.y]:
            return results  # can't act on what it can't see

        dx, dy = target.x - monster.x, target.y - monster.y
        # Chebyshev distance = max(|dx|, |dy|) -- counts diagonal steps as 1, matching
        # how attack adjacency (including diagonals) works, unlike the cardinal-only
        # movement used for pathing below.
        chebyshev_distance = max(abs(dx), abs(dy))

        if chebyshev_distance <= 1:
            if target.fighter and target.fighter.hp > 0:
                results.extend(monster.fighter.attack(target))
            return results

        # Build a per-tile movement cost grid for tcod's pathfinder: 1 = walkable,
        # 0 = blocked. np.where broadcasts over the whole game_map.walkable grid at once.
        cost = np.where(game_map.walkable, 1, 0).astype(np.int8)
        for entity in entities:
            # Exclude the target too, not just the monster itself -- otherwise its own
            # tile (the pathfinding goal) gets marked unwalkable and get_path always
            # returns empty, since A* can't path onto a blocked goal tile.
            if entity is not monster and entity is not target and entity.blocks and cost[entity.x, entity.y]:
                cost[entity.x, entity.y] = 0  # don't path through other blocking entities

        # tcod.path.AStar runs A* over the cost grid; diagonal=0 disables diagonal moves
        # so paths only go cardinal directions. get_path returns a list of (x, y) tiles
        # from start to target, NOT including the start tile itself.
        path = tcod.path.AStar(cost, diagonal=0).get_path(monster.x, monster.y, target.x, target.y)
        if path:
            monster.x, monster.y = path[0]  # step onto the next tile in the path
        return results
