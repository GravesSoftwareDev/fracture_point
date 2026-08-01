from pathlib import Path
import tcod

# Constants

ASSETS_DIR = Path('assets')
FONT_PATH = ASSETS_DIR / 'IBM_Plex_Mono' / 'IBMPlexMono-Regular.ttf'

# Console Size in characters (columns, rows)
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

TILE_WIDTH = 10
TILE_HEIGHT = 18

def main() -> None:
    tileset = tcod.tileset.load_truetype_font(
        str(FONT_PATH),
        TILE_WIDTH,
        TILE_HEIGHT
    )

    with tcod.context.new(
        columns=SCREEN_WIDTH,
        rows=SCREEN_HEIGHT,
        tileset=tileset,
        title='Fracture Point',
        vsync=True
    ) as context:
        console = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order='F')

        while True:
            console.clear()
            console.print(x=2, y=2, text="Fracture Point")
            console.print(x=2, y=4, text="If you can read this in IBM Plex Mono, the pipeline works.")

            context.present(console)

            for event in tcod.event.wait():
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()

if __name__ == "__main__":
    main()