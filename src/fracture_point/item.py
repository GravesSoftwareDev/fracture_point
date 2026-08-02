from dataclasses import dataclass

@dataclass
class Item:
    """
    Something that can sit on the floor and be picked up.

    power_bonus/defense_bonus are flat additions to whatever slot this
    item occupies. `slot` controls which equipment slot it can go into.
    Only "weapon" does anything yet. "armor and "wand" are placeholders
    so Equipment doesn't need reshaping when those systems are built.
    """

    name: str
    char: str
    color: tuple[int, int, int]
    slot: str = "weapon" # "weapon" | "armor" | "wand" | "amulet" | "ring" | "earing"(only weapon is used right now)
    power_bonus: int = 0
    defense_bonus: int = 0
    
