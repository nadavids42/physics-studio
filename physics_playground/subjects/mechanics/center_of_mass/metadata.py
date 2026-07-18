"""Registry and mission metadata owned by this simulation slice."""

from physics_playground.missions.models import MissionDefinition, MissionType
from physics_playground.models.simulations import (
    Difficulty,
    InteractiveMode,
    SimulationDefinition,
    VisualMetadata,
)

SIMULATION = SimulationDefinition(
    id="center_of_mass",
    title="Center of Mass",
    icon="🎯",
    description="Arrange masses and find the point where the system balances.",
    page_module="physics_playground.subjects.mechanics.center_of_mass.page",
    mission_group="Center of Mass",
    modes=tuple(InteractiveMode),
    central_question="Where is the balance point of several objects?",
    concepts=("Center of mass", "Balance", "Weighted averages"),
    difficulty=Difficulty.BEGINNER,
    badge_count=3,
    renderer="shared-browser-player",
    model_version="center-of-mass-1.0",
    simulation_type="Analytical",
    visual=VisualMetadata(
        "#00897B",
        "#E0F2F1",
        "●",
        "Several masses arranged along a balance line",
    ),
)

MISSIONS = (
    MissionDefinition(
        id="com_predict",
        simulation_id="center_of_mass",
        title="Predicted the balance point",
        description="Predict which way the center of mass shifts.",
        hints=("It moves toward larger masses.",),
        category=MissionType.EXPLANATION,
        difficulty=Difficulty.BEGINNER,
        prerequisites=(),
        hidden=False,
        completion_rule_id="run:com_predict",
        group="Center of Mass",
    ),
    MissionDefinition(
        id="com_origin",
        simulation_id="center_of_mass",
        title="Balanced at the origin",
        description="Put the center of mass within 0.1 m of zero.",
        hints=("Balance mass × position on both sides.",),
        category=MissionType.DISCOVERY,
        difficulty=Difficulty.BEGINNER,
        prerequisites=("com_predict",),
        hidden=False,
        completion_rule_id="run:com_origin",
        group="Center of Mass",
    ),
    MissionDefinition(
        id="com_three",
        simulation_id="center_of_mass",
        title="Balanced three objects",
        description="Complete a run with three positive masses.",
        hints=("Give the optional third object some mass.",),
        category=MissionType.COMPARISON,
        difficulty=Difficulty.INTERMEDIATE,
        prerequisites=("com_predict",),
        hidden=False,
        completion_rule_id="run:com_three",
        group="Center of Mass",
    ),
)
