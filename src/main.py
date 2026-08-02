from pathlib import Path
import tcod

from fracture_point.dungeon_generator import generate_dungeon
from fracture_point.entity import Entity
from fracture_point.fighter import Fighter
from fracture_point.stats import Stats
from fracture_point.engine import Engine

ASSETS_DIR = Path("assets")
FONT_PATH = ASSETS_DIR / "IBM_Plex_Mono" / "IBMPlexMono-Regular.ttf"

MAP_WIDTH = 60
MAP_HEIGHT = 45
SIDEBAR_WIDTH = 24

SCREEN_WIDTH = MAP_WIDTH + 1 + SIDEBAR_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT

TILE_WIDTH = 10
TILE_HEIGHT = 18


def main() -> None:
    tileset = tcod.tileset.load_truetype_font(str(FONT_PATH), TILE_WIDTH, TILE_HEIGHT)

    game_map, rooms = generate_dungeon(
        MAP_WIDTH, MAP_HEIGHT, max_rooms=12, room_min_size=6, room_max_size=10
    )

    player_x, player_y = rooms[0].center
    player = Entity(
        x=player_x, y=player_y,
        char="@", color=(255, 255, 255), name="Player", blocks_movement=True,
        fighter=Fighter(
            stats=Stats(strength=14, dexterity=12, intelligence=10, vitality=14, wisdom=10, luck=10),
            base_power=3, base_defense=1, base_max_hp=6,
        ),
    )
    game_map.entities.append(player)

    for room in rooms[1:]:
        enemy_x, enemy_y = room.center
        enemy = Entity(
            x=enemy_x, y=enemy_y,
            char="r", color=(200, 80, 80), name="Rat", blocks_movement=True,
            fighter=Fighter(
                stats=Stats(strength=6, dexterity=8, intelligence=4, vitality=6, wisdom=4, luck=8),
                base_power=2, base_defense=0, base_max_hp=0,
            ),
        )
        game_map.entities.append(enemy)

    engine = Engine(game_map=game_map, player=player, sidebar_width=SIDEBAR_WIDTH)

    with tcod.context.new(
        columns=SCREEN_WIDTH,
        rows=SCREEN_HEIGHT,
        tileset=tileset,
        title="Fracture Point",
        vsync=True,
    ) as context:
        console = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")

        while True:
            engine.render(console)
            context.present(console)
            engine.handle_events()


if __name__ == "__main__":
    main()