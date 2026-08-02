from dataclasses import dataclass, field

@dataclass
class Item:
    """
    Something that can sit on the floor and be picked up.

    power_bonus/defense_bonus are flat additions to whatever slot this
    item occupies. `slot_type` lists every slot *category* this item can go into. Almost everything has exactly one entry. Dual-eligible items are rare special cases - e.g. an amulaet that can also sit in a chest slot. equip_item() will need to ask which one in these cases.
    """

    name: str
    char: str
    color: tuple[int, int, int]
    slot_types: list[str] = field(default_factory=lambda: ["weapon"])
    power_bonus: int = 0
    defense_bonus: int = 0

