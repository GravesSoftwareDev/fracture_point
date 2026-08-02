from __future__ import annotations

from typing import TYPE_CHECKING

import tcod

if TYPE_CHECKING:
    from fracture_point.engine import Engine


class GameState:
    """
    A single node in the game's state graph.

    Each concrete state controls its own input handling and rendering,
    and declares which other states it's allowed to transition into
    via `linked_states`.
    """

    name: str = "base"
    linked_states: frozenset[str] = frozenset()

    def __init__(self, engine: "Engine"):
        self.engine = engine

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: tcod.event.Event) -> int | None:
        raise NotImplementedError

    def render(self, map_console: tcod.console.Console, panel_console: tcod.console.Console) -> None:
        raise NotImplementedError