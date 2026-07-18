"""
Circuit Breaker - Prevents cascade failures
Like Android's Doze mode protecting battery
"""

import asyncio
import time
import logging
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("CircuitBreaker")


class State(Enum):
    CLOSED = "closed"       # Working normally
    OPEN = "open"           # Failed - rejecting calls
    HALF_OPEN = "half_open" # Testing recovery


@dataclass
class CBStats:
    failures: int = 0
    successes: int = 0
    total_calls: int = 0
    total_failures: int = 0
    last_failure: float = 0.0
    last_success: float = 0.0


class CircuitBreaker:
    """
    Stops calling a failing service to prevent system hang.
    Auto-recovers after timeout.
    """

    def __init__(
        self,
        name: str,
        fail_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_needed: int = 2,
        timeout_per_call: float = 15.0
    ):
        self.name = name
        self.fail_threshold = fail_threshold
        self.recovery_timeout = recovery_timeout
        self.success_needed = success_needed
        self.timeout_per_call = timeout_per_call
        self.state = State.CLOSED
        self.stats = CBStats()
        self._half_successes = 0
        self._lock = asyncio.Lock()

    async def call(
        self,
        func: Callable,
        *args,
        fallback: Any = None,
        **kwargs
    ) -> Any:
        """
        Call function through circuit breaker.
        Returns fallback if circuit is OPEN.
        """
        async with self._lock:
            self.stats.total_calls += 1

            if self.state == State.OPEN:
                if self._can_try_reset():
                    self.state = State.HALF_OPEN
                    self._half_successes = 0
                    logger.info(
                        f"⚡ {self.name}: HALF_OPEN (testing)"
                    )
                else:
                    remaining = (
                        self.recovery_timeout
                        - (time.time() - self.stats.last_failure)
                    )
                    logger.debug(
                        f"⚡ {self.name}: OPEN "
                        f"(recovery in {remaining:.0f}s)"
                    )
                    return fallback

        # Execute outside lock
        try:
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.timeout_per_call
                )
            else:
                result = func(*args, **kwargs)

            await self._on_success()
            return result

        except asyncio.TimeoutError:
            await self._on_failure(
                TimeoutError(
                    f"{self.name} timed out "
                    f"after {self.timeout_per_call}s"
                )
            )
            return fallback

        except Exception as e:
            await self._on_failure(e)
            return fallback

    async def _on_success(self):
        async with self._lock:
            self.stats.successes += 1
            self.stats.last_success = time.time()
            self.stats.failures = 0

            if self.state == State.HALF_OPEN:
                self._half_successes += 1
                if self._half_successes >= self.success_needed:
                    self.state = State.CLOSED
                    logger.info(
                        f"✅ {self.name}: CLOSED (recovered)"
                    )

    async def _on_failure(self, error: Exception):
        async with self._lock:
            self.stats.failures += 1
            self.stats.total_failures += 1
            self.stats.last_failure = time.time()

            logger.warning(
                f"⚡ {self.name}: failure #{self.stats.failures} "
                f"- {str(error)[:60]}"
            )

            if self.stats.failures >= self.fail_threshold:
                if self.state != State.OPEN:
                    self.state = State.OPEN
                    logger.error(
                        f"🔴 {self.name}: CIRCUIT OPEN "
                        f"(will retry in {self.recovery_timeout}s)"
                    )

    def _can_try_reset(self) -> bool:
        return (
            time.time() - self.stats.last_failure
            >= self.recovery_timeout
        )

    @property
    def available(self) -> bool:
        return self.state != State.OPEN

    def status(self) -> dict:
        avail_pct = (
            (self.stats.total_calls - self.stats.total_failures)
            / max(self.stats.total_calls, 1) * 100
        )
        return {
            "name": self.name,
            "state": self.state.value,
            "availability": f"{avail_pct:.1f}%",
            "total_calls": self.stats.total_calls,
            "total_failures": self.stats.total_failures,
            "current_failures": self.stats.failures
        }


# -- Global Registry ------------------------------------------

_breakers: dict = {}


def get_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Get or create a named circuit breaker"""
    if name not in _breakers:
        _breakers[name] = CircuitBreaker(name, **kwargs)
    return _breakers[name]


def all_statuses() -> list:
    return [b.status() for b in _breakers.values()]
