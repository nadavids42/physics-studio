"""Renderer-independent contracts for optional interactive scientific charts."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from enum import StrEnum


class ChartLineStyle(StrEnum):
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"


class ChartMarker(StrEnum):
    CIRCLE = "circle"
    SQUARE = "square"
    TRIANGLE = "triangle"


@dataclass(frozen=True, slots=True)
class ChartAxis:
    label: str
    unit: str = ""

    @property
    def display_label(self) -> str:
        return f"{self.label} ({self.unit})" if self.unit else self.label


@dataclass(frozen=True, slots=True)
class InteractiveSeries:
    id: str
    label: str
    x: tuple[float, ...]
    y: tuple[float, ...]
    semantic_color: str = "graph_1"
    line_style: ChartLineStyle = ChartLineStyle.SOLID
    marker: ChartMarker = ChartMarker.CIRCLE

    def validate(self) -> None:
        if not self.id or not self.label or len(self.x) != len(self.y) or not self.x:
            raise ValueError("Chart series require an ID, label, and equal nonempty coordinates.")
        if not all(math.isfinite(value) for value in (*self.x, *self.y)):
            raise ValueError("Interactive chart coordinates must be finite.")


@dataclass(frozen=True, slots=True)
class InteractiveChart:
    id: str
    title: str
    description: str
    x_axis: ChartAxis
    y_axis: ChartAxis
    series: tuple[InteractiveSeries, ...]
    hover: bool = True
    linked_highlight: bool = True
    zoom: bool = False
    table: bool = True

    def validate(self) -> None:
        if not self.id or not self.title or not self.description:
            raise ValueError("Interactive charts require ID, title, and textual description.")
        if not self.x_axis.label or not self.y_axis.label or not self.series:
            raise ValueError("Interactive charts require labeled axes and at least one series.")
        for item in self.series:
            item.validate()
        if len({item.id for item in self.series}) != len(self.series):
            raise ValueError("Interactive chart series IDs must be unique.")

    def to_dict(self) -> dict[str, object]:
        self.validate()
        payload = asdict(self)
        payload["x_axis"]["display_label"] = self.x_axis.display_label
        payload["y_axis"]["display_label"] = self.y_axis.display_label
        return payload
