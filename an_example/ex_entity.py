"""A plain entity with optional attached components (composition, not inheritance).

Nothing here knows what a "monster" or "item" is -- an Entity is just position +
appearance + whichever components it happens to hold. Behavior lives in the
components (Fighter, AI, ...), not in Entity subclasses. This is what lets a
monster later also carry an Inventory, or an item later also be a Fighter
(a hostile trap, say) without restructuring a class hierarchy.
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from an_example.ex_components.xai import HostileAI
    from an_example.ex_components.xfighter import Fighter


class Entity:
    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: tuple[int, int, int],
        name: str,
        *,
        blocks: bool = False,
        fighter: Fighter | None = None,
        ai: HostileAI | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks  # does this entity block movement into its tile?

        self.fighter = fighter
        self.ai = ai

        # Let each component reach back to the entity it's attached to,
        # e.g. so Fighter.attack() can read self.owner.name for messages.
        for component in (fighter, ai):
            if component is not None:
                component.owner = self

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def distance_to(self, other: "Entity") -> float:
        return math.hypot(other.x - self.x, other.y - self.y)