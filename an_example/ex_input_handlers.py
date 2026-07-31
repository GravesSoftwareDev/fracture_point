"""Turns a raw tcod.event into an action dict, keyed off the current GameState.

Keeping this separate from Engine means the engine never touches tcod.event at
all -- it only ever sees plain dicts like {"move": (dx, dy)} or {"quit": True}.
That split is what makes it easy to add e.g. a networked or replay-driven input
source later without touching game logic.
"""
from __future__ import annotations

from typing import Any

import tcod.event

from ex_engine import GameState

MOVE_KEYS = {
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.K: (0, -1),  # vi-keys
    tcod.event.KeySym.J: (0, 1),
    tcod.event.KeySym.H: (-1, 0),
    tcod.event.KeySym.L: (1, 0),
}


def _dispatch_player_turn(event: tcod.event.Event) -> dict[str, Any]:
    match event:
        case tcod.event.Quit():
            return {"quit": True}
        case tcod.event.KeyDown(sym=tcod.event.KeySym.ESCAPE):
            return {"quit": True}
        case tcod.event.KeyDown(sym=sym) if sym in MOVE_KEYS:
            return {"move": MOVE_KEYS[sym]}
    return {}


def _dispatch_player_dead(event: tcod.event.Event) -> dict[str, Any]:
    match event:
        case tcod.event.Quit():
            return {"quit": True}
        case tcod.event.KeyDown(sym=tcod.event.KeySym.ESCAPE):
            return {"quit": True}
    return {}


def dispatch(state: GameState, event: tcod.event.Event) -> dict[str, Any]:
    """Route an event to the handler for the current state."""
    match state:
        case GameState.PLAYER_DEAD:
            return _dispatch_player_dead(event)
        case _:
            # ENEMY_TURN never actually reaches here (the engine resolves it
            # synchronously in handle_action), but PLAYER_TURN does.
            return _dispatch_player_turn(event)