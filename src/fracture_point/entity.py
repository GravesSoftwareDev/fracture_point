from __future__ import annotations

from fracture_point.equipment import Equipment
from fracture_point.fighter import Fighter
from fracture_point.inventory import Inventory
from fracture_point.item import Item


class Entity:
    """A generic object on the map: player, enemy, item, etc."""

    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: tuple[int, int, int],
        name: str,
        blocks_movement: bool = False,
        fighter: Fighter | None = None,
        item: Item | None = None,
        inventory: Inventory | None = None,
        equipment: Equipment | None = None,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.fighter = fighter
        self.item = item
        self.inventory = inventory
        self.equipment = equipment

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy