"""Registry and mission metadata owned by this simulation slice."""

from physics_playground.missions.models import MissionDefinition, MissionType
from physics_playground.models.simulations import (
    Difficulty,
    InteractiveMode,
    SimulationDefinition,
    VisualMetadata,
)

SIMULATION = SimulationDefinition(
    id="inclined_plane",
    title="Inclined Plane",
    icon="📐",
    description="Explore how ramp angle and friction decide whether a block slides.",
    page_module="physics_playground.subjects.mechanics.inclined_plane.page",
    mission_group="Inclined Plane",
    modes=tuple(InteractiveMode),
    central_question="When does gravity overcome friction on a ramp?",
    concepts=("Forces", "Friction", "Acceleration"),
    difficulty=Difficulty.BEGINNER,
    badge_count=3,
    renderer="shared-browser-player",
    model_version="inclined-plane-1.0",
    simulation_type="Analytical",
    visual=VisualMetadata(
        "#FB8C00",
        "#FFF3E0",
        "▰",
        "A block resting on an inclined ramp",
    ),
)

MISSIONS = (
    MissionDefinition(
        id="incline_predict",
        simulation_id="inclined_plane",
        title="Predicted whether the block slides",
        description="Predict motion before running the ramp.",
        hints=("Compare downhill gravity with maximum static friction.",),
        category=MissionType.EXPLANATION,
        difficulty=Difficulty.BEGINNER,
        prerequisites=(),
        hidden=False,
        completion_rule_id="run:incline_predict",
        group="Inclined Plane",
    ),
    MissionDefinition(
        id="incline_slide",
        simulation_id="inclined_plane",
        title="Made the block slide",
        description="Create a setup where gravity defeats friction.",
        hints=("Raise the angle or lower friction.",),
        category=MissionType.DISCOVERY,
        difficulty=Difficulty.BEGINNER,
        prerequisites=("incline_predict",),
        hidden=False,
        completion_rule_id="run:incline_slide",
        group="Inclined Plane",
    ),
    MissionDefinition(
        id="incline_threshold",
        simulation_id="inclined_plane",
        title="Found the slipping threshold",
        description="Run within two degrees of the critical angle.",
        hints=("The threshold satisfies tan(angle) = static friction.",),
        category=MissionType.COMPARISON,
        difficulty=Difficulty.INTERMEDIATE,
        prerequisites=("incline_predict",),
        hidden=False,
        completion_rule_id="run:incline_threshold",
        group="Inclined Plane",
    ),
)
