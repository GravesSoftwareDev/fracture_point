import random
import textwrap

import tcod

from fracture_point.entity import Entity
from fracture_point.game_map import GameMap
from fracture_point.message_log import MessageLog
from fracture_point.turn_queue import TurnQueue
from fracture_point import save_data
from fracture_point.pathfinding import compute_path
from fracture_point.states.state_manager import StateManager
from fracture_point.states.playing import PlayingState
from fracture_point.states.inventory import InventoryState
from fracture_point.states.socketing import SocketingState
from fracture_point.states.identify import IdentifyState
from fracture_point.states.unequip import UnequipState
from fracture_point.states.run_end import RunEndState

FOV_RADIUS = 8

# Render priority for entities sharing a tile - HIGHER draws on top.
# Sorted ascending and drawn in that order, so the highest-priority
# thing present is always what's visible last (on top) if several
# entities land on the same tile.
PRIORITY_CORPSE = 0
PRIORITY_GROUND_ITEM = 50   # items, gold, gems, consumables
PRIORITY_LIVING = 80
PRIORITY_PLAYER = 100


class Engine:
    def __init__(self, game_map: GameMap, player: Entity, panel_width: int = 32):
        self.game_map = game_map
        self.player = player
        self.log = MessageLog()

        self.map_console = tcod.console.Console(self.game_map.width, self.game_map.height, order="F")
        self.panel_width = panel_width
        self.panel_console = tcod.console.Console(panel_width, self.game_map.height, order="F")

        self.turn_queue = TurnQueue()
        for entity in self.game_map.entities:
            self.turn_queue.schedule(entity, 0)

        self.states = StateManager()
        self.states.register(PlayingState(self))
        self.states.register(InventoryState(self))
        self.states.register(SocketingState(self))
        self.states.register(IdentifyState(self))
        self.states.register(UnequipState(self))
        self.states.register(RunEndState(self))
        self.states.start("playing")

        save = save_data.load_save()
        self.currency_at_start = save["currency"]
        self.gold_collected = 0
        self.known_properties: set[str] = set(save.get("known_properties", []))

        self.run_active = True
        self.run_outcome: str | None = None  # "died" | "escaped"
        self.final_currency = self.currency_at_start

        self.update_fov()

    def update_fov(self) -> None:
        self.game_map.visible[:] = tcod.map.compute_fov(
            transparency=self.game_map.tiles,
            pov=(self.player.x, self.player.y),
            radius=FOV_RADIUS,
        )
        self.game_map.explored |= self.game_map.visible

    def run(self, console: tcod.console.Console, context: tcod.context.Context) -> None:
        while self.run_active:
            entity, time = self.turn_queue.pop_next()

            if entity.fighter is None:
                continue

            if entity is self.player:
                cost = self.await_player_turn(console, context)
                if self.run_active:
                    self.regen_player_gear_charge()
            else:
                cost = self.take_enemy_action(entity)

            if not self.run_active:
                break

            self.turn_queue.schedule(entity, time + cost)

        self.show_run_end_screen(console, context)

    def show_run_end_screen(self, console: tcod.console.Console, context: tcod.context.Context) -> None:
        """
        Displays the terminal run_end state and waits for any key.
        Returns control to the caller (main.py's hub/run loop) - reaching
        the Hub is a real transition, not a dead end.
        """
        while True:
            self.render(console)
            context.present(console, keep_aspect=True, integer_scaling=False)

            for event in tcod.event.wait():
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()
                if isinstance(event, tcod.event.KeyDown):
                    return

    def end_run(self, outcome: str) -> None:
        """Called once, exactly when a run stops (death or reaching the
        stairs). Banks currency regardless of outcome. Gear is only
        banked on a successful escape - death wipes any saved gear,
        including gear that had persisted from an earlier escape."""
        self.run_outcome = outcome
        self.run_active = False
        self.final_currency = self.currency_at_start + self.gold_collected
        save_data.save_currency(self.final_currency)

        if outcome == "escaped":
            save_data.save_gear(
                self.player.equipment.equipped,
                self.player.inventory.items,
                self.player.inventory.gems,
            )
        elif outcome == "died":
            save_data.clear_gear()

        self.states.replace("run_end")

    def await_player_turn(self, console: tcod.console.Console, context: tcod.context.Context) -> int:
        while True:
            self.render(console)
            context.present(console, keep_aspect=True, integer_scaling=False)

            for event in tcod.event.wait():
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()

                cost = self.states.current.handle_event(event)
                if cost is not None:
                    return cost

                break

    def try_pickup(self) -> bool:
        gem_target = self.game_map.get_gem_at(self.player.x, self.player.y)
        if gem_target is not None:
            if self.player.inventory.gems_full:
                self.log.add("No room to carry another crystal.")
                return False
            self.player.inventory.add_gem(gem_target.gem)
            self.log.add(f"You pick up {gem_target.gem.name}.")
            self.game_map.entities.remove(gem_target)
            return True

        consumable_target = self.game_map.get_consumable_at(self.player.x, self.player.y)
        if consumable_target is not None:
            if self.player.inventory.consumables_full:
                self.log.add("No room to carry another consumable.")
                return False
            self.player.inventory.add_consumable(consumable_target.consumable)
            self.log.add(f"You pick up {consumable_target.consumable.name}.")
            self.game_map.entities.remove(consumable_target)
            return True

        target = self.game_map.get_item_at(self.player.x, self.player.y)
        if target is None:
            self.log.add("There's nothing here to pick up.")
            return False

        if self.player.inventory.is_full:
            self.log.add("Your inventory is full.")
            return False

        self.player.inventory.add(target.item)
        self.log.add(f"You pick up {target.item.display_name(self.known_properties)}.")
        self.game_map.entities.remove(target)
        return True

    def equip_item(self, item) -> None:
        candidate_slots = self.player.equipment.empty_slots_for(item)

        if not candidate_slots:
            self.log.add(f"No open slot for {item.display_name(self.known_properties)}.")
            return

        slot_id = candidate_slots[0]
        previous = self.player.equipment.equip(item, slot_id)
        self.player.inventory.remove(item)

        display = item.display_name(self.known_properties)
        if previous is not None:
            self.player.inventory.add(previous)
            self.log.add(f"You equip {display} ({slot_id}), stowing {previous.display_name(self.known_properties)}.")
        else:
            self.log.add(f"You equip {display} ({slot_id}).")

    def unequip_slot(self, slot_id: str) -> None:
        previous = self.player.equipment.unequip(slot_id)
        if previous is None:
            self.log.add(f"Nothing equipped in {slot_id}.")
            return

        if not self.player.inventory.add(previous):
            self.player.equipment.equip(previous, slot_id)
            self.log.add("No room in your inventory to unequip that.")
            return

        self.log.add(f"You unequip {previous.display_name(self.known_properties)} ({slot_id}).")

    def socket_gem(self, gem, item) -> None:
        index = item.empty_socket_index()
        if index is None:
            self.log.add(f"{item.display_name(self.known_properties)} has no open socket.")
            return

        item.sockets[index] = gem
        self.player.inventory.remove_gem(gem)
        self.log.add(f"You socket {gem.name} into {item.display_name(self.known_properties)}.")

    def attempt_identify(self, item) -> None:
        scroll = next((c for c in self.player.inventory.consumables if c.kind == "identify"), None)

        if scroll is None:
            self.log.add("You have no identify scroll.")
            return

        self.player.inventory.remove_consumable(scroll)
        self.known_properties.add(item.identify_property)
        save_data.save_known_properties(self.known_properties)

        self.log.add(f"It's {item.name}!")

    def player_action(self, dx: int, dy: int) -> bool:
        dest_x, dest_y = self.player.x + dx, self.player.y + dy

        target = self.game_map.get_blocking_entity_at(dest_x, dest_y)
        if target is not None:
            self.attack(self.player, target)
            return True

        if not self.game_map.is_walkable(dest_x, dest_y):
            return False

        self.player.move(dx, dy)

        gold_entity = self.game_map.get_gold_at(dest_x, dest_y)
        if gold_entity is not None:
            self.gold_collected += gold_entity.gold_value
            self.log.add(f"You find {gold_entity.gold_value} gold.")
            self.game_map.entities.remove(gold_entity)

        if self.game_map.stairs == (dest_x, dest_y):
            self.log.add("You found the stairs and escaped with your loot!")
            self.end_run("escaped")

        return True

    def find_nearest_visible_enemy(self) -> Entity | None:
        candidates = [
            e for e in self.game_map.entities
            if e is not self.player
            and e.fighter is not None
            and e.fighter.is_alive
            and self.game_map.visible[e.x, e.y]
        ]
        if not candidates:
            return None

        return min(
            candidates,
            key=lambda e: max(abs(e.x - self.player.x), abs(e.y - self.player.y)),
        )

    def cast_bolt(self, caster: Entity, target: Entity) -> None:
        raw_damage = caster.fighter.magic_power
        damage = round(raw_damage * (1 - target.fighter.magic_resist))

        if damage > 0:
            self.log.add(f"{caster.name} casts a bolt at {target.name} for {damage}.")
            target.fighter.take_damage(damage)
        else:
            self.log.add(f"{caster.name}'s bolt fizzles against {target.name}.")

        if not target.fighter.is_alive:
            self.die(target)

    def attempt_cast(self) -> int | None:
        wand = self.player.equipment.equipped["wand"]
        if wand is None:
            self.log.add("You have no wand equipped.")
            return None

        gem = wand.socketed_active_gem()
        if gem is None:
            self.log.add(f"{wand.display_name(self.known_properties)} has no ability crystal socketed.")
            return None

        if not gem.can_cast():
            self.log.add(f"{gem.name} doesn't have enough charge ({gem.current_charge}/{gem.max_charge}).")
            return None

        target = self.find_nearest_visible_enemy()
        if target is None:
            self.log.add("No target in sight.")
            return None

        gem.consume()
        self.cast_bolt(self.player, target)
        return self.player.fighter.action_cost

    def regen_player_gear_charge(self) -> None:
        for item in self.player.equipment.equipped.values():
            if item is None:
                continue
            for gem in item.sockets:
                if gem is not None:
                    gem.regen()

    def take_enemy_action(self, entity: Entity) -> int:
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
        entity.is_corpse = True

        if entity is self.player:
            self.log.add("You have died.")
            self.end_run("died")

    def _render_priority(self, entity: Entity) -> int:
        """Higher = drawn on top when multiple entities share a tile.
        See the module-level PRIORITY_* constants."""
        if entity is self.player:
            return PRIORITY_PLAYER
        if entity.is_corpse:
            return PRIORITY_CORPSE
        if entity.fighter is not None and entity.fighter.is_alive:
            return PRIORITY_LIVING
        return PRIORITY_GROUND_ITEM

    def render(self, console: tcod.console.Console) -> None:
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
                elif gm.stairs == (x, y):
                    base_char = ">"
                    color = (230, 200, 80) if gm.visible[x, y] else (110, 95, 40)
                else:
                    base_char = "." if gm.tiles[x, y] else "#"
                    if gm.visible[x, y]:
                        color = (200, 200, 200) if gm.tiles[x, y] else (130, 130, 130)
                    else:
                        color = (60, 60, 60) if gm.tiles[x, y] else (40, 40, 40)

                console.print(x=x, y=y, text=base_char, fg=color)

        # Draw lowest-priority entities first, highest last, so anything
        # sharing a tile with something more "important" gets covered by
        # it rather than the reverse. This is what fixes corpses
        # painting over the player/items - previously entities were
        # drawn in raw list order, which had no relationship to what
        # should visually "win" on a shared tile.
        for entity in sorted(gm.entities, key=self._render_priority):
            # A corpse should never hide the stairs marker underneath it -
            # stairs are drawn at the tile level above, not as an entity,
            # so sorting alone can't protect them the way it protects the
            # player/items. Skip drawing the corpse there entirely instead.
            if entity.is_corpse and gm.stairs == (entity.x, entity.y):
                continue

            if gm.visible[entity.x, entity.y]:
                console.print(x=entity.x, y=entity.y, text=entity.char, fg=entity.color)
            elif gm.explored[entity.x, entity.y] and entity.fighter is None:
                dim_color = tuple(c // 2 for c in entity.color)
                console.print(x=entity.x, y=entity.y, text=entity.char, fg=dim_color)

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

        console.print(x=x, y=y, text=f"Gold: {self.gold_collected}", fg=(230, 200, 80))
        y += 1

        weapon = self.player.equipment.equipped["weapon"]
        weapon_name = weapon.display_name(self.known_properties) if weapon else "(none)"
        console.print(x=x, y=y, text=f"Weapon: {weapon_name}", fg=(180, 180, 220))
        y += 1

        wand = self.player.equipment.equipped["wand"]
        if wand is None:
            wand_text = "Wand: (none)"
        else:
            gem = wand.socketed_active_gem()
            wand_name = wand.display_name(self.known_properties)
            if gem is None:
                wand_text = f"Wand: {wand_name} [no crystal]"
            else:
                wand_text = f"Wand: {wand_name} [{gem.name} {gem.current_charge}/{gem.max_charge}]"
        console.print(x=x, y=y, text=wand_text, fg=(180, 220, 220))
        y += 1

        console.print(x=x, y=y, text="[i]nv  [g]et  [c]ast", fg=(120, 120, 120))
        y += 2

        console.print(x=x, y=y, text="── Log ──", fg=(120, 120, 120))
        y += 1

        content_width = console.width - 4
        wrapped_lines: list[str] = []
        for message in self.log.messages:
            wrapped_lines.extend(textwrap.wrap(message, width=content_width))

        max_lines = console.height - y - 2
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
                line = f"{i + 1}. {item.inventory_label(self.known_properties)}"
                console.print(x=x, y=y, text=line, fg=item.color)
                y += 1

        y += 1
        console.print(x=x, y=y, text="[s] socket a crystal", fg=(120, 120, 120))
        y += 1
        console.print(x=x, y=y, text="[r] read identify scroll", fg=(120, 120, 120))
        y += 1
        console.print(x=x, y=y, text="[u] unequip gear", fg=(120, 120, 120))
        y += 1
        console.print(x=x, y=y, text="[esc] back", fg=(120, 120, 120))

    def render_socketing(self, console: tcod.console.Console, step: str, socketable_items: list) -> None:
        title = "Socket: Choose Item" if step == "choose_item" else "Socket: Choose Gem"
        console.draw_frame(
            x=0, y=0, width=console.width, height=console.height,
            title=title, fg=(180, 180, 180), bg=(0, 0, 0),
        )

        x, y = 2, 2

        if step == "choose_item":
            if not socketable_items:
                console.print(x=x, y=y, text="(nothing has an open socket)", fg=(150, 150, 150))
            else:
                for i, item in enumerate(socketable_items):
                    line = f"{i + 1}. {item.display_name(self.known_properties)}"
                    console.print(x=x, y=y, text=line, fg=item.color)
                    y += 1
        else:
            gems = self.player.inventory.gems
            if not gems:
                console.print(x=x, y=y, text="(no crystals carried)", fg=(150, 150, 150))
            else:
                for i, gem in enumerate(gems):
                    line = f"{i + 1}. {gem.name} ({gem.current_charge}/{gem.max_charge})"
                    console.print(x=x, y=y, text=line, fg=gem.color)
                    y += 1

        y += 1
        console.print(x=x, y=y, text="[esc] back", fg=(120, 120, 120))

    def render_identify(self, console: tcod.console.Console, unidentified_items: list) -> None:
        console.draw_frame(
            x=0, y=0, width=console.width, height=console.height,
            title="Read Scroll", fg=(180, 180, 180), bg=(0, 0, 0),
        )

        x, y = 2, 2

        scroll_count = sum(1 for c in self.player.inventory.consumables if c.kind == "identify")
        console.print(x=x, y=y, text=f"Identify Scrolls: {scroll_count}", fg=(200, 200, 220))
        y += 2

        if not unidentified_items:
            console.print(x=x, y=y, text="(nothing unidentified)", fg=(150, 150, 150))
        else:
            for i, item in enumerate(unidentified_items):
                line = f"{i + 1}. {item.display_name(self.known_properties)}"
                console.print(x=x, y=y, text=line, fg=item.color)
                y += 1

        y += 1
        console.print(x=x, y=y, text="[esc] back", fg=(120, 120, 120))

    def render_unequip(self, console: tcod.console.Console, equipped_slots: list) -> None:
        console.draw_frame(
            x=0, y=0, width=console.width, height=console.height,
            title="Unequip", fg=(180, 180, 180), bg=(0, 0, 0),
        )

        x, y = 2, 2

        if not equipped_slots:
            console.print(x=x, y=y, text="(nothing equipped)", fg=(150, 150, 150))
        else:
            for i, (slot_id, item) in enumerate(equipped_slots):
                line = f"{i + 1}. [{slot_id}] {item.display_name(self.known_properties)}"
                console.print(x=x, y=y, text=line, fg=item.color)
                y += 1

        y += 1
        console.print(x=x, y=y, text="[esc] back", fg=(120, 120, 120))

    def render_run_end(self, console: tcod.console.Console) -> None:
        title = "You Escaped" if self.run_outcome == "escaped" else "You Died"
        console.draw_frame(
            x=0, y=0, width=console.width, height=console.height,
            title=title, fg=(180, 180, 180), bg=(0, 0, 0),
        )

        x, y = 2, 2
        console.print(x=x, y=y, text=f"Gold found this run: {self.gold_collected}", fg=(230, 200, 80))
        y += 1
        console.print(x=x, y=y, text=f"Total gold banked: {self.final_currency}", fg=(230, 200, 80))
        y += 2

        if self.run_outcome == "escaped":
            console.print(x=x, y=y, text="Your gear is safe.", fg=(150, 220, 150))
        else:
            console.print(x=x, y=y, text="Your gear is lost.", fg=(220, 120, 120))
        y += 2

        console.print(x=x, y=y, text="Press any key to return to the Hub.", fg=(120, 120, 120))