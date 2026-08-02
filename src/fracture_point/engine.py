import random
import textwrap

import tcod

from fracture_point.entity import Entity
from fracture_point.game_map import GameMap
from fracture_point.message_log import MessageLog
from fracture_point.turn_queue import TurnQueue
from fracture_point.states.state_manager import StateManager
from fracture_point.states.playing import PlayingState
from fracture_point.states.inventory import InventoryState
from fracture_point.pathfinding import compute_path

FOV_RADIUS = 8


class Engine:
    def __init__(self, game_map: GameMap, player: Entity, panel_width: int = 32):
        self.game_map = game_map
        self.player = player
        self.log = MessageLog()

        # The map and side panel are now fully independent consoles,
        # composited together in render(). This replaces the old
        # shared-console-plus-manual-x-offset approach, and lets the
        # panel draw its own frame/title so it reads as its own window.
        self.map_console = tcod.console.Console(self.game_map.width, self.game_map.height, order="F")
        self.panel_width = panel_width
        self.panel_console = tcod.console.Console(panel_width, self.game_map.height, order="F")

        self.turn_queue = TurnQueue()
        for entity in self.game_map.entities:
            self.turn_queue.schedule(entity, 0)

        self.states = StateManager()
        self.states.register(PlayingState(self))
        self.states.register(InventoryState(self))
        self.states.start("playing")

        self.update_fov()

    def update_fov(self) -> None:
        self.game_map.visible[:] = tcod.map.compute_fov(
            transparency=self.game_map.tiles,
            pov=(self.player.x, self.player.y),
            radius=FOV_RADIUS,
        )
        self.game_map.explored |= self.game_map.visible

    def run(self, console: tcod.console.Console, context: tcod.context.Context) -> None:
        while True:
            entity, time = self.turn_queue.pop_next()

            if entity.fighter is None:
                continue

            if entity is self.player:
                cost = self.await_player_turn(console, context)
            else:
                cost = self.take_enemy_action(entity)

            self.turn_queue.schedule(entity, time + cost)

    def await_player_turn(self, console: tcod.console.Console, context: tcod.context.Context) -> int:
        while True:
            self.render(console)
            context.present(console)

            for event in tcod.event.wait():
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()

                cost = self.states.current.handle_event(event)
                if cost is not None:
                    return cost

                break

    def try_pickup(self) -> bool:
        target = self.game_map.get_item_at(self.player.x, self.player.y)
        if target is None:
            self.log.add("There's nothing here to pick up.")
            return False

        if self.player.inventory.is_full:
            self.log.add("Your inventory is full.")
            return False

        self.player.inventory.add(target.item)
        self.log.add(f"You pick up {target.item.name}.")
        self.game_map.entities.remove(target)
        return True

    def equip_item(self, item) -> None:
        candidate_slots = self.player.equipment.empty_slots_for(item)

        if not candidate_slots:
            self.log.add(f"No open slot for {item.name}.")
            return

        slot_id = candidate_slots[0]
        previous = self.player.equipment.equip(item, slot_id)
        self.player.inventory.remove(item)

        if previous is not None:
            self.player.inventory.add(previous)
            self.log.add(f"You equip {item.name} ({slot_id}), stowing {previous.name}.")
        else:
            self.log.add(f"You equip {item.name} ({slot_id}).")

    def unequip_slot(self, slot_id: str) -> None:
        previous = self.player.equipment.unequip(slot_id)
        if previous is None:
            self.log.add(f"Nothing equipped in {slot_id}.")
            return

        if not self.player.inventory.add(previous):
            self.player.equipment.equip(previous, slot_id)
            self.log.add("No room in your inventory to unequip that.")
            return

        self.log.add(f"You unequip {previous.name} ({slot_id}).")

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
        """
        Attack if adjacent. Otherwise, check whether this entity can
        currently see the player (its own FOV, from its own position,
        using its own perception_radius) - if so, path toward the
        player. If not, fall back to the old random wander so
        not-yet-aggroed enemies still feel alive rather than frozen.
        """
        dist_x = abs(entity.x - self.player.x)
        dist_y = abs(entity.y - self.player.y)
        is_adjacent = dist_x <= 1 and dist_y <= 1 and (dist_x + dist_y) > 0

        if is_adjacent and self.player.fighter.is_alive:
            self.attack(entity, self.player)
            return entity.fighter.action_cost

        can_see_player = tcod.map.compute_fov(
            transparency=self.game_map.tiles,
            pov=(entity.x, entity.y),
            radius=entity.perception_radius,
        )[self.player.x, self.player.y]

        if can_see_player:
            path = compute_path(self.game_map, (entity.x, entity.y), (self.player.x, self.player.y))
            if path:
                next_x, next_y = path[0]
                if self.game_map.is_walkable(next_x, next_y):
                    entity.move(next_x - entity.x, next_y - entity.y)
                # If the next path tile is blocked (another entity is
                # standing there), the enemy just waits this turn rather
                # than trying to path around - fine for now with small
                # enemy counts; worth revisiting if enemies ever cluster.
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
        """
        Composites the map and panel consoles onto the actual screen
        console. Each sub-console is cleared and redrawn by the current
        state, then blitted side by side - map on the left, panel on
        the right.
        """
        self.map_console.clear()
        self.panel_console.clear()

        self.states.current.render(self.map_console, self.panel_console)

        console.clear()
        self.map_console.blit(console, dest_x=0, dest_y=0)
        self.panel_console.blit(console, dest_x=self.map_console.width, dest_y=0)

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
            if entity is not self.player and entity.fighter is None and entity.item is None:
                console.print(x=entity.x, y=entity.y, text=entity.char, fg=entity.color)

    def render_sidebar(self, console: tcod.console.Console) -> None:
        console.draw_frame(
            x=0, y=0, width=console.width, height=console.height,
            title="Fracture Point", fg=(180, 180, 180), bg=(0, 0, 0),
        )

        x, y = 2, 2

        if self.player.fighter is not None:
            hp_text = f"HP: {self.player.fighter.hp}/{self.player.fighter.max_hp}"
            console.print(x=x, y=y, text=hp_text, fg=(255, 255, 255))
        y += 1

        weapon = self.player.equipment.equipped["weapon"]
        weapon_name = weapon.name if weapon else "(none)"
        console.print(x=x, y=y, text=f"Weapon: {weapon_name}", fg=(180, 180, 220))
        y += 1

        console.print(x=x, y=y, text="[i]nv  [g]et  [u]nequip", fg=(120, 120, 120))
        y += 2

        console.print(x=x, y=y, text="── Log ──", fg=(120, 120, 120))
        y += 1

        content_width = console.width - 4  # inset from the frame on both sides
        wrapped_lines: list[str] = []
        for message in self.log.messages:
            wrapped_lines.extend(textwrap.wrap(message, width=content_width))

        max_lines = console.height - y - 2  # leave room for the frame's bottom edge
        for line in wrapped_lines[-max_lines:]:
            console.print(x=x, y=y, text=line, fg=(200, 200, 200))
            y += 1

    def render_inventory(self, console: tcod.console.Console) -> None:
        console.draw_frame(
            x=0, y=0, width=console.width, height=console.height,
            title="Inventory", fg=(180, 180, 180), bg=(0, 0, 0),
        )

        x, y = 2, 2

        if not self.player.inventory.items:
            console.print(x=x, y=y, text="(empty)", fg=(150, 150, 150))
        else:
            for i, item in enumerate(self.player.inventory.items):
                line = f"{i + 1}. {item.name} (+{item.power_bonus} pwr)"
                console.print(x=x, y=y, text=line, fg=item.color)
                y += 1

        y += 1
        console.print(x=x, y=y, text="[esc] back", fg=(120, 120, 120))