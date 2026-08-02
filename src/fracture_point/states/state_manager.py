from __future__ import annotations

from fracture_point.states.base import GameState

class StateManager:
    """
    Holds the stack of active GameStates and enforces the link graph.

     -push(name): stacks a new state on top of the current one (e.g. opening
     the inventory over Playing). The state underneath stays alive and resumes
     when this one is popped
     -replace(name): swaps the current state out entirely (e.g. leaving Playing
     for a Hub screen between runs) - nothing to resume by popping.

    Both check the current stat's `linked_states` first, so a state can only move
    to states it explicitly declares a link to.
    """

    def __init__(self):
        self._registry: dict[str, GameState] = {}
        self._stack: list[GameState] = []

    def register(self, state: GameState) -> None:
        self._registry[state.name] = state

    @property
    def current(self) -> GameState:
        return self._stack[-1]

    def start(self, name: str) -> None:
        """
        Sets the very first state. Only valid on an empty stack.
        """
        if self._stack:
            raise RuntimeError("start() can only be called before any stat is active.")
        state = self._registry[name]
        self._stack.append(state)
        state.on_enter()

    def push(self, name: str) -> None:
        self._check_link(name)
        state = self._registry[name]
        self._stack.append(state)
        state.on_enter()

    def pop(self) -> None:
        if len(self._stack) <= 1:
            raise RuntimeError("Cannot pop the last remaining state.")
        old = self._stack.pop()
        old.on_exit()

    def replace(self, name: str) -> None:
        self._check_link(name)
        old = self._stack.pop()
        old.on_exit()
        state = self._registry[name]
        self._stack.append(state)
        state.on_enter()

    def _check_link(self, name: str) -> None:
        if name not in self._registry:
            raise ValueError(f"no registered state named '{name}'.")
        if name not in self.current.linked_states:
            raise ValueError(f"'{self.current.name}' has no link to '{name}'.")