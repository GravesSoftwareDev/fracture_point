"""Combat stats and actions for any Entity that can fight (player or monster)."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from example_files.entity import Entity


class Fighter:
    def __init__(self, hp: int, defense: int, power: int) -> None:
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.owner: Entity | None = None  # set by Entity.__init__

    def take_damage(self, amount: int) -> list[dict[str, Any]]:
        """Apply damage and report results (a message, and death if hp hits 0)."""
        self.hp -= amount
        results: list[dict[str, Any]] = []
        if self.hp <= 0:
            results.append({"dead": self.owner})
        return results

    def attack(self, target: Entity) -> list[dict[str, Any]]:
        """Attack `target`. Returns a list of result dicts for the engine to process.

        Each engine action (move, attack, AI turn, ...) reports what happened as
        a list of small dicts (e.g. {"message": ...}, {"dead": entity}) instead of
        printing or mutating engine state directly. This keeps components ignorant
        of message logs, render state, or game-over handling -- the engine decides
        what a "death" or "message" *means*.
        """
        assert self.owner is not None
        assert target.fighter is not None
        damage = self.power - target.fighter.defense
        results: list[dict[str, Any]] = []
        if damage > 0:
            results.append({"message": f"{self.owner.name} attacks {target.name} for {damage} damage."})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({"message": f"{self.owner.name} attacks {target.name} but does no damage."})
        return results