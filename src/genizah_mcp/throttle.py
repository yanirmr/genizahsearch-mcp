"""Small async token buckets, one for each allowed upstream operation."""

import asyncio
import time


class TokenBucket:
    def __init__(self, rpm: int, burst: int) -> None:
        self.rate = rpm / 60.0
        self.capacity = float(burst)
        self.tokens = float(burst)
        self.updated = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self) -> float:
        """Acquire one token and return total waited seconds."""
        waited = 0.0
        while True:
            async with self.lock:
                now = time.monotonic()
                self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
                self.updated = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return waited
                delay = (1 - self.tokens) / self.rate
            await asyncio.sleep(delay)
            waited += delay
