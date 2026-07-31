"""All drawing lives here, separate from Engine's game logic. Engine never
imports tcod.console -- it hands render_all() a console and reads its own state.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import tcod.console

if TYPE_CHECKING:
    from an_example.ex_engine import Engine

FLOOR_VISIBLE, FLOOR_EXPLORED = (200, 180, 50), (60, 55, 20)
WALL_VISIBLE, WALL_EXPLORED = (130, 110, 50), (40, 35, 20)
LOG_COLOR = (180, 180, 220)


def camera_offset(
    focus_x: int, focus_y: int, screen_width: int, screen_height: int, map_width: int, map_height: int,
) -> tuple[int, int]:
    """Top-left world coordinate the screen should show, clamped to map edges."""
    cam_x = max(0, min(map_width - screen_width, focus_x - screen_width // 2))
    cam_y = max(0, min(map_height - screen_height, focus_y - screen_height // 2))
    return cam_x, cam_y


def render_all(
    console: tcod.console.Console,
    engine: "Engine",
    camera_x: int,
    camera_y: int,
    screen_width: int,
    screen_height: int,
) -> None:
    game_map = engine.game_map

    for sx in range(screen_width):
        for sy in range(screen_height):
            wx, wy = camera_x + sx, camera_y + sy
            if not game_map.in_bounds(wx, wy) or not game_map.explored[wx, wy]:
                continue  # never seen: leave blank
            is_wall = not game_map.walkable[wx, wy]
            if game_map.visible[wx, wy]:
                color = WALL_VISIBLE if is_wall else FLOOR_VISIBLE
            else:
                color = WALL_EXPLORED if is_wall else FLOOR_EXPLORED
            console.print(x=sx, y=sy, text="#" if is_wall else ".", fg=color)

    for entity in engine.entities:
        if game_map.visible[entity.x, entity.y]:
            console.print(x=entity.x - camera_x, y=entity.y - camera_y, text=entity.char, fg=entity.color)

    for i, message in enumerate(engine.messages):
        console.print(x=0, y=screen_height + i, text=message, fg=LOG_COLOR)