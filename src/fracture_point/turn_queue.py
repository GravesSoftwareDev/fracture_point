from __future__ import annotations

import heapq
import itertools

class TurnQueue:
    """
    A time-based scheduler for turn order.

    Each entity has a "next action time" = whoever has the lowest time goes next.
    After acting, an entity is rescheduled at current_time + action_cost, so faster
    entities (lower action_cost) naturally get more turns over time than slower ones.

    Uses a min-heap. intertools.count() breaks ties between entities scheduled at the
    same time, so heapq never has to compare entity objects directly.
    """

    def __init__(self):
        self._heap: list[tuple[int, int, object]] = []
        self._counter = itertools.count()

    def schedule(self, entity: object, time: int) -> None:
        heapq.heappush(self._heap, (time, next(self._counter), entity))

    def pop_next(self) -> tuple[object, int]:
        time, _, entity = heapq.heappop(self._heap)
        return entity, time

    def __len__(self) -> int:
        return len(self._heap)