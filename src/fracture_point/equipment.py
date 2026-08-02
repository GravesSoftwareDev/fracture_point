from __future__ import annotations

from fracture_point.fighter import Fighter
from fracture_point.item import Item


class Equipment:
    """
    Named equipment slots, per the GDD's slot-based gear system.

    Slots are stored as data (slot_id -> category, slot_id -> equipped
    Item) rather than fixed attributes, specifically so new slots can
    be granted at runtime (e.g. a third ring slot unlocked by a
    Strength threshold, or extra earring slots) without changing this
    class's shape.

    Only "weapon" and armor/jewelry categories affecting power/defense
    are functional. "wand" is a stub category, unused until magic exists.
    """

    # (slot_id, category) - the starting slot layout. Category is what
    # an Item's slot_types are checked against.
    DEFAULT_SLOTS = [
        ("weapon", "weapon"),
        ("head", "head"),
        ("chest", "chest"),
        ("hands", "hands"),
        ("legs", "legs"),
        ("feet", "feet"),
        ("ring_1", "ring"),
        ("ring_2", "ring"),
        ("amulet", "amulet"),
        ("bracelet", "bracelet"),
        ("earrings", "earrings"),
        ("wand", "wand"),  # stub, unused until magic exists
    ]

    def __init__(self, fighter: Fighter):
        self.fighter = fighter
        self.slot_category: dict[str, str] = dict(self.DEFAULT_SLOTS)
        self.equipped: dict[str, Item | None] = {slot_id: None for slot_id, _ in self.DEFAULT_SLOTS}

    def add_slot(self, slot_id: str, category: str) -> None:
        """Grants a new slot at runtime - e.g. a third ring slot from a
        Strength threshold, or a bonus earring slot. slot_id must be
        unique (so a third ring slot might be 'ring_3')."""
        if slot_id in self.slot_category:
            raise ValueError(f"Slot '{slot_id}' already exists.")
        self.slot_category[slot_id] = category
        self.equipped[slot_id] = None

    def empty_slots_for(self, item: Item) -> list[str]:
        """Every currently-empty slot_id whose category matches one of
        this item's slot_types. Usually 0 or 1 result; more than 1 means
        either multiple same-category slots are open (e.g. both rings
        free) or the item is dual-eligible across categories - either
        way, the caller needs to ask the player which one to use."""
        return [
            slot_id
            for slot_id, category in self.slot_category.items()
            if category in item.slot_types and self.equipped[slot_id] is None
        ]

    def equip(self, item: Item, slot_id: str) -> Item | None:
        """Equips item into a specific slot_id, returning whatever was
        previously there (or None). Caller is responsible for choosing
        slot_id (typically via empty_slots_for) and for putting the
        returned item back into inventory."""
        if slot_id not in self.slot_category:
            raise ValueError(f"No such slot: '{slot_id}'")
        if self.slot_category[slot_id] not in item.slot_types:
            raise ValueError(f"{item.name} can't go in slot '{slot_id}'.")

        previous = self.equipped[slot_id]

        if previous is not None:
            self._apply_bonus(previous, sign=-1)

        self.equipped[slot_id] = item
        self._apply_bonus(item, sign=+1)

        return previous

    def unequip(self, slot_id: str) -> Item | None:
        previous = self.equipped.get(slot_id)
        if previous is not None:
            self._apply_bonus(previous, sign=-1)
            self.equipped[slot_id] = None
        return previous

    def _apply_bonus(self, item: Item, sign: int) -> None:
        self.fighter.equipment_power_bonus += sign * item.power_bonus
        self.fighter.equipment_defense_bonus += sign * item.defense_bonus
        self.fighter.equipment_magic_power_bonus += sign * item.magic_power_bonus
