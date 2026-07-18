"""Compatibility import for the shared-player embedding adapter.

New code should import from :mod:`physics_playground.canvas.embed`.
"""

from physics_playground.canvas.embed import show

__all__ = ["show"]
