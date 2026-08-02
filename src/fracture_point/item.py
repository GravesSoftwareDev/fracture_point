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

    Identify only affects what's *displayed*, not what the item *does*
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
    base_name: str = ""
    identify_property: str | None = None

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
        return None\

    def is_identified(self, known_properties: set[str]) -> bool:
        return self.identify_property is None or self.identify_property in known_properties

    def display_name(self, known_properties: set[str]) -> str:
        if self.is_identified(known_properties):
            return self.name
        return f"Unidentified {self.base_name or self.name}"

    def inventory_label(self, known_properties: set[str]) -> str:
        """
        A one-line summary for menus: name plus stats if identified, or
        '(unidentified)' marker with stats hidden if not.
        """
        name = self.display_name(known_properties)

        if not self.is_identified(known_properties):
            return f"{name} (properties unknown)"

        stats = []
        if self.power_bonus:
            stats.append(f"={self.power_bonus} pwr")
        if self.magic_power_bonus:
            stats.append(f"+{self.magic_power_bonus} mag")
        if self.defense_bonus:
            stats.append(f"+{self.defense_bonus} def")

        return f"{name} ({','.join(stats)})" if stats else name