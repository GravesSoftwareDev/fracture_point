import numpy as np

class GameMap:
    """
    Holds the tile grid for one level.

    `tiles` is a 2D boolean array: True = walkable, False = blocked.
    Indexed as tiles[x,y] to match how we address entities (x,y).
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = np.full((width, height), fill_value=True, order="F")

        # Wall off the border so the player can't walk off the map.
        self.tiles[0, :] = False
        self.tiles[width - 1, :] = False
        self.tiles[:, 0] = False
        self.tiles[:, height - 1] = False

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if (x,y) is inside the bounds of the map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        """Return True if (x,y) is inside the bounds of the map and walkable."""
        return self.in_bounds(x, y) and self.tiles[x, y]