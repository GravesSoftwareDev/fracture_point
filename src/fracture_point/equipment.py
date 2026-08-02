from __future__ import annotations

from fracture_point.fighter import Fighter
from fracture_point.item import Item


class Equipment:
    """
    Fixed equipment slots, per the GDD's slot-based gear system.

    Only `weapon` is functional right now. `armor` and `wand` exist as
    placeholders so this class's shape doesn't need to change once
    those systems (armor mitigation, magic casting) get designed - they
    just start actually being read from somewhere once that happens.

    Equipping/unequipping directly pushes power_bonus/defense_bonus onto
    the linked Fighter, which folds them into its derived power/defense
    the same way base_power/base_defense already work.
    """

    def __init__(self, fighter: Fighter):
        self.fighter = fighter
        self.weapon: Item | None = None
        self.armor: Item | None = None  # not used yet
        self.wand: Item | None = None   # not used yet

    def equip_weapon(self, item: Item) -> Item | None:
        """Equips item into the weapon slot, returning whatever was
        previously equipped there (or None), so the caller can put it
        back in the inventory."""
        previous = self.weapon

        if previous is not None:
            self.fighter.equipment_power_bonus -= previous.power_bonus

        self.weapon = item
        self.fighter.equipment_power_bonus += item.power_bonus

        return previous

    def unequip_weapon(self) -> Item | None:
        previous = self.weapon
        if previous is not None:
            self.fighter.equipment_power_bonus -= previous.power_bonus
            self.weapon = None
        return previous