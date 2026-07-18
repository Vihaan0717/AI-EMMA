"""
Rate Limiter - Token Bucket Algorithm
Prevents resource exhaustion like iOS memory pressure
"""

import asyncio
import time
import logging
from typing import Dict

logger = logging.getLogger("RateLimiter")


class RateLimiter:
    """
    Token bucket rate limiter.
    Smooth and burst-tolerant.
    """

    def __init__(
        self,
        name: str,
        max_calls: int = 10,
        period: float = 1.0,
        burst: int = None
    ):
        self.name = name
        self.max_calls = max_calls
        self.period = period
        self.burst = burst or (max_calls * 2)
        self.tokens = float(self.burst)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
        self.accepted = 0
        self.rejected = 0
        self.waited = 0

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.last_refill = now
        gain = elapsed * (self.max_calls / self.period)
        self.tokens = min(float(self.burst), self.tokens + gain)

    async def acquire(self, tokens: int = 1) -> bool:
        """Non-blocking acquire. Returns True if allowed."""
        async with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.accepted += 1
                return True
            self.rejected += 1
            return False

    async def wait(
        self, tokens: int = 1, timeout: float = 30.0
    ) -> bool:
        """Blocking acquire with timeout."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if await self.acquire(tokens):
                return True
            self.waited += 1
            await asyncio.sleep(0.05)
        logger.warning(
            f"🚦 {self.name}: wait timeout ({timeout}s)"
        )
        return False

    def status(self) -> dict:
        return {
            "name": self.name,
            "tokens": int(self.tokens),
            "accepted": self.accepted,
            "rejected": self.rejected,
            "waited": self.waited
        }


# -- Global Registry ------------------------------------------

_limiters: Dict[str, RateLimiter] = {}

DEFAULTS = {
    "ollama":        {"max_calls": 5,  "period": 1.0},
    "gemini":        {"max_calls": 10, "period": 1.0},
    "whatsapp_send": {"max_calls": 3,  "period": 1.0},
    "telegram_send": {"max_calls": 15, "period": 1.0},
    "search":        {"max_calls": 2,  "period": 1.0},
    "tts":           {"max_calls": 3,  "period": 1.0},
    "screenshot":    {"max_calls": 1,  "period": 15.0},
    "biometric":     {"max_calls": 1,  "period": 5.0},
    "memory_write":  {"max_calls": 20, "period": 1.0},
    "embedding":     {"max_calls": 5,  "period": 1.0},
}


def get_limiter(name: str, **kwargs) -> RateLimiter:
    if name not in _limiters:
        cfg = {**DEFAULTS.get(name, {}), **kwargs}
        _limiters[name] = RateLimiter(name, **cfg)
    return _limiters[name]


def all_statuses() -> list:
    return [l.status() for l in _limiters.values()]
