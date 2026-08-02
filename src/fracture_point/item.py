from dataclasses import dataclass, field

from fracture_point.gem import Gem

@dataclass
class Item:
    """
    Something that can sit on the floor and be picked up.

    slot_types lists every slot *category* this item can go into.
    power_bonus is melee power (weapons); magic_power_bonus is magic
    power (wands); defense_bonus applies to armor/jewelry against
    physical damage. Magic resist isn't gear-driven yet - it's purely
    an Intelligence-derived stat for now (see Fighter).
    """

    name: str
    char: str
    color: tuple[int, int, int]
    slot_types: list[str] = field(default_factory=lambda: ["weapon"])
    power_bonus: int = 0
    magic_power_bonus: int = 0
    defense_bonus: int = 0
    gem_slots: int = 0
    sockets: list[Gem | None] = field(default_factory=list)

    def __post_init__(self):
        if not self.sockets:
            self.sockets = [None] * self.gem_slots

    def socketed_active_gem(self) -> Gem | None:
        """
        First non-empty socket. Fine while items only ever have one meaningful socket - revisit when expanding socketing system.
        """

        for gem in self.sockets:
            if gem is not None:
                return gem

        return None

    def empty_socket_index(self) -> int | None:
        """
        Index of the first empty socket, or None if the item has no empty
        sockets.
        """
        for i, gem in enumerate(self.sockets):
            if gem is None:
                return i
        return None