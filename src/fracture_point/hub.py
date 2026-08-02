from __future__ import annotations

import tcod

from fracture_point import save_data

def run_hub_screen(console: tcod.console.Console, context: tcod.context.Context) -> str:
    save = save_data.load_save()
    currency = save["currency"]
    equipped, inventory_items, loose_gems = save_data.load_gear()

    while True:
        console.clear()
        console.draw_frame(
            x=0, y=0, width=console.width, height=console.height,
            title="Hub", fg=(180, 180, 180), bg=(0, 0, 0),
        )

        x, y = 2, 2
        console.print(x=x, y=y, text="Welcome back.", fg=(255, 255, 255))
        y += 2
        console.print(x=x, y=y, text=f"Currency: {currency}", fg=(230, 200, 80))
        y += 2

        console.print(x=x, y=y, text="Gear on hand:", fg=(180, 180, 220))
        y += 1
        if not equipped and not inventory_items and not loose_gems:
            console.print(x=x, y=y, text="  (nothing)", fg=(120, 120, 120))
            y += 1
        else:
            for slot_id, item in equipped.items():
                console.print(x=x, y=y, text=f"  [{slot_id}] {item.name}", fg=item.color)
                y += 1
            for item in inventory_items:
                console.print(x=x, y=y, text=f"  (carried) {item.name}", fg=item.color)
                y += 1
            for gem in loose_gems:
                console.print(x=x, y=y, text=f"  (loose crystal) {gem.name}", fg=gem.color)
                y += 1

        y += 2
        console.print(x=x, y=y, text="[enter] Descend", fg=(150, 220, 150))
        y += 1
        console.print(x=x, y=y, text="[esc] Quit", fg=(220, 120, 120))
        y += 2
        console.print(x=x, y=y, text="(Crafting/shop coming in a future step)", fg=(90, 90, 90))

        context.present(console, keep_aspect=True, integer_scaling=False)

        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                return "quit"
            if isinstance(event, tcod.event.KeyDown):
                if event.sym == tcod.event.KeySym.RETURN:
                    return "descend"
                if event.sym == tcod.event.KeySym.ESCAPE:
                    return "quit"