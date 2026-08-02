from __future__ import annotations

import tcod

from fracture_point.states.base import GameState

MOVE_KEYS = {
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.W: (0, -1),
    tcod.event.KeySym.S: (0, 1),
    tcod.event.KeySym.A: (-1, 0),
    tcod.event.KeySym.D: (1, 0),
}


class PlayingState(GameState):
    """The main dungeon-crawling state: movement, attacking, casting,
    picking up items, and opening the inventory overlay.

    Unequipping used to have its own direct key here ('u'), but it only
    ever unequipped the weapon slot - a leftover from before jewelry/
    armor slots existed. That's been removed in favor of a proper
    Unequip menu reachable through the inventory overlay, which can
    target any filled slot.
    """

    name = "playing"
    linked_states = frozenset({"inventory", "run_end"})

    def handle_event(self, event: tcod.event.Event) -> int | None:
        if not isinstance(event, tcod.event.KeyDown):
            return None

        engine = self.engine

        if event.sym == tcod.event.KeySym.ESCAPE:
            raise SystemExit()

        if event.sym == tcod.event.KeySym.I:
            engine.states.push("inventory")
            return None

        if event.sym == tcod.event.KeySym.G:
            if engine.try_pickup():
                return engine.player.fighter.action_cost
            return None

        if event.sym == tcod.event.KeySym.C:
            return engine.attempt_cast()

        if event.sym in MOVE_KEYS:
            dx, dy = MOVE_KEYS[event.sym]
            if engine.player_action(dx, dy):
                engine.update_fov()
                return engine.player.fighter.action_cost
            return None

        return None

    def render(self, map_console: tcod.console.Console, panel_console: tcod.console.Console) -> None:
        engine = self.engine
        engine.render_map(map_console)
        engine.render_sidebar(panel_console)