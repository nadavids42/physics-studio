"""Registry and mission metadata owned by this simulation slice."""

from physics_playground.missions.models import MissionDefinition, MissionType
from physics_playground.models.simulations import (
    Difficulty,
    LearningMode,
    SimulationDefinition,
    VisualMetadata,
)
from physics_playground.subjects.mechanics.cannonball.physics import PROJECTILE_MODEL_VERSION

SIMULATION = SimulationDefinition(
    id="cannonball",
    title="Cannonball Launcher",
    icon="🎯",
    description="Aim a projectile and compare ideal and drag-filled flight.",
    page_module="physics_playground.subjects.mechanics.cannonball.page",
    mission_group="Cannonball Launcher",
    modes=tuple(LearningMode),
    central_question="Which launch angle sends a cannonball farthest?",
    concepts=("Projectile motion", "Energy", "Air resistance"),
    difficulty=Difficulty.INTERMEDIATE,
    badge_count=4,
    renderer="shared-browser-player",
    model_version=PROJECTILE_MODEL_VERSION,
    simulation_type="Analytical + numerical",
    visual=VisualMetadata(
        "#E53935",
        "#FFEBEE",
        "💥",
        "A cannonball arcing toward a target",
    ),
)

MISSIONS = (
    MissionDefinition(
        id="cannon_predict",
        simulation_id="cannonball",
        title="Guessed the best launch angle",
        description="Predict the ideal maximum-range angle.",
        hints=("Balance upward and horizontal motion.",),
        category=MissionType.EXPLANATION,
        difficulty=Difficulty.BEGINNER,
        prerequisites=(),
        hidden=False,
        completion_rule_id="run:cannon_predict",
        group="Cannonball Launcher",
    ),
    MissionDefinition(
        id="cannon_sweet_spot",
        simulation_id="cannonball",
        title="Fired at the 45° sweet spot",
        description="Run a launch between 43° and 47°.",
        hints=("The ideal range formula contains sin(2θ).",),
        category=MissionType.DISCOVERY,
        difficulty=Difficulty.BEGINNER,
        prerequisites=("cannon_predict",),
        hidden=False,
        completion_rule_id="run:cannon_sweet_spot",
        group="Cannonball Launcher",
    ),
    MissionDefinition(
        id="cannon_bullseye",
        simulation_id="cannonball",
        title="Hit the target",
        description="Land within two meters of the target.",
        hints=(
            "Reuse the target while adjusting speed.",
            "Use range feedback to bracket the target.",
        ),
        category=MissionType.DISCOVERY,
        difficulty=Difficulty.INTERMEDIATE,
        prerequisites=("cannon_predict",),
        hidden=False,
        completion_rule_id="run:cannon_bullseye",
        group="Cannonball Launcher",
    ),
    MissionDefinition(
        id="cannon_moon",
        simulation_id="cannonball",
        title="Fired a cannon on the Moon",
        description="Complete a lunar launch.",
        hints=("Change the world to the Moon.",),
        category=MissionType.DISCOVERY,
        difficulty=Difficulty.BEGINNER,
        prerequisites=("cannon_predict",),
        hidden=False,
        completion_rule_id="run:cannon_moon",
        group="Cannonball Launcher",
    ),
)
