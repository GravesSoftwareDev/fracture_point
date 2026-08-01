from pathlib import Path
import tcod

from fracture_point.entity import Entity
from fracture_point.fighter import Fighter
from fracture_point.game_map import GameMap
from fracture_point.engine import Engine

ASSETS_DIR = Path("assets")
FONT_PATH = ASSETS_DIR / "IBM_Plex_Mono" / "IBMPlexMono-Regular.ttf"

MAP_WIDTH = 60
MAP_HEIGHT = 45
SIDEBAR_WIDTH = 24

SCREEN_WIDTH = MAP_WIDTH + 1 + SIDEBAR_WIDTH  # +1 for the border column
SCREEN_HEIGHT = MAP_HEIGHT

TILE_WIDTH = 10
TILE_HEIGHT = 18


def main() -> None:
    tileset = tcod.tileset.load_truetype_font(str(FONT_PATH), TILE_WIDTH, TILE_HEIGHT)

    game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)

    player = Entity(
        x=MAP_WIDTH // 2, y=MAP_HEIGHT // 2,
        char="@", color=(255, 255, 255), name="Player", blocks_movement=True,
        fighter=Fighter(max_hp=20, power=4, defense=1),
    )
    enemy = Entity(
        x=MAP_WIDTH // 2 + 5, y=MAP_HEIGHT // 2,
        char="r", color=(200, 80, 80), name="Rat", blocks_movement=True,
        fighter=Fighter(max_hp=6, power=2, defense=0),
    )

    game_map.entities.append(player)
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