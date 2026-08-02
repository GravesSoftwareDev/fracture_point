from __future__ import annotations

import tcod

from fracture_point.states.base import GameState

class RunEndState(GameState):
    """
    Terminal state shown after a run ends, either by death or by
    reaching the stairs. `linked_states` is deliberately empty - there's
    nowhere to go from here yet, since the Hub/meta-progression flow
    doesn't exist. Right now this just displays a summary and the game
    quits on any key; the intent is for a future Hub state to become
    the real destination once it's built.
    """

    name = "run_end"
    linked_states = frozenset()

    def handle_event(self, event: tcod.event.Event) -> int | None:
        return None # Input is handled directly by Engine.show_run_end_screen for now.

    def render(self, map_console: tcod.console.Console, panel_console: tcod.console.Console) -> None:
        self.engine.render_map(map_console)
        self.engine.render_run_end(panel_console)