"""Central numerical validation, computational budgets, and timing records."""

from __future__ import annotations

import math
import time
from collections import deque
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import fields, is_dataclass
from functools import wraps
from threading import Lock
from typing import Any, ParamSpec, TypedDict, TypeVar

from physics_playground.validation import PhysicsValidationError

MAX_TRAJECTORY_SAMPLES = 50_000
MAX_INTEGRATION_STEPS = 200_000
MAX_SCAN_POINTS = 500
MAX_NOTEBOOK_TRIALS = 500
P = ParamSpec("P")
T = TypeVar("T")


class TimingRecord(TypedDict):
    name: str
    milliseconds: float
    source: str
    timestamp: float


_timings: deque[TimingRecord] = deque(maxlen=200)
_lock = Lock()


def validate_finite_parameters(value: Any, prefix: str = "parameters") -> None:
    if is_dataclass(value):
        for item in fields(value):
            validate_finite_parameters(getattr(value, item.name), f"{prefix}.{item.name}")
    elif isinstance(value, float) and not math.isfinite(value):
        raise PhysicsValidationError(f"{prefix} must be finite, not {value}.")


def enforce_budget(name: str, value: int, maximum: int) -> None:
    if value > maximum:
        raise PhysicsValidationError(
            f"{name} requests {value:,} units, above the safe limit of {maximum:,}."
        )


def recommended_time_step(characteristic_time: float, fraction: float = 0.01) -> float:
    if not math.isfinite(characteristic_time) or characteristic_time <= 0:
        raise PhysicsValidationError("Characteristic time must be finite and positive.")
    return characteristic_time * fraction


def stability_message(actual: float, recommended: float, label: str = "time step") -> str | None:
    return (
        f"The {label} is {actual / recommended:.1f}× the recommended {recommended:.5g}; reduce it for better conservation."
        if actual > recommended
        else None
    )


def record_timing(name: str, elapsed: float, cache: str = "computed") -> None:
    with _lock:
        _timings.append(
            {
                "name": name,
                "milliseconds": elapsed * 1000,
                "source": cache,
                "timestamp": time.time(),
            }
        )


def timed(name: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(function: Callable[P, T]) -> Callable[P, T]:
        @wraps(function)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            start = time.perf_counter()
            try:
                return function(*args, **kwargs)
            finally:
                record_timing(name, time.perf_counter() - start)

        return wrapped

    return decorator


@contextmanager
def timing_block(name: str, source: str = "render") -> Iterator[None]:
    """Record a bounded timing sample for a page or presentation operation."""

    start = time.perf_counter()
    try:
        yield
    finally:
        record_timing(name, time.perf_counter() - start, source)


def timing_snapshot() -> list[TimingRecord]:
    with _lock:
        return list(_timings)
