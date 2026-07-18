"""Verified unit-based formatting retained independently of Streamlit."""


def friendly_speed(meters_per_second: float) -> str:
    """State speed in SI and converted road-speed units without analogies."""

    return f"{meters_per_second:.2f} m/s ({meters_per_second * 3.6:.1f} km/h)"


def friendly_minutes(minutes: float) -> str:
    """State elapsed time without unverifiable activity comparisons."""

    if minutes < 60:
        return f"{minutes:.1f} min"
    hours, remaining = divmod(minutes, 60)
    return f"{int(hours)} h {remaining:.0f} min"
