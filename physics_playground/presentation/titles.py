"""Audience-neutral scientific labels for the shared application shell."""

from physics_playground.models.simulations import SimulationDefinition

DESCRIPTIVE_TITLES = {
    "cannonball": "Cannonball Launcher — Projectile Motion",
    "bumper_cars": "Bumper Cars — One-Dimensional Collisions",
    "boing": "Boing Machine — Spring Oscillation",
    "pendulum": "Swing Machine — Pendulum Motion",
}


def scientific_title(definition: SimulationDefinition) -> str:
    """Pair a playful name with its scientific subject where needed."""

    return DESCRIPTIVE_TITLES.get(definition.id, definition.title)
