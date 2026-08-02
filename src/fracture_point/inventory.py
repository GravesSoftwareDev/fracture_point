from __future__ import annotations

from fracture_point.consumable import Consumable
from fracture_point.gem import Gem
from fracture_point.item import Item


class Inventory:
    """Carried items, loose gems, and consumables - three separate
    lists since each is handled completely differently (equipping,
    socketing, using-and-removing)."""

    def __init__(self, capacity: int = 10, gem_capacity: int = 10, consumable_capacity: int = 10):
        self.capacity = capacity
        self.items: list[Item] = []
        self.gem_capacity = gem_capacity
        self.gems: list[Gem] = []
        self.consumable_capacity = consumable_capacity
        self.consumables: list[Consumable] = []

    @property
    def is_full(self) -> bool:
        return len(self.items) >= self.capacity

    @property
    def gems_full(self) -> bool:
        return len(self.gems) >= self.gem_capacity

    @property
    def consumables_full(self) -> bool:
        return len(self.consumables) >= self.consumable_capacity

    def add(self, item: Item) -> bool:
        if self.is_full:
            return False
        self.items.append(item)
        return True

    def remove(self, item: Item) -> None:
        self.items.remove(item)

    def add_gem(self, gem: Gem) -> bool:
        if self.gems_full:
            return False
        self.gems.append(gem)
        return True

    def remove_gem(self, gem: Gem) -> None:
        self.gems.remove(gem)

    def add_consumable(self, consumable: Consumable) -> bool:
        if self.consumables_full:
            return False
        self.consumables.append(consumable)
        return True

    def remove_consumable(self, consumable: Consumable) -> None:
        self.consumables.remove(consumable)