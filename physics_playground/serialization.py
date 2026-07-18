"""Stable JSON serialization for contracts and trial history."""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, TypeVar, cast, get_args, get_origin, get_type_hints

import numpy as np

from physics_playground.contracts import JsonValue

T = TypeVar("T")


def to_jsonable(value: Any) -> JsonValue:
    """Recursively convert contract values into JSON-compatible primitives."""

    if is_dataclass(value):
        return {item.name: to_jsonable(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Enum):
        return cast(JsonValue, value.value)
    if isinstance(value, MappingProxyType):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return cast(JsonValue, value.tolist())
    if isinstance(value, np.generic):
        return cast(JsonValue, value.item())
    if isinstance(value, Path):
        return str(value)
    return cast(JsonValue, value)


def dumps(value: Any, *, indent: int | None = None) -> str:
    """Serialize a contract value using strict JSON (NaN is rejected)."""

    return json.dumps(to_jsonable(value), indent=indent, allow_nan=False, sort_keys=True)


def dataclass_from_dict(model: type[T], payload: dict[str, Any]) -> T:
    """Rebuild a typed parameter dataclass from JSON-compatible notebook data.

    Nested dataclasses, enums, tuples, lists and optional values are restored
    recursively. Unknown fields are rejected so an old or corrupt trial cannot
    silently alter a model after a schema change.
    """
    if not is_dataclass(model):
        raise TypeError(f"{model!r} is not a dataclass type")
    hints = get_type_hints(model)
    known = {item.name for item in fields(model)}
    unknown = set(payload) - known
    if unknown:
        raise ValueError(f"Unknown {model.__name__} fields: {', '.join(sorted(unknown))}")

    def restore(annotation: Any, value: Any) -> Any:
        if value is None:
            return None
        origin = get_origin(annotation)
        arguments = get_args(annotation)
        if origin in (tuple, list):
            subtype = arguments[0] if arguments else Any
            values = [restore(subtype, item) for item in value]
            return tuple(values) if origin is tuple else values
        if origin is not None and type(None) in arguments:
            subtype = next(item for item in arguments if item is not type(None))
            return restore(subtype, value)
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            return annotation(value)
        if isinstance(annotation, type) and is_dataclass(annotation):
            return dataclass_from_dict(annotation, value)
        return value

    return model(**{name: restore(hints.get(name, Any), value) for name, value in payload.items()})
