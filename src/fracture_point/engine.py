import random
import textwrap

import tcod

from fracture_point.entity import Entity
from fracture_point.game_map import GameMap
from fracture_point.message_log import MessageLog
from fracture_point.turn_queue import TurnQueue

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

FOV_RADIUS = 8


class Engine:
    def __init__(self, game_map: GameMap, player: Entity, sidebar_width: int = 24):
        self.game_map = game_map
        self.player = player
        self.log = MessageLog()

        self.sidebar_width = sidebar_width
        self.border_x = self.game_map.width
        self.sidebar_x = self.border_x + 1

        # Every entity starts scheduled at time 0. Order among them at
        # the same time is just insertion order (see TurnQueue), which
        # is fine - it only matters who's *fastest going forward*, not
        # who technically goes first on turn zero.
        self.turn_queue = TurnQueue()
        for entity in self.game_map.entities:
            self.turn_queue.schedule(entity, 0)

        self.update_fov()

    def update_fov(self) -> None:
        self.game_map.visible[:] = tcod.map.compute_fov(
            transparency=self.game_map.tiles,
            pov=(self.player.x, self.player.y),
            radius=FOV_RADIUS,
        )
        self.game_map.explored |= self.game_map.visible

    def run(self, console: tcod.console.Console, context: tcod.context.Context) -> None:
        """Main game loop: pop whoever's next in the turn queue and let
        them act, then reschedule them based on their own action_cost.

        We only render/present right before the player's turn - enemy
        actions between player turns happen "silently" and their results
        just show up the next time we render, same as the old
        all-enemies-move-at-once behavior, just now spread across
        individually-timed turns instead of a single batch.
        """
        while True:
            entity, time = self.turn_queue.pop_next()

            if entity.fighter is None:
                continue  # Dead (or fighter-less) entities drop out permanently.

            if entity is self.player:
                self.render(console)
                context.present(console)
                cost = self.await_player_action()
            else:
                cost = self.take_enemy_action(entity)

            self.turn_queue.schedule(entity, time + cost)

    def await_player_action(self) -> int:
        """Block until the player takes a valid action, then return its
        tick cost. Invalid inputs (unrecognized keys, bumping a wall)
        loop back around without costing a turn.
        """
        while True:
            for event in tcod.event.wait():
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()

                if isinstance(event, tcod.event.KeyDown):
                    if event.sym == tcod.event.KeySym.ESCAPE:
                        raise SystemExit()

                    if event.sym in MOVE_KEYS:
                        dx, dy = MOVE_KEYS[event.sym]
                        took_turn = self.player_action(dx, dy)

                        if took_turn:
                            self.update_fov()
                            return self.player.fighter.action_cost

    def player_action(self, dx: int, dy: int) -> bool:
        dest_x, dest_y = self.player.x + dx, self.player.y + dy

        target = self.game_map.get_blocking_entity_at(dest_x, dest_y)
        if target is not None:
            self.attack(self.player, target)
            return True

        if self.game_map.is_walkable(dest_x, dest_y):
            self.player.move(dx, dy)
            return True

        return False

    def take_enemy_action(self, entity: Entity) -> int:
        """Simple AI: attack the player if adjacent, otherwise wander.
        Real pathing/behavior differences per enemy type come later.
        """
        dist_x = abs(entity.x - self.player.x)
        dist_y = abs(entity.y - self.player.y)
        is_adjacent = dist_x <= 1 and dist_y <= 1 and (dist_x + dist_y) > 0

        if is_adjacent and self.player.fighter.is_alive:
            self.attack(entity, self.player)
        else:
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)])
            dest_x, dest_y = entity.x + dx, entity.y + dy
            if (dx, dy) != (0, 0) and self.game_map.is_walkable(dest_x, dest_y):
                entity.move(dx, dy)

        return entity.fighter.action_cost

    def attack(self, attacker: Entity, defender: Entity) -> None:
        raw_damage = max(0, attacker.fighter.power - defender.fighter.defense)
        damage = round(raw_damage * (1 - defender.fighter.damage_reduction))

        if damage > 0:
            self.log.add(f"{attacker.name} hits {defender.name} for {damage}.")
            defender.fighter.take_damage(damage)
        else:
            self.log.add(f"{attacker.name} hits {defender.name} but does no damage.")

        if not defender.fighter.is_alive:
            self.die(defender)

    def die(self, entity: Entity) -> None:
        self.log.add(f"{entity.name} dies!")
        entity.blocks_movement = False
        entity.char = "%"
        entity.color = (120, 30, 30)
        entity.fighter = None

        if entity is self.player:
            self.log.add("You died. Press any key to exit.")
            for event in tcod.event.wait():
                if isinstance(event, tcod.event.KeyDown):
                    raise SystemExit()

    def render(self, console: tcod.console.Console) -> None:
        console.clear()
        self.render_map(console)
        self.render_border(console)
        self.render_sidebar(console)

    def render_map(self, console: tcod.console.Console) -> None:
        gm = self.game_map

        for x in range(gm.width):
            for y in range(gm.height):
                if not gm.explored[x, y]:
                    color = (50, 10, 40)
                    base_char = "|"
                else:
                    base_char = "." if gm.tiles[x, y] else "#"

                if gm.visible[x, y]:
                    color = (200, 200, 200) if gm.tiles[x, y] else (130, 130, 130)
                elif gm.explored[x, y]:
                    color = (60, 60, 60) if gm.tiles[x, y] else (40, 40, 40)

                console.print(x=x, y=y, text=base_char, fg=color)

        for entity in gm.entities:
            if gm.visible[entity.x, entity.y]:
                console.print(x=entity.x, y=entity.y, text=entity.char, fg=entity.color)
            if entity is not self.player and entity.fighter is None:
                console.print(x=entity.x, y=entity.y, text=entity.char, fg=entity.color)

    def render_border(self, console: tcod.console.Console) -> None:
        for y in range(console.height):
            console.print(x=self.border_x, y=y, text="│", fg=(90, 90, 90))

    def render_sidebar(self, console: tcod.console.Console) -> None:
        x = self.sidebar_x
        y = 1

        console.print(x=x, y=y, text="Fracture Point", fg=(255, 255, 255))
        y += 2

        if self.player.fighter is not None:
            hp_text = f"HP: {self.player.fighter.hp}/{self.player.fighter.max_hp}"
            console.print(x=x, y=y, text=hp_text, fg=(255, 255, 255))
        y += 2

        console.print(x=x, y=y, text="── Log ──", fg=(120, 120, 120))
        y += 1

        wrapped_lines: list[str] = []
        for message in self.log.messages:
            wrapped_lines.extend(textwrap.wrap(message, width=self.sidebar_width))

        max_lines = console.height - y - 1
        for line in wrapped_lines[-max_lines:]:
            console.print(x=x, y=y, text=line, fg=(200, 200, 200))
            y += 1