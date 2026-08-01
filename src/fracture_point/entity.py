from __future__ import annotations

from fracture_point.fighter import Fighter


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
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.fighter = fighter

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy