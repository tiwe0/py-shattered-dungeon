import heapq
from dungeon.action import TimeManagerActionSuspend
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from dungeon.actor import Actor
    from dungeon.engine import Engine


class TimeManager:
    """单例."""
    _instance: 'Optional[TimeManager]' = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.activated_entities = []
        heapq.heapify(self.activated_entities)
        self.is_busy = False
        self.engine: 'Optional[Engine]' = None

    def add_actor(self, actor: 'Actor'):
        heapq.heappush(self.activated_entities, actor)
        actor.time_manager = self

    def run(self):
        while True:
            actor = heapq.heappop(self.activated_entities)
            actor.fetch_action()
            if isinstance(actor.current_action, TimeManagerActionSuspend):
                heapq.heappush(self.activated_entities, actor)
                return
            actor.act()
            heapq.heappush(self.activated_entities, actor)
