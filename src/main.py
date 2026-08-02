from pathlib import Path
import tcod
import random

from fracture_point.dungeon_generator import generate_dungeon
from fracture_point.entity import Entity
from fracture_point.equipment import Equipment
from fracture_point.fighter import Fighter
from fracture_point.inventory import Inventory
from fracture_point.item import Item
from fracture_point.stats import Stats
from fracture_point.engine import Engine

ASSETS_DIR = Path("assets")
FONT_PATH = ASSETS_DIR / "IBM_Plex_Mono" / "IBMPlexMono-Regular.ttf"

MAP_WIDTH = 90
MAP_HEIGHT = 55
PANEL_WIDTH = 32

SCREEN_WIDTH = MAP_WIDTH + PANEL_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT

TILE_WIDTH = 10
TILE_HEIGHT = 18


def main() -> None:
    tileset = tcod.tileset.load_truetype_font(str(FONT_PATH), TILE_WIDTH, TILE_HEIGHT)

    game_map, rooms = generate_dungeon(
        MAP_WIDTH, MAP_HEIGHT, max_rooms=18, room_min_size=6, room_max_size=10
    )

    player_x, player_y = rooms[0].center
    player_fighter = Fighter(
        stats=Stats(strength=14, dexterity=12, intelligence=10, vitality=14, wisdom=10, luck=10),
        base_power=3, base_defense=1, base_max_hp=6,
    )
    player = Entity(
        x=player_x, y=player_y,
        char="@", color=(255, 255, 255), name="Player", blocks_movement=True,
        fighter=player_fighter,
        inventory=Inventory(capacity=10),
        equipment=Equipment(fighter=player_fighter),
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

    engine = Engine(game_map=game_map, player=player, panel_width=PANEL_WIDTH)

    with tcod.context.new(
        columns=SCREEN_WIDTH,
        rows=SCREEN_HEIGHT,
        tileset=tileset,
        title="Fracture Point",
        vsync=True,
    ) as context:
        console = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")
        engine.run(console, context)
    

if __name__ == "__main__":
    main()