"""Pure mission evidence for Planet Launcher."""

from physics_playground.contracts import MissionEvaluation
from physics_playground.subjects.mechanics.orbital_gravity.physics import OrbitOutcome, OrbitResult


def evaluate_orbit_missions(r: OrbitResult):
    return (
        MissionEvaluation(
            "orbit_crash", r.outcome == OrbitOutcome.CRASH, "Crash into the central body."
        ),
        MissionEvaluation(
            "orbit_escape", r.outcome == OrbitOutcome.ESCAPE, "Escape to deep space."
        ),
        MissionEvaluation(
            "orbit_egg",
            r.outcome == OrbitOutcome.ELLIPTICAL and r.eccentricity > 0.15,
            "Create an egg-shaped orbit.",
        ),
    )
