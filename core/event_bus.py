import asyncio
from collections import defaultdict
from typing import Callable, Any


class EventBus:
    """Simple asyncio pub/sub. Handlers are async callables."""

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._queue: asyncio.Queue = asyncio.Queue()

    def subscribe(self, event_type: str, handler: Callable) -> None:
        self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: Callable) -> None:
        self._subscribers["*"].append(handler)

    async def publish(self, event_type: str, payload: Any) -> None:
        await self._queue.put((event_type, payload))

    async def run(self) -> None:
        """Drain the queue and dispatch to handlers. Run as background task."""
        while True:
            event_type, payload = await self._queue.get()
            handlers = self._subscribers.get(event_type, []) + self._subscribers.get("*", [])
            for handler in handlers:
                try:
                    await handler(event_type, payload)
                except Exception as e:
                    print(f"[EventBus] Handler error ({event_type}): {e}")
            self._queue.task_done()


# Singleton
event_bus = EventBus()
