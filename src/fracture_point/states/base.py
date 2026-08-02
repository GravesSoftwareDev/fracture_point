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
    via `linked_states`. This is what lets us enforce things like 
    "the inventory can be opened from Playing, but Crafting is only 
    reachable from the Hub" at the graph level, instead of trusting
    every piece of code to respect an unwritten rule.
    """

    name: str = "base"
    linked_states: frozenset[str] = frozenset()

    def __init__(self, engine: "Engine"):
        self.engine = engine

    def on_enter(self) -> None:
        """
        Called when this state becomes current. Override for setup logic.
        """

    def on_exit(self) -> None:
        """
        Called when this state stops being current. Override for cleanup logic.
        """

    def handle_event(self, event: tcod.event.Event) -> int | None:
        """
        Process one input event.

        Return an int (tick cost) if this event ended the players turn.
        Return None if it didn't consume a turn.
        """
        raise NotImplementedError

    def render (self, console: tcod.console.Console) -> None:
        raise NotImplementedError