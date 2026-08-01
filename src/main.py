from pathlib import Path
import tcod

from fracture_point.entity import Entity
from fracture_point.game_map import GameMap
from fracture_point.engine import Engine

ASSETS_DIR = Path("assets")
FONT_PATH = ASSETS_DIR / "IBM_Plex_Mono" / "IBMPlexMono-Regular.ttf"

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
TILE_WIDTH = 10
TILE_HEIGHT = 18


def main() -> None:
    tileset = tcod.tileset.load_truetype_font(str(FONT_PATH), TILE_WIDTH, TILE_HEIGHT)

    game_map = GameMap(SCREEN_WIDTH, SCREEN_HEIGHT)
    player = Entity(x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2, char="@", color=(255, 255, 255), name="Player")
    engine = Engine(game_map=game_map, player=player)

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