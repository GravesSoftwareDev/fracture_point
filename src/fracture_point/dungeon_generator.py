from __future__ import annotations

import random

from fracture_point.game_map import GameMap


class RectangularRoom:
    """A rectangular room defined by its top-left corner and size."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> tuple[int, int]:
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return center_x, center_y

    @property
    def inner(self) -> tuple[slice, slice]:
        """The floor area of the room, one tile in from each edge.

        Leaving the outermost ring uncarved means adjacent rooms/corridors
        don't accidentally merge into one shapeless blob - each room keeps
        a visible wall boundary unless a corridor deliberately punches
        through it.
        """
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def tunnel_between(start: tuple[int, int], end: tuple[int, int]):
    """Yield tile coordinates for an L-shaped corridor between two points.

    Randomly goes horizontal-then-vertical or vertical-then-horizontal,
    purely so corridors don't all look identical.
    """
    x1, y1 = start
    x2, y2 = end

    if random.random() < 0.5:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            yield x, y1
        for y in range(min(y1, y2), max(y1, y2) + 1):
            yield x2, y
    else:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            yield x1, y
        for x in range(min(x1, x2), max(x1, x2) + 1):
            yield x, y2


def generate_dungeon(
    map_width: int,
    map_height: int,
    max_rooms: int = 12,
    room_min_size: int = 6,
    room_max_size: int = 10,
) -> tuple[GameMap, list[RectangularRoom]]:
    """Build a dungeon out of randomly placed, non-overlapping rooms
    connected by corridors.

    Returns the finished GameMap plus the list of rooms in placement
    order, so the caller can decide what goes where (player in the
    first room, enemies in the rest, etc.) without this function needing
    to know anything about entities.
    """
    dungeon = GameMap(map_width, map_height, fill_value=False)
    rooms: list[RectangularRoom] = []

    for _ in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(1, map_width - room_width - 2)
        y = random.randint(1, map_height - room_height - 2)

        new_room = RectangularRoom(x, y, room_width, room_height)

        if any(new_room.intersects(other) for other in rooms):
            continue  # Overlaps an existing room - discard and try again.

        dungeon.tiles[new_room.inner] = True

        if rooms:
            prev_center = rooms[-1].center
            for tx, ty in tunnel_between(prev_center, new_room.center):
                dungeon.tiles[tx, ty] = True

        rooms.append(new_room)
    dungeon.stairs = rooms[-1].center
    return dungeon, rooms