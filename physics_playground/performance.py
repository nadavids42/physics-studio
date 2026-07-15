"""Central numerical validation, computational budgets, and timing records."""
from __future__ import annotations
from collections import deque
from dataclasses import fields,is_dataclass
import math,time
from threading import Lock
from typing import Any,Callable,TypeVar
from functools import wraps
from physics_playground.validation import PhysicsValidationError

MAX_TRAJECTORY_SAMPLES=50_000
MAX_INTEGRATION_STEPS=200_000
MAX_SCAN_POINTS=500
MAX_NOTEBOOK_TRIALS=500
F=TypeVar("F",bound=Callable[...,Any])
_timings=deque(maxlen=200);_lock=Lock()
def validate_finite_parameters(value:Any,prefix="parameters"):
    if is_dataclass(value):
        for item in fields(value):validate_finite_parameters(getattr(value,item.name),f"{prefix}.{item.name}")
    elif isinstance(value,float) and not math.isfinite(value):raise PhysicsValidationError(f"{prefix} must be finite, not {value}.")
def enforce_budget(name,value,maximum):
    if value>maximum:raise PhysicsValidationError(f"{name} requests {value:,} units, above the safe limit of {maximum:,}.")
def recommended_time_step(characteristic_time:float,fraction:float=.01)->float:
    if not math.isfinite(characteristic_time) or characteristic_time<=0:raise PhysicsValidationError("Characteristic time must be finite and positive.")
    return characteristic_time*fraction
def stability_message(actual:float,recommended:float,label="time step"):
    return f"The {label} is {actual/recommended:.1f}× the recommended {recommended:.5g}; reduce it for better conservation." if actual>recommended else None
def record_timing(name,elapsed,cache="computed"):
    with _lock:_timings.append({"name":name,"milliseconds":elapsed*1000,"source":cache,"timestamp":time.time()})
def timed(name):
    def decorator(function):
        @wraps(function)
        def wrapped(*args,**kwargs):
            start=time.perf_counter()
            try:return function(*args,**kwargs)
            finally:record_timing(name,time.perf_counter()-start)
        return wrapped
    return decorator
def timing_snapshot():
    with _lock:return list(_timings)
