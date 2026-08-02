from __future__ import annotations
from fracture_point.item import Item

class Inventory:
    """
    A simple carried-items list. No weight/slot-count system yet.
    Just a capacity cap so it can't grow unbounded.
    """

    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        self.items: list[Item] = []

    @property
    def is_full(self) -> bool:
        return len(self.items) >= self.capacity

    def add(self, item: Item) -> bool:
        if self.is_full:
            return False
        self.items.append(item)
        return True

    def remove(self, item: Item) -> None:
        self.items.remove(item)