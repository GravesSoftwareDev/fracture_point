from fracture_point.stats import Stats, diminishing_bonus


class Fighter:
    """
    Combat stats for an entity that can fight. (Player, Enemy, Trap, etc.)

    Power/Max_hp/Defense are *derived*: a base number (standing in for whatever 
    weapon/armor is equipped, once gear exists) modified by the entity's stats.
    """
    STRENGTH_DAMAGE_MAX_BONUS = 1.5
    STRENGTH_DAMAGE_K = 40
    STRENGTH_MITIGATION_MAX_BONUS = 0.5
    STRENGTH_MITIGATION_K = 60

    HP_PER_VITALITY = 1

    def __init__(self, stats: Stats, base_power: int, base_defense: int, base_max_hp: int):
            self.stats = stats
            self.base_power = base_power
            self.base_defense = base_defense
            self.base_max_hp = base_max_hp
            self.hp = self.max_hp

    @property
    def power(self) -> int:
        """
        Power is the base power modified by the strength stat.
        """
        bonus = diminishing_bonus(self.stats.strength, self.STRENGTH_DAMAGE_MAX_BONUS, self.STRENGTH_DAMAGE_K)
        return round(self.base_power * (1 + bonus))

    @property
    def defense(self) -> int:
        """
        Defense is the base defense modified by the strength stat.
        """
        return self.base_defense

    @property
    def damage_reduction(self) -> float:
        """
        Damage reduction is a fraction of damage mitigated, based on the strength stat.
        """
        return diminishing_bonus(self.stats.strength, self.STRENGTH_MITIGATION_MAX_BONUS, self.STRENGTH_MITIGATION_K)

    @property
    def max_hp(self) -> int:
        """
        Max HP is the base max HP modified by the vitality stat.
        """
        return self.base_max_hp + (self.stats.vitality * self.HP_PER_VITALITY)
    
    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp < 0: # Ensure hp doesn't go below 0
            self.hp = 0