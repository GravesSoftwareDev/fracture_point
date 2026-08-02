from __future__ import annotations

import tcod

from fracture_point.states.base import GameState

NUMBER_KEYS = {
    tcod.event.KeySym.N1: 0, tcod.event.KeySym.N2: 1, tcod.event.KeySym.N3: 2,
    tcod.event.KeySym.N4: 3, tcod.event.KeySym.N5: 4, tcod.event.KeySym.N6: 5,
    tcod.event.KeySym.N7: 6, tcod.event.KeySym.N8: 7, tcod.event.KeySym.N9: 8,
}

class SocketingState(GameState):
    """
    Two-step overlay: First choose which carried/equipped item to socket into
    (only items with an open socket are listed), then choose which carried gem to palce there.

    Will add swapping/removing at a later step
    """

    name = "socketing"
    linked_states = frozenset({"inventory"})

    def on_enter(self):
        self.step = "choose_item"
        self.selected_item = None

    def _socketable_items(self) -> list:
        """
        Every item (equipped or carried) that has at least one empty socket
        """

        engine = self.engine
        candidates = []

        for item in engine.player.equipment.equipped.values():
            if item is not None and item.empty_socket_index() is not None:
                candidates.append(item)

        for item in engine.player.inventory.items:
            if item.empty_socket_index() is not None:
                candidates.append(item)

        return candidates

    def handle_event(self, event: tcod.event.Event) -> int | None:
        if not isinstance(event, tcod.event.KeyDown):
            return None

        engine = self.engine

        if event.sym == tcod.event.KeySym.ESCAPE:
            if self.step == "choose_gem":
                self.step = "choose_ietm"
                self.selected_item = None
            else:
                engine.states.pop()
            return None

        if event.sym not in NUMBER_KEYS:
            return None

        index = NUMBER_KEYS[event.sym]

        if self.step == "choose_item":
            items = self._socketable_items()
            if index < len(items):
                self.selected_item = items[index]
                self.step = "choose_gem"
            return None

        if self.step == "choose_gem":
            gems = engine.player.inventory.gems
            if index < len(gems):
                gem = gems[index]
                engine.socket_gem(gem, self.selected_item)
                engine.states.pop()
            return None
        return None

    def render(self, map_console: tcod.console.Console, panel_console: tcod.console.Console):
        self.engine.render_map(map_console)
        self.engine.render_socketing(panel_console, self.step, self._socketable_items())