from __future__ import annotations

import tcod

from fracture_point.states.base import GameState

NUMBER_KEYS = {
    tcod.event.KeySym.N1: 0, tcod.event.KeySym.N2: 1, tcod.event.KeySym.N3: 2,
    tcod.event.KeySym.N4: 3, tcod.event.KeySym.N5: 4, tcod.event.KeySym.N6: 5,
    tcod.event.KeySym.N7: 6, tcod.event.KeySym.N8: 7, tcod.event.KeySym.N9: 8,
}


class InventoryState(GameState):
    """
    An overlay on top of Playing: browsing and equipping carried items.

    Equipping costs a turn (per the GDD); opening/closing this screen
    and browsing don't.
    """

    name = "inventory"
    linked_states = frozenset({"playing", "socketing"})

    def handle_event(self, event: tcod.event.Event) -> int | None:
        if not isinstance(event, tcod.event.KeyDown):
            return None

        engine = self.engine

        if event.sym == tcod.event.KeySym.ESCAPE:
            engine.states.pop()
            return None

        if event.sym == tcod.event.KeySym.S:
            engine.states.push("socketing")
            return None
        
        if event.sym in NUMBER_KEYS:
            index = NUMBER_KEYS[event.sym]
            if index < len(engine.player.inventory.items):
                item = engine.player.inventory.items[index]
                engine.equip_item(item)
                engine.states.pop()
                return engine.player.fighter.action_cost

        return None

    def render(self, map_console: tcod.console.Console, panel_console: tcod.console.Console) -> None:
        self.engine.render_map(map_console)
        self.engine.render_inventory(panel_console)