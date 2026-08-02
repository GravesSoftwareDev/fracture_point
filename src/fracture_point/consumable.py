from dataclasses import dataclass

@dataclass
class Consumable:
    """
    A single-use item, distinct from equippable items. It gets used up and removed. Starting with the indentify object, but later will add things like potions and what not.
    """

    name: str
    char: str
    color: tuple[int,int,int]
    kind: str = "identify"