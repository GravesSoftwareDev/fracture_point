import random

import tcod

from fracture_point.entity import Entity
from fracture_point.game_map import GameMap

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
                    took_turn = self.try_move_player(dx, dy)

                    # This is the core turn structure: the player's action
                    # only "counts" as a turn if it actually did something.
                    # Bumping into a wall shouldn't let enemies act for free.
                    if took_turn:
                        self.process_enemy_turns()

    def try_move_player(self, dx: int, dy: int) -> bool:
        dest_x = self.player.x + dx
        dest_y = self.player.y + dy

        if self.game_map.is_walkable(dest_x, dest_y):
            self.player.move(dx, dy)
            return True

        return False
        # Bumping a wall does nothing for now. Bumping an enemy will
        # become an attack once combat exists (next step or two).

    def process_enemy_turns(self) -> None:
        """Give every non-player entity a turn.

        Right now this just wanders enemies randomly, purely to prove
        the turn cadence works. Real enemy AI (chasing, attacking) comes
        once we have combat and stats in place.
        """
        for entity in self.game_map.entities:
            if entity is self.player:
                continue

            dx, dy = random.choice(list(MOVE_KEYS.values()))
            dest_x, dest_y = entity.x + dx, entity.y + dy

            if (dx, dy) != (0, 0) and self.game_map.is_walkable(dest_x, dest_y):
                entity.move(dx, dy)

    def render(self, console: tcod.console.Console) -> None:
        console.clear()

        for x in range(self.game_map.width):
            for y in range(self.game_map.height):
                char = "." if self.game_map.tiles[x, y] else "#"
                console.print(x=x, y=y, text=char, fg=(90, 90, 90))

        for entity in self.game_map.entities:
            console.print(x=entity.x, y=entity.y, text=entity.char, fg=entity.color)