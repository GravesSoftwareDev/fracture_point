from pathlib import Path
import random
import tcod

from fracture_point.dungeon_generator import generate_dungeon
from fracture_point.entity import Entity
from fracture_point.equipment import Equipment
from fracture_point.gem import Gem
from fracture_point.fighter import Fighter
from fracture_point.inventory import Inventory
from fracture_point.item import Item
from fracture_point.stats import Stats
from fracture_point.engine import Engine
from fracture_point.hub import run_hub_screen
from fracture_point import save_data
from fracture_point.consumable import Consumable

ASSETS_DIR = Path("assets")
FONT_PATH = ASSETS_DIR / "IBM_Plex_Mono" / "IBMPlexMono-Bold.ttf"

MAP_WIDTH = 90
MAP_HEIGHT = 55
PANEL_WIDTH = 32

SCREEN_WIDTH = MAP_WIDTH + PANEL_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT

TILE_WIDTH = 14
TILE_HEIGHT = 24


def build_run() -> Engine:
    """Generates a fresh dungeon and player (restoring any saved gear),
    and returns a ready-to-run Engine. Called once per descent from
    the Hub - previously this was just inline in main()."""
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

    for i, room in enumerate(rooms[1:], start=1):
        enemy_x, enemy_y = room.center
        enemy = Entity(
            x=enemy_x, y=enemy_y,
            char="r", color=(200, 80, 80), name="Rat", blocks_movement=True,
            fighter=Fighter(
                stats=Stats(strength=6, dexterity=16, intelligence=4, vitality=6, wisdom=4, luck=8),
                base_power=2, base_defense=0, base_max_hp=0,
            ),
        )
        game_map.entities.append(enemy)

        gold_x, gold_y = room.x1 + 1, room.y1 + 1
        gold_pile = Entity(
            x=gold_x, y=gold_y,
            char="$", color=(230, 200, 80), name="Gold",
            gold_value=random.randint(5, 20),
        )
        game_map.entities.append(gold_pile)

        if i % 2 == 0:
            item_x, item_y = room.x1 + 2, room.y1 + 2
            dagger = Entity(
                x=item_x, y=item_y,
                char="/", color=(200, 200, 100), name="Dagger",
                item=Item(name="Dagger", char="/", color=(200, 200, 100), slot_types=["weapon"], power_bonus=2),
            )
            game_map.entities.append(dagger)

            ring_x, ring_y = room.x1 + 3, room.y1 + 2
            ring = Entity(
                x=ring_x, y=ring_y,
                char="=", color=(220, 180, 60), name="Ring of Fortitude",
                item=Item(name="Ring of Fortitude", char="=", color=(220, 180, 60), slot_types=["ring"], defense_bonus=1),
            )
            game_map.entities.append(ring)

            wand_x, wand_y = room.x1 + 4, room.y1 + 2
            wand = Entity(
                x=wand_x, y=wand_y,
                char="/", color=(120, 200, 220), name="Apprentice Wand",
                item=Item(
                    name="Apprentice Wand", char="/", color=(120, 200, 220),
                    slot_types=["wand"], magic_power_bonus=3,
                    gem_slots=1, sockets=[]
                ),
            )
            game_map.entities.append(wand)

            ember_crystal = Gem(
                name="Ember Crystal", char="*", color=(220, 120, 60),
                max_charge=8, charge_per_turn=1, cast_cost=4,
            )
            ember_x, ember_y = room.x1 + 5, room.y1 + 2
            ember_entity = Entity(
                x=ember_x, y=ember_y,
                char="*", color=(220, 120, 60), name="Ember Crystal",
                gem=ember_crystal,
            )
            game_map.entities.append(ember_entity)

            flame_ring_x, flame_ring_y = room.x1 + 6, room.y1 + 2
            flame_ring = Entity(
                x=flame_ring_x, y=flame_ring_y,
                char="=", color=(220, 100, 60), name="Ring of Flame",
                item=Item(
                    name="Ring of Flame", char="=", color=(220, 100, 60),
                    slot_types=["ring"], defense_bonus=2,
                    base_name="Ring", identify_property="flame",
                ),
            )
            game_map.entities.append(flame_ring)

            scroll_x, scroll_y = room.x1 + 1, room.y1 + 3
            scroll_entity = Entity(
                x=scroll_x, y=scroll_y,
                char="?", color=(230, 230, 180), name="Identify Scroll",
                consumable=Consumable(name="Identify Scroll", char="?", color=(230, 230, 180), kind="identify"),
            )
            game_map.entities.append(scroll_entity)

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

        # The window/context/console are created once and persist for
        # the whole session. The Hub and each dungeon run just take
        # turns rendering into the same console.
        while True:
            action = run_hub_screen(console, context)
            if action == "quit":
                break

            engine = build_run()
            engine.run(console, context)


if __name__ == "__main__":
    main()