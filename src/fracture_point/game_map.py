import numpy as np

from fracture_point.entity import Entity


class GameMap:
    """Holds the tile grid and entity list for one level.

    `tiles` is a 2D boolean array: True = walkable floor, False = wall.
    Indexed as tiles[x, y] to match how we address entities (x, y).
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = np.full((width, height), fill_value=True, dtype=bool)
        self.entities: list[Entity] = []

        # Wall off the border so nothing can walk off the map.
        self.tiles[0, :] = False
        self.tiles[width - 1, :] = False
        self.tiles[:, 0] = False
        self.tiles[:, height - 1] = False

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y) or not self.tiles[x, y]:
            return False
        # Can't walk into a tile occupied by a blocking entity.
        return not any(
            e.blocks_movement and e.x == x and e.y == y for e in self.entities
        )

    def get_blocking_entity_at(self, x: int, y: int) -> Entity | None:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == x and entity.y == y:
                return entity
        return None