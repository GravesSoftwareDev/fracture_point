import tcod

from fracture_point.entity import Entity
from fracture_point.game_map import GameMap

# Move keys -> (dx, dy). Arrow keys plus WASD for now; we can expand
# this later (vi keys, rebinding, etc.) once input handling needs it.
MOVE_KEYS = {
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.W: (0, -1),
    tcod.event.KeySym.S: (0, 1),
    tcod.event.KeySym.A: (-1, 0),
    tcod.event.KeySym.D: (1, 0),
}


class Engine:
    def __init__(self, game_map: GameMap, player: Entity):
        self.game_map = game_map
        self.player = player

    def handle_events(self) -> None:
        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                raise SystemExit()

            if isinstance(event, tcod.event.KeyDown):
                if event.sym in MOVE_KEYS:
                    dx, dy = MOVE_KEYS[event.sym]
                    self.try_move_player(dx, dy)

    def try_move_player(self, dx: int, dy: int) -> None:
        dest_x = self.player.x + dx
        dest_y = self.player.y + dy

        if self.game_map.is_walkable(dest_x, dest_y):
            self.player.move(dx, dy)
        # If it's not walkable, we just do nothing for now.
        # This is where a "bump into wall" message/sound would go later.

    def render(self, console: tcod.console.Console) -> None:
        console.clear()

        # Draw the map: '#' for wall, '.' for floor.
        for x in range(self.game_map.width):
            for y in range(self.game_map.height):
                char = "." if self.game_map.tiles[x, y] else "#"
                console.print(x=x, y=y, text=char, fg=(90, 90, 90))

        # Draw the player on top.
        console.print(x=self.player.x, y=self.player.y, text=self.player.char, fg=self.player.color)