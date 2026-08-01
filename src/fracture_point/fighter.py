class Fighter:
    """
    Combat stats for an entity that can fight. (Player, Enemy, Trap, etc.)

    Deliberately simple for now. Flat power/defense numbers. Once the stat system
    and gear bonuses exist, this is where their combined effects will be calculated.
    """

    def __init__(self, power: int, defense: int, max_hp: int):
        self.power = power
        self.defense = defense
        self.max_hp = max_hp
        self.hp = max_hp

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp < 0: # Ensure hp doesn't go below 0
            self.hp = 0