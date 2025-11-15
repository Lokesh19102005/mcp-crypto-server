import asyncio
import time
from typing import Any, Optional

class InMemoryCache:
    def __init__(self, ttl: int = 5):
        self._data = {}
        self.ttl = ttl
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            value, expire = entry
            if expire and expire < time.time():
                del self._data[key]
                return None
            return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        async with self._lock:
            expire = time.time() + (ttl if ttl is not None else self.ttl) if ttl != 0 else None
            self._data[key] = (value, expire)

    async def delete(self, key: str):
        async with self._lock:
            if key in self._data:
                del self._data[key]
