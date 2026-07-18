"""Load versioned frontend build artifacts packaged with Physics Studio."""

from functools import lru_cache
from importlib.resources import files


@lru_cache(maxsize=64)
def load_javascript_asset(name: str) -> str:
    """Return a built JavaScript asset by basename."""

    if not name or name != name.rsplit("/", 1)[-1] or not name.endswith(".js"):
        raise ValueError("JavaScript asset names must be plain .js basenames.")
    return files("physics_playground.static.js").joinpath(name).read_text(encoding="utf-8")


def frontend_asset_cache_info():
    """Expose bounded cache diagnostics without exposing cached source strings."""

    return load_javascript_asset.cache_info()
