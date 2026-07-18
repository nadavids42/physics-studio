"""Kid-friendly comparisons retained independently of Streamlit."""

SPEED_REFERENCES = (
    ("a rocket going to space", 7_800.0),
    ("a jet plane", 250.0),
    ("a race car", 90.0),
    ("a cheetah at full sprint", 30.0),
    ("a kid sprinting", 7.0),
    ("a grown-up walking", 1.4),
)


def friendly_speed(meters_per_second: float) -> str:
    for name, reference_speed in SPEED_REFERENCES:
        ratio = meters_per_second / reference_speed
        if ratio >= 1.0:
            return (
                f"about {ratio:.0f}× faster than {name}"
                if ratio >= 1.8
                else f"about as fast as {name}"
            )
    return "slower than a grown-up walking"


def friendly_minutes(minutes: float) -> str:
    if minutes < 2:
        return "shorter than brushing your teeth"
    if minutes < 12:
        return "about one recess"
    if minutes < 35:
        return "about one episode of a cartoon"
    if minutes < 70:
        return "about one soccer game half... plus snacks"
    if minutes < 150:
        return "about one whole movie"
    return "longer than a movie — bring a book"
