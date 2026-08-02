from dataclasses import dataclass, field


@dataclass
class Item:
    """
    Something that can sit on the floor and be picked up.

    slot_types lists every slot *category* this item can go into.
    power_bonus is melee power (weapons); magic_power_bonus is magic
    power (wands); defense_bonus applies to armor/jewelry against
    physical damage. Magic resist isn't gear-driven yet - it's purely
    an Intelligence-derived stat for now (see Fighter).
    """

    name: str
    char: str
    color: tuple[int, int, int]
    slot_types: list[str] = field(default_factory=lambda: ["weapon"])
    power_bonus: int = 0
    magic_power_bonus: int = 0
    defense_bonus: int = 0