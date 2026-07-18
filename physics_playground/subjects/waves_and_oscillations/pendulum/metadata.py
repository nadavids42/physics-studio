"""Registry and mission metadata owned by this simulation slice."""

from physics_playground.missions.models import MissionDefinition, MissionType
from physics_playground.models.simulations import (
    Difficulty,
    InteractiveMode,
    SimulationDefinition,
    VisualMetadata,
)

SIMULATION = SimulationDefinition(
    id="pendulum",
    title="The Swing Machine",
    icon="🎢",
    description="Explore how length, gravity, and angle change a swing.",
    page_module="physics_playground.subjects.waves_and_oscillations.pendulum.page",
    mission_group="The Swing Machine",
    modes=tuple(InteractiveMode),
    central_question="What controls how long a swing takes?",
    concepts=("Oscillation", "Gravity", "Approximation"),
    difficulty=Difficulty.BEGINNER,
    badge_count=3,
    renderer="shared-browser-player",
    model_version="pendulum-2.0",
    simulation_type="Analytical + numerical",
    visual=VisualMetadata(
        "#43A047",
        "#E8F5E9",
        "●",
        "A pendulum swinging from a support",
    ),
)

MISSIONS = (
    MissionDefinition(
        id="pend_predict",
        simulation_id="pendulum",
        title="Guessed the swing secret",
        description="Predict the small-angle period behavior.",
        hints=("Think about pendulum clocks.",),
        category=MissionType.EXPLANATION,
        difficulty=Difficulty.BEGINNER,
        prerequisites=(),
        hidden=False,
        completion_rule_id="run:pend_predict",
        group="The Swing Machine",
    ),
    MissionDefinition(
        id="pend_four",
        simulation_id="pendulum",
        title="Built a perfect 4-second swing",
        description="Create a period between 3.9 and 4.1 seconds.",
        hints=("Period grows with rope length.", "Try changing length or gravity."),
        category=MissionType.DISCOVERY,
        difficulty=Difficulty.INTERMEDIATE,
        prerequisites=("pend_predict",),
        hidden=False,
        completion_rule_id="run:pend_four",
        group="The Swing Machine",
    ),
    MissionDefinition(
        id="pend_moon",
        simulation_id="pendulum",
        title="Went swinging on the Moon",
        description="Run a pendulum using lunar gravity.",
        hints=("Change the world to the Moon.",),
        category=MissionType.DISCOVERY,
        difficulty=Difficulty.BEGINNER,
        prerequisites=("pend_predict",),
        hidden=False,
        completion_rule_id="run:pend_moon",
        group="The Swing Machine",
    ),
)
