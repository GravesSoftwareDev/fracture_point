import random as r
import tcod as t

from pathlib import Path

# Constants

ASSETS_DIR = Path("assets")
FONT_PATH = ASSETS_DIR / "IBMPlexMono-Bold.ttf"

SCREEN_WIDTH, SCREEN_HEIGHT = 100, 50
MAP_WIDTH, MAP_HEIGHT = 100, 50
TILE_WIDTH, TILE_HEIGHT = 10, 10 # Only works with custom fonts/tilesets. If using OS default, this is moot.
TILESET = None #t.tileset.load_truetype_font(str(FONT_PATH), TILE_WIDTH, TILE_HEIGHT) # Set to None to use OS default font

def main() -> None:
    console = t.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F") # `order` "F" - screen renders w x h, "C" - screen renders h x w

    with t.context.new(columns=console.width, rows= console.height,tileset=TILESET, title="Fracture Point") as context:
        while True:
            console.clear()
            render_all(console, SCREEN_WIDTH, SCREEN_HEIGHT)
            context.present(console)
            for event in t.event.wait():
                handle_input(event)

def render_all(
    console: t.console.Console,
    screen_width: int,
    screen_height: int,
) -> None:

    for sx in range(screen_width):
        for sy in range(screen_height):
            console.print(x=sx, y=sy, text=f"▓", fg=( 255, 100, 255))
            if sx > 0 and sx < screen_width-1 and sy > 0 and sy < screen_height-1:
                console.print(x=sx, y=sy, text="░", fg=(255, 100, 255))        

def handle_input(event: t.event.Event) -> dict[str, bool]:
    quit = False
    match event:
            case t.event.Quit():
                quit = True
            case t.event.KeyDown(sym=t.event.KeySym.ESCAPE):
                quit = True

    if quit:
        raise SystemExit()
    

if __name__ == "__main__":
    main()