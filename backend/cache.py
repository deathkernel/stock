"""Small in-process TTL cache with request de-duplication.

This is intentionally process-local. It reduces repeated provider/ML work for
single-instance deployments; distributed deployments should use Redis or an
equivalent shared cache later.
"""
from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any


class TTLCache:
    def __init__(self, ttl_seconds: int = 900, max_entries: int = 256) -> None:
        self.ttl_seconds = max(0, ttl_seconds)
        self.max_entries = max(1, max_entries)
        self._items: dict[str, tuple[float, Any]] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._guard = asyncio.Lock()
        self.hits = 0
        self.misses = 0

    def _get(self, key: str) -> Any | None:
        item = self._items.get(key)
        if item is None:
            return None
        expires_at, value = item
        if expires_at <= time.monotonic():
            self._items.pop(key, None)
            return None
        return value

    async def get_or_set(self, key: str, factory: Callable[[], Awaitable[Any]]) -> Any:
        if self.ttl_seconds <= 0:
            self.misses += 1
            return await factory()

        cached = self._get(key)
        if cached is not None:
            self.hits += 1
            return cached

        async with self._guard:
            lock = self._locks.setdefault(key, asyncio.Lock())

        async with lock:
            cached = self._get(key)
            if cached is not None:
                self.hits += 1
                return cached

            self.misses += 1
            value = await factory()
            if len(self._items) >= self.max_entries:
                oldest = min(self._items, key=lambda item: self._items[item][0])
                self._items.pop(oldest, None)
            self._items[key] = (time.monotonic() + self.ttl_seconds, value)
            return value

    def stats(self) -> dict[str, int | float]:
        total = self.hits + self.misses
        return {
            "entries": len(self._items),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / total, 4) if total else 0.0,
        }


research_cache = TTLCache()
