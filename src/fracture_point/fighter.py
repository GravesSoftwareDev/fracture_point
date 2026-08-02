from __future__ import annotations

from fracture_point.stats import Stats, diminishing_bonus


class Fighter:
    """
    Combat stats for an entity that can fight. (Player, Enemy, Trap, etc.)

    power/max_hp/damage_reduction/action_cost are *derived*: a base
    number modified by Stats via the diminishing-returns curve, plus
    flat bonuses from equipped gear (equipment_power_bonus/
    equipment_defense_bonus), written to directly by Equipment.
    """

    STRENGTH_DAMAGE_MAX_BONUS = 1.5
    STRENGTH_DAMAGE_K = 40
    STRENGTH_MITIGATION_MAX_BONUS = 0.5
    STRENGTH_MITIGATION_K = 60

    INTELLIGENCE_DAMAGE_MAX_BONUS = 1.5
    INTELLIGENCE_DAMAGE_K = 40
    INTELLIGENCE_RESIST_MAX_BONUS = 0.5
    INTELLIGENCE_RESIST_K = 60

    HP_PER_VITALITY = 1

    BASE_ACTION_COST = 100
    DEXTERITY_SPEED_MAX_BONUS = 0.8
    DEXTERITY_SPEED_K = 40

    def __init__(
        self,
        stats: Stats,
        base_power: int,
        base_defense: int,
        base_max_hp: int,
        base_magic_power: int=0,
        base_magic_resist: int=0,
    ):
        self.stats = stats
        self.base_power = base_power
        self.base_defense = base_defense
        self.base_max_hp = base_max_hp
        self.base_magic_power = base_magic_power
        self.base_magic_resist = base_magic_resist

        self.equipment_power_bonus = 0
        self.equipment_defense_bonus = 0
        self.equipment_magic_power_bonus = 0

        self.hp = self.max_hp


    @property
    def power(self) -> int:
        bonus = diminishing_bonus(
            self.stats.strength, self.STRENGTH_DAMAGE_MAX_BONUS, self.STRENGTH_DAMAGE_K
        )
        return round((self.base_power + self.equipment_power_bonus) * (1 + bonus))

    @property
    def defense(self) -> int:
        return self.base_defense + self.equipment_defense_bonus

    @property
    def damage_reduction(self) -> float:
        return diminishing_bonus(
            self.stats.strength, self.STRENGTH_MITIGATION_MAX_BONUS, self.STRENGTH_MITIGATION_K
        )

    @property
    def magic_power(self) -> int:
        bonus = diminishing_bonus(
            self.stats.intelligence, self.INTELLIGENCE_DAMAGE_MAX_BONUS, self.INTELLIGENCE_DAMAGE_K
        )
        return round((self.base_magic_power + self.equipment_magic_power_bonus) * (1 + bonus))

    @property
    def magic_resist(self) ->float:
        """
        Fraction of incoming magic damage negated. Purely stat driven for now.
        """
        return diminishing_bonus(
            self.stats.intelligence, self.INTELLIGENCE_RESIST_MAX_BONUS, self.INTELLIGENCE_RESIST_K
        )

    @property
    def max_hp(self) -> int:
        return self.base_max_hp + self.stats.vitality * self.HP_PER_VITALITY

    @property
    def action_cost(self) -> int:
        bonus = diminishing_bonus(
            self.stats.dexterity, self.DEXTERITY_SPEED_MAX_BONUS, self.DEXTERITY_SPEED_K
        )
        return round(self.BASE_ACTION_COST / (1 + bonus))

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0