from pathlib import Path
import random
import tcod

from fracture_point.dungeon_generator import generate_dungeon
from fracture_point.entity import Entity
from fracture_point.equipment import Equipment
from fracture_point.fighter import Fighter
from fracture_point.inventory import Inventory
from fracture_point.stats import Stats
from fracture_point.engine import Engine
from fracture_point.hub import run_hub_screen
from fracture_point.loot_table import pick_loot
from fracture_point import save_data

ASSETS_DIR = Path("assets")
FONT_PATH = ASSETS_DIR / "IBM_Plex_Mono" / "IBMPlexMono-Bold.ttf"

MAP_WIDTH = 90
MAP_HEIGHT = 55
PANEL_WIDTH = 32

SCREEN_WIDTH = MAP_WIDTH + PANEL_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT

TILE_WIDTH = 10
TILE_HEIGHT = 18

# Chance that any given non-starting room gets ONE random loot spawn,
# on top of its guaranteed enemy + gold. Which item you get is decided
# by loot_table.json's per-entry weights, not this constant - this only
# controls whether a room gets a loot roll AT ALL.
LOOT_CHANCE = 0.6


def pick_free_tile(room, taken_positions: set[tuple[int, int]]) -> tuple[int, int]:
    """
    Picks a random tile within a room's interior, avoiding any already-
    occupied positions (so loot doesn't spawn stacked on the enemy or
    gold pile in that room). Falls back to the room's center if it
    can't find a free spot after a few tries.
    """
    for _ in range(10):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)
        if (x, y) not in taken_positions:
            return x, y
    return room.center


def build_run() -> Engine:
    """Generates a fresh dungeon and player (restoring any saved gear),
    and returns a ready-to-run Engine. Called once per descent from
    the Hub."""
    game_map, rooms = generate_dungeon(
        MAP_WIDTH, MAP_HEIGHT, max_rooms=18, room_min_size=6, room_max_size=10
    )

    player_x, player_y = rooms[0].center
    player_fighter = Fighter(
        stats=Stats(strength=14, dexterity=12, intelligence=12, vitality=14, wisdom=10, luck=10),
        base_power=3, base_defense=1, base_max_hp=6,
        base_magic_power=2, base_magic_resist=0,
    )
    player_equipment = Equipment(fighter=player_fighter)
    player_inventory = Inventory(capacity=10)

    saved_equipped, saved_inventory_items, saved_gems = save_data.load_gear()
    for slot_id, item in saved_equipped.items():
        player_equipment.equip(item, slot_id)
    for item in saved_inventory_items:
        player_inventory.add(item)
    for gem in saved_gems:
        player_inventory.add_gem(gem)

    player = Entity(
        x=player_x, y=player_y,
        char="@", color=(255, 255, 255), name="Player", blocks_movement=True,
        fighter=player_fighter,
        inventory=player_inventory,
        equipment=player_equipment,
    )
    game_map.entities.append(player)

    for room in rooms[1:]:
        taken_positions: set[tuple[int, int]] = set()

        enemy_x, enemy_y = room.center
        taken_positions.add((enemy_x, enemy_y))
        enemy = Entity(
            x=enemy_x, y=enemy_y,
            char="r", color=(160, 160, 160), name="Rat", blocks_movement=True,
            fighter=Fighter(
                stats=Stats(strength=6, dexterity=16, intelligence=4, vitality=6, wisdom=4, luck=8),
                base_power=2, base_defense=0, base_max_hp=0,
            ),
        )
        game_map.entities.append(enemy)

        gold_x, gold_y = pick_free_tile(room, taken_positions)
        taken_positions.add((gold_x, gold_y))
        gold_pile = Entity(
            x=gold_x, y=gold_y,
            char="$", color=(230, 200, 80), name="Gold",
            gold_value=random.randint(5, 20),
        )
        game_map.entities.append(gold_pile)

        if random.random() < LOOT_CHANCE:
            loot_x, loot_y = pick_free_tile(room, taken_positions)
            game_map.entities.append(pick_loot(loot_x, loot_y))

    return Engine(game_map=game_map, player=player, panel_width=PANEL_WIDTH)


def main() -> None:
    tileset = tcod.tileset.load_truetype_font(str(FONT_PATH), TILE_WIDTH, TILE_HEIGHT)

    with tcod.context.new(
        columns=SCREEN_WIDTH,
        rows=SCREEN_HEIGHT,
        tileset=tileset,
        title="Fracture Point",
        vsync=True,
        sdl_window_flags=tcod.context.SDL_WINDOW_RESIZABLE,
    ) as context:
        console = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")

        while True:
            action = run_hub_screen(console, context)
            if action == "quit":
                break

            engine = build_run()
            engine.run(console, context)


if __name__ == "__main__":
    main()