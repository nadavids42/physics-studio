"""Typed design tokens for scientific illustrations and application UI.

Colors are named for meaning, not for the simulation that first uses them.
Renderers should consume :func:`theme_payload` rather than embedding constants.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

ThemeName = Literal["light", "dark", "auto"]


@dataclass(frozen=True, slots=True)
class SpacingTokens:
    xxs: int = 2
    xs: int = 4
    sm: int = 8
    md: int = 12
    lg: int = 16
    xl: int = 24
    xxl: int = 32
    xxxl: int = 48


@dataclass(frozen=True, slots=True)
class ShapeTokens:
    radius_small: int = 6
    radius_medium: int = 10
    radius_large: int = 16
    radius_panel: int = 20
    radius_pill: int = 999
    line_hairline: float = 1
    line_regular: float = 1.5
    line_emphasis: float = 2.5
    line_vector: float = 3
    object_outline: float = 2
    trail_opacity: float = 0.24
    grid_opacity: float = 0.16
    shadow_low: str = "0 2px 8px rgba(15, 23, 42, .10)"
    shadow_medium: str = "0 8px 24px rgba(15, 23, 42, .14)"
    shadow_high: str = "0 18px 48px rgba(15, 23, 42, .18)"


@dataclass(frozen=True, slots=True)
class TypographyTokens:
    family_ui: str = (
        "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    )
    family_equation: str = "'STIX Two Math', 'Cambria Math', Georgia, serif"
    family_numeric: str = "'IBM Plex Mono', 'SFMono-Regular', Consolas, monospace"
    heading_large: int = 30
    heading_medium: int = 24
    heading_small: int = 19
    body: int = 16
    label: int = 14
    annotation: int = 13
    helper: int = 12
    graph_axis: int = 12
    tooltip: int = 13
    weight_regular: int = 400
    weight_medium: int = 550
    weight_semibold: int = 650
    line_height_tight: float = 1.2
    line_height_body: float = 1.55


@dataclass(frozen=True, slots=True)
class MotionTokens:
    instant_ms: int = 0
    fast_ms: int = 120
    standard_ms: int = 200
    deliberate_ms: int = 320
    emphasis_ms: int = 480
    ease_standard: str = "cubic-bezier(.2, 0, 0, 1)"
    ease_enter: str = "cubic-bezier(0, 0, .2, 1)"
    ease_exit: str = "cubic-bezier(.4, 0, 1, 1)"


@dataclass(frozen=True, slots=True)
class ResponsiveTokens:
    mobile_max_px: int = 480
    tablet_max_px: int = 820
    content_max_px: int = 1100
    canvas_min_height_px: int = 180
    control_target_px: int = 44
    desktop_gutter_px: int = 24
    tablet_gutter_px: int = 16
    mobile_gutter_px: int = 10


@dataclass(frozen=True, slots=True)
class ThemeTokens:
    name: Literal["light", "dark"]
    canvas: str
    surface: str
    surface_raised: str
    surface_muted: str
    border: str
    grid: str
    text: str
    text_muted: str
    text_inverse: str
    accent: str
    accent_soft: str
    selected: str
    focus: str
    warning: str
    error: str
    success: str
    velocity: str
    acceleration: str
    net_force: str
    gravity: str
    normal_force: str
    friction: str
    tension: str
    electric_field: str
    magnetic_field: str
    displacement: str
    energy: str
    trajectory: str
    uncertainty: str
    graph_1: str
    graph_2: str
    graph_3: str
    graph_4: str
    graph_5: str
    graph_6: str
    graph_7: str

    @property
    def graph_colors(self) -> tuple[str, ...]:
        return (
            self.graph_1,
            self.graph_2,
            self.graph_3,
            self.graph_4,
            self.graph_5,
            self.graph_6,
            self.graph_7,
        )


SPACING = SpacingTokens()
SHAPE = ShapeTokens()
TYPOGRAPHY = TypographyTokens()
MOTION = MotionTokens()
RESPONSIVE = ResponsiveTokens()

LIGHT_THEME = ThemeTokens(
    "light",
    canvas="#F7FAFC",
    surface="#FFFFFF",
    surface_raised="#FFFFFF",
    surface_muted="#EAF0F6",
    border="#B8C5D1",
    grid="#526577",
    text="#152536",
    text_muted="#526577",
    text_inverse="#FFFFFF",
    accent="#1769AA",
    accent_soft="#DCEEFF",
    selected="#7C3AED",
    focus="#005FCC",
    warning="#9A5B00",
    error="#B42318",
    success="#157347",
    velocity="#087EA4",
    acceleration="#7C3AED",
    net_force="#C2410C",
    gravity="#9A3412",
    normal_force="#166534",
    friction="#8A4B08",
    tension="#6D28D9",
    electric_field="#006D77",
    magnetic_field="#7E22CE",
    displacement="#0F766E",
    energy="#B45309",
    trajectory="#1769AA",
    uncertainty="#64748B",
    graph_1="#0072B2",
    graph_2="#D55E00",
    graph_3="#00875A",
    graph_4="#A23B72",
    graph_5="#8A5A00",
    graph_6="#5B55A5",
    graph_7="#34495E",
)

DARK_THEME = ThemeTokens(
    "dark",
    canvas="#0D1726",
    surface="#142235",
    surface_raised="#1B2C42",
    surface_muted="#21364E",
    border="#6F8499",
    grid="#A9B8C7",
    text="#F3F7FB",
    text_muted="#C0CEDA",
    text_inverse="#0D1726",
    accent="#73B7F2",
    accent_soft="#193D5C",
    selected="#C4A7FF",
    focus="#9ACBFF",
    warning="#FFD166",
    error="#FF8A80",
    success="#63D6A0",
    velocity="#56C8E8",
    acceleration="#C4A7FF",
    net_force="#FF9B73",
    gravity="#FFB08A",
    normal_force="#7DDEA5",
    friction="#F2C46D",
    tension="#D0B5FF",
    electric_field="#67D5D0",
    magnetic_field="#D0A5FF",
    displacement="#65D6C3",
    energy="#FFD166",
    trajectory="#73B7F2",
    uncertainty="#B4C2D0",
    graph_1="#56B4E9",
    graph_2="#FF9F68",
    graph_3="#63D6A0",
    graph_4="#E69AC7",
    graph_5="#FFD166",
    graph_6="#B8AEFF",
    graph_7="#E4ECF3",
)


def theme_payload(theme: ThemeTokens) -> dict[str, object]:
    """Return stable camelCase-free JSON-ready tokens for Python and JS renderers."""
    return {
        "colors": asdict(theme),
        "spacing": asdict(SPACING),
        "shape": asdict(SHAPE),
        "typography": asdict(TYPOGRAPHY),
        "motion": asdict(MOTION),
        "responsive": asdict(RESPONSIVE),
    }
