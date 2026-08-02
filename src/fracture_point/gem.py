from dataclasses import dataclass

@dataclass
class Gem:
    """
    A socketable crystal. Right now every gem is an "active" ability tied to
    the bolt spell. This is just for scope. We'll add other variants later.

    """

    name: str
    char: str
    color: tuple[int, int, int]
    max_charge: int
    charge_per_turn: int
    cast_cost: int
    current_charge: int | None = None

    def __post_init__(self):
        if self.current_charge is None:
            self.current_charge = self.max_charge

    def regen(self) -> None:
        self.current_charge = min(self.max_charge, self.current_charge + self.charge_per_turn)

    def can_cast(self) -> bool:
        return self.current_charge >= self.cast_cost

    def consume(self) -> None:
        self.current_charge = max(0, self.current_charge - self.cast_cost)
    