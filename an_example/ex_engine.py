"""GameState: an explicit state enum instead of a scatter of booleans.

input_handlers.py picks which dispatch function to call based on `Engine.state`;
Engine.handle_action() is the only place state transitions happen. Later phases
add more states (SHOW_INVENTORY, TARGETING, ...) and more `case`s -- the shape
doesn't change, it just grows.
"""
from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from an_example.ex_entity import Entity
    from an_example.ex_game_map import GameMap

MESSAGE_LOG_LINES = 5


class GameState(Enum):
    PLAYER_TURN = auto()
    ENEMY_TURN = auto()
    PLAYER_DEAD = auto()
    # Phase 3 adds SHOW_INVENTORY, TARGETING here -- same pattern, new members.


class Engine:
    def __init__(self, player: "Entity", entities: list["Entity"], game_map: "GameMap") -> None:
        self.player = player
        self.entities = entities  # includes the player
        self.game_map = game_map
        self.state = GameState.PLAYER_TURN
        self.messages: list[str] = []
        self.game_map.update_fov((player.x, player.y))

    def log(self, text: str) -> None:
        self.messages.append(text)
        self.messages = self.messages[-MESSAGE_LOG_LINES:]

    def blocking_entity_at(self, x: int, y: int) -> "Entity | None":
        for entity in self.entities:
            if entity.blocks and entity.x == x and entity.y == y:
                return entity
        return None

    def handle_action(self, action: dict[str, Any]) -> None:
        """The only place GameState transitions happen."""
        if action.get("quit"):
            raise SystemExit()

        if self.state == GameState.PLAYER_TURN:
            move = action.get("move")
            if move:
                self._player_move_or_attack(*move)
                self.state = GameState.ENEMY_TURN

        if self.state == GameState.ENEMY_TURN:
            self._run_enemy_turns()
            if self.player.fighter.hp <= 0:
                self.state = GameState.PLAYER_DEAD
            else:
                self.state = GameState.PLAYER_TURN

    def _player_move_or_attack(self, dx: int, dy: int) -> None:
        dest_x, dest_y = self.player.x + dx, self.player.y + dy
        target = self.blocking_entity_at(dest_x, dest_y)
        if target is not None:
            for result in self.player.fighter.attack(target):
                self._process_result(result)
        elif self.game_map.is_walkable(dest_x, dest_y):
            self.player.move(dx, dy)
            self.game_map.update_fov((self.player.x, self.player.y))

    def _run_enemy_turns(self) -> None:
        for entity in list(self.entities):
            if entity is self.player or entity.ai is None:
                continue
            for result in entity.ai.take_turn(self.player, self.game_map, self.entities):
                self._process_result(result)

    def _process_result(self, result: dict[str, Any]) -> None:
        message = result.get("message")
        if message:
            self.log(message)
        dead_entity = result.get("dead")
        if dead_entity is not None:
            self._kill(dead_entity)

    def _kill(self, entity: "Entity") -> None:
        if entity is self.player:
            entity.char = "%"
            entity.color = (150, 0, 0)
            self.log("You have died!")
        else:
            self.log(f"{entity.name} dies.")
            self.entities.remove(entity)