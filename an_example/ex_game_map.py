"""The dungeon: walkable/explored/visible NumPy arrays plus room+corridor
generation. Same tcod.map.compute_fov approach as the tutorial (chapter 5),
just wrapped in a class so Engine doesn't have to juggle three loose arrays.
"""
from __future__ import annotations

import random

import numpy as np
import tcod.map
from tcod import libtcodpy

FOV_RADIUS = 8


class GameMap:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.walkable = np.zeros((width, height), dtype=bool, order="F")
        self.explored = np.zeros((width, height), dtype=bool, order="F")
        self.visible = np.zeros((width, height), dtype=bool, order="F")

    @property
    def transparent(self) -> np.ndarray:
        # Separate from `walkable` on purpose: a window could be transparent
        # but not walkable. They're the same array for now since every floor
        # tile here is both.
        return self.walkable

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and bool(self.walkable[x, y])

    def update_fov(self, pov: tuple[int, int]) -> None:
        self.visible = tcod.map.compute_fov(
            self.transparent,
            pov=pov,
            radius=FOV_RADIUS,
            light_walls=True,
            algorithm=libtcodpy.FOV_SYMMETRIC_SHADOWCAST,
        )
        self.explored |= self.visible


def generate_map(
    rng: random.Random, map_width: int, map_height: int, max_rooms: int = 14,
) -> tuple[GameMap, tuple[int, int], tuple[int, int]]:
    """Carve rooms connected by L-shaped corridors. Returns (map, player_start, monster_start)."""
    game_map = GameMap(map_width, map_height)
    centers: list[tuple[int, int]] = []

    for _ in range(max_rooms):
        w, h = rng.randint(4, 9), rng.randint(4, 7)
        x = rng.randint(1, map_width - w - 2)
        y = rng.randint(1, map_height - h - 2)
        game_map.walkable[x : x + w, y : y + h] = True
        center = (x + w // 2, y + h // 2)

        if centers:
            prev_x, prev_y = centers[-1]
            new_x, new_y = center
            x_from, x_to = sorted((prev_x, new_x))
            game_map.walkable[x_from : x_to + 1, prev_y] = True
            y_from, y_to = sorted((prev_y, new_y))
            game_map.walkable[new_x, y_from : y_to + 1] = True

        centers.append(center)
    return game_map, centers