from dataclasses import dataclass

def diminishing_bonus(stat_value: int, max_bonus: float, k: float) -> float:
    """
    Bonus fraction for a stat value, formula:
        Bonus = MaxBonus * (S / (S + k))

    Returns a fraction (0.5 means 50% bonus, 0.0 means no bonus, 1.0 means 100% bonus).
    Approaches max_bonus as stat_value increases and hits exactly half of max_bonus when stat_value = k.
    """

    if stat_value <= 0:
        return 0.0
    return max_bonus * (stat_value / (stat_value + k))

@dataclass
class Stats:
    """
    The Six core stats. Default values are 10, which is the average human baseline.
    """
    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    vitality: int = 10
    wisdom: int = 10
    luck: int = 10