#!/usr/bin/env python
"""
Run with: python main.py  (from inside this directory)
"""
import random

import tcod.console
import tcod.context
import tcod.event

import render_functions
from components.ai import HostileAI
from components.fighter import Fighter
from engine import Engine
from entity import Entity
from game_map import generate_map
from input_handlers import dispatch
import time


SCREEN_WIDTH, SCREEN_HEIGHT = 60, 30
MAP_WIDTH, MAP_HEIGHT = 80, 45

def main() -> None:
    seed = int(time.time())
    rng = random.Random(seed)
    game_map, centers = generate_map(rng, MAP_WIDTH, MAP_HEIGHT)

    player = Entity(
        *rng.choice(centers), char="@", color=(255, 255, 255), name="Player",
        blocks=True, fighter=Fighter(hp=200, defense=4, power=45),
    )
    entities = [player]
    monsters = [
        Entity(*rng.choice(centers),char="G",color=(200,200,50),name="Goblin",blocks=True,fighter=Fighter(hp=5,defense=0,power=2),ai=HostileAI()),
        Entity(*rng.choice(centers),char="S",color=(50,200,50),name="Slime",blocks=True,fighter=Fighter(hp=10,defense=2,power=1),ai=HostileAI()),
        Entity(*rng.choice(centers),char="R",color=(130,130,130),name="Rock Golem",blocks=True,fighter=Fighter(hp=25,defense=5,power=3),ai=HostileAI()),
        Entity(*rng.choice(centers),char="D",color=(200,50,50),name="Dragon",blocks=True,fighter=Fighter(hp=50,defense=10,power=20),ai=HostileAI()),
    ]
    entities.extend(monsters)
    engine = Engine(player, entities, game_map)
    engine.log("You descend into the dungeon.")

    console = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT + 6, order="F")

    with tcod.context.new(columns=console.width, rows=console.height, title="roguelike: phase 1 skeleton") as context:
        while True:
            console.clear()
            camera_x, camera_y = render_functions.camera_offset(
                player.x, player.y, SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT,
            )
            render_functions.render_all(console, engine, camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT)
            context.present(console)

            for event in tcod.event.wait():
                action = dispatch(engine.state, event)
                if action:
                    engine.handle_action(action)


if __name__ == "__main__":
    main()