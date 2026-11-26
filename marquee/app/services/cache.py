"""Small in-process TTL cache. Swap for Redis if the app runs on several workers."""
from __future__ import annotations

import threading
import time
from typing import Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    def __init__(self, ttl_seconds: int, max_items: int = 256):
        self._ttl = ttl_seconds
        self._max = max_items
        self._items: dict[str, tuple[float, T]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> T | None:
        with self._lock:
            entry = self._items.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at < time.monotonic():
                del self._items[key]
                return None
            return value

    def set(self, key: str, value: T) -> None:
        with self._lock:
            if len(self._items) >= self._max:
                oldest = min(self._items, key=lambda k: self._items[k][0])
                del self._items[oldest]
            self._items[key] = (time.monotonic() + self._ttl, value)
