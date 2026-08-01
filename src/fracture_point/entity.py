class Entity:
    """
    A generic object on the map: Player, Enemy, Item, etc.

    For now, this is intentionally bare-bones. Stats, gear, etc. will be added later.
    """

    def __init__(self, x: int, y: int, char: str, color: tuple[int, int, int], name: str = "<Unnamed>"):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name

    def move(self, dx: int, dy: int) -> None:
        """Move the entity by a given amount."""
        self.x += dx
        self.y += dy

    