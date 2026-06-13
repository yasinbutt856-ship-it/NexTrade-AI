import asyncio
import time
from collections import deque


class RateLimiter:
    def __init__(self, max_per_second: int = 20):
        self.max_per_second = max_per_second
        self._tokens = deque[float]()

    async def acquire(self) -> None:
        now = time.monotonic()
        while self._tokens and self._tokens[0] <= now - 1.0:
            self._tokens.popleft()
        if len(self._tokens) >= self.max_per_second:
            sleep_time = self._tokens[0] - (now - 1.0)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        self._tokens.append(time.monotonic())
