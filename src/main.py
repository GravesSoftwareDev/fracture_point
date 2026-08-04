import random as r
import tcod as t
from core_classes import keybind_mapping

from pathlib import Path

# Constants
COORDS = [(-40, -3), (-39, -3), (-38, -3), (-37, -3), (-36, -3), (-40, -2), (-40, -1), (-40, 0), (-39, 0), (-38, 0), (-37, 0), (-40, 1), (-40, 2), (-40, 3), (-34, -3), (-33, -3), (-32, -3), (-31, -3), (-34, -2), (-30, -2), (-34, -1), (-30, -1), (-34, 0), (-33, 0), (-32, 0), (-31, 0), (-34, 1), (-32, 1), (-34, 2), (-31, 2), (-34, 3), (-30, 3), (-27, -3), (-26, -3), (-25, -3), (-28, -2), (-24, -2), (-28, -1), (-24, -1), (-28, 0), (-27, 0), (-26, 0), (-25, 0), (-24, 0), (-28, 1), (-24, 1), (-28, 2), (-24, 2), (-28, 3), (-24, 3), (-21, -3), (-20, -3), (-19, -3), (-18, -3), (-22, -2), (-22, -1), (-22, 0), (-22, 1), (-22, 2), (-21, 3), (-20, 3), (-19, 3), (-18, 3), (-16, -3), (-15, -3), (-14, -3), (-13, -3), (-12, -3), (-14, -2), (-14, -1), (-14, 0), (-14, 1), (-14, 2), (-14, 3), (-10, -3), (-6, -3), (-10, -2), (-6, -2), (-10, -1), (-6, -1), (-10, 0), (-6, 0), (-10, 1), (-6, 1), (-10, 2), (-6, 2), (-9, 3), (-8, 3), (-7, 3), (-4, -3), (-3, -3), (-2, -3), (-1, -3), (-4, -2), (0, -2), (-4, -1), (0, -1), (-4, 0), (-3, 0), (-2, 0), (-1, 0), (-4, 1), (-2, 1), (-4, 2), (-1, 2), (-4, 3), (0, 3), (2, -3), (3, -3), (4, -3), (5, -3), (6, -3), (2, -2), (2, -1), (2, 0), (3, 0), (4, 0), (5, 0), (2, 1), (2, 2), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (12, -3), (13, -3), (14, -3), (15, -3), (12, -2), (16, -2), (12, -1), (16, -1), (12, 0), (13, 0), (14, 0), (15, 0), (12, 1), (12, 2), (12, 3), (19, -3), (20, -3), (21, -3), (18, -2), (22, -2), (18, -1), (22, -1), (18, 0), (22, 0), (18, 1), (22, 1), (18, 2), (22, 2), (19, 3), (20, 3), (21, 3), (24, -3), (25, -3), (26, -3), (27, -3), (28, -3), (26, -2), (26, -1), (26, 0), (26, 1), (26, 2), (24, 3), (25, 3), (26, 3), (27, 3), (28, 3), (30, -3), (34, -3), (30, -2), (31, -2), (34, -2), (30, -1), (32, -1), (34, -1), (30, 0), (32, 0), (34, 0), (30, 1), (33, 1), (34, 1), (30, 2), (34, 2), (30, 3), (34, 3), (36, -3), (37, -3), (38, -3), (39, -3), (40, -3), (38, -2), (38, -1), (38, 0), (38, 1), (38, 2), (38, 3)]

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
    for cx, cy in COORDS:
        console.print(x=screen_width//2 + cx, y = screen_height//2 + cy, text=f"▓", fg=( 255, 100, 255))     

def handle_input(event: t.event.Event) -> dict[str, bool]:
    def do_quit():
        raise SystemExit()

    keybinds = [
        keybind_mapping(t.event.Quit(), "event", do_quit),
        keybind_mapping("ESCAPE", "keybind", do_quit)
    ]

    for keybind in keybinds:
        if keybind.type == "event" and isinstance(event, type(keybind.event)):
            keybind.action()
        elif keybind.type == "keybind" and isinstance(event, t.event.KeyDown) and event.sym == t.event.KeySym[keybind.event]:
            keybind.action()

if __name__ == "__main__":
    main()