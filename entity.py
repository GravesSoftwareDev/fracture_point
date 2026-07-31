from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.ai import HostileAI
    from components.fighter import Fighter

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
        self.blocks = blocks

        self.fighter = fighter
        self.ai = ai

        for componenet in (fighter, ai):
            if component is not None:

        