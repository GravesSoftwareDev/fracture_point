from __future__ import annotations

import tcod

from fracture_point.states.base import GameState

NUMBER_KEYS = {
    tcod.event.KeySym.N1: 0, tcod.event.KeySym.N2: 1, tcod.event.KeySym.N3: 2,
    tcod.event.KeySym.N4: 3, tcod.event.KeySym.N5: 4, tcod.event.KeySym.N6: 5,
    tcod.event.KeySym.N7: 6, tcod.event.KeySym.N8: 7, tcod.event.KeySym.N9: 8,
}


class UnequipState(GameState):
    """
    Overlay: lists every currently FILLED equipment slot (weapon,
    armor, rings, wand, etc.) and lets the player pick one to remove.
    Replaces the old behavior where 'u' only ever unequipped the
    weapon slot - that was a leftover from before jewelry/armor slots
    existed, never generalized until now.

    Free action, no turn cost - same rule as unequipping has always
    followed (removing gear is free; only equipping costs a turn).
    """

    name = "unequip"
    linked_states = frozenset({"inventory"})

    def _equipped_slots(self) -> list[tuple[str, object]]:
        return [
            (slot_id, item)
            for slot_id, item in self.engine.player.equipment.equipped.items()
            if item is not None
        ]

    def handle_event(self, event: tcod.event.Event) -> int | None:
        if not isinstance(event, tcod.event.KeyDown):
            return None

        engine = self.engine

        if event.sym == tcod.event.KeySym.ESCAPE:
            engine.states.pop()
            return None

        if event.sym in NUMBER_KEYS:
            slots = self._equipped_slots()
            index = NUMBER_KEYS[event.sym]
            if index < len(slots):
                slot_id, _item = slots[index]
                engine.unequip_slot(slot_id)
                engine.states.pop()
            return None

        return None

    def render(self, map_console: tcod.console.Console, panel_console: tcod.console.Console) -> None:
        self.engine.render_map(map_console)
        self.engine.render_unequip(panel_console, self._equipped_slots())