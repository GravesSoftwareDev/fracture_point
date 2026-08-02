from __future__ import annotations

from fracture_point.item import Item
from fracture_point.gem import Gem

class Inventory:
    """
    A simple carried-items list. No weight/slot-count system yet.
    Just a capacity cap so it can't grow unbounded.
    """

    def __init__(self, capacity: int = 10, gem_capacity: int = 10):
        self.capacity = capacity
        self.items: list[Item] = []
        self.gem_capacity = gem_capacity
        self.gems: list[Gem] = []
        

    @property
    def is_full(self) -> bool:
        return len(self.items) >= self.capacity

    @property
    def gems_full(self) -> bool:
        return len(self.gems) >= self.gem_capacity

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