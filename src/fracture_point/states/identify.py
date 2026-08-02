from __future__ import annotations

import tcod

from fracture_point.states.base import GameState

NUMBER_KEYS = {
    tcod.event.KeySym.N1: 0, tcod.event.KeySym.N2: 1, tcod.event.KeySym.N3: 2,
    tcod.event.KeySym.N4: 3, tcod.event.KeySym.N5: 4, tcod.event.KeySym.N6: 5,
    tcod.event.KeySym.N7: 6, tcod.event.KeySym.N8: 7, tcod.event.KeySym.N9: 8,
}


class IdentifyState(GameState):
    """
    Overlay: pick an unidentified item (equipped or carried) to reveal
    with a scroll. Only lists items whose identify_property isn't
    already known - once a property's known, the item just displays
    normally everywhere and won't show up here anymore.
    """

    name = "identify"
    linked_states = frozenset({"inventory"})

    def _unidentified_items(self) -> list:
        engine = self.engine
        candidates = []

        for item in engine.player.equipment.equipped.values():
            if item is not None and item.identify_property is not None and item.identify_property not in engine.known_properties:
                candidates.append(item)

        for item in engine.player.inventory.items:
            if item.identify_property is not None and item.identify_property not in engine.known_properties:
                candidates.append(item)

        return candidates

    def handle_event(self, event: tcod.event.Event) -> int | None:
        if not isinstance(event, tcod.event.KeyDown):
            return None

        engine = self.engine

        if event.sym == tcod.event.KeySym.ESCAPE:
            engine.states.pop()
            return None

        if event.sym in NUMBER_KEYS:
            items = self._unidentified_items()
            index = NUMBER_KEYS[event.sym]
            if index < len(items):
                engine.attempt_identify(items[index])
                engine.states.pop()
            return None

        return None

    def render(self, map_console: tcod.console.Console, panel_console: tcod.console.Console) -> None:
        self.engine.render_map(map_console)
        self.engine.render_identify(panel_console, self._unidentified_items())