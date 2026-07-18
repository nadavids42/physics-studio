"""Registry and mission metadata owned by this simulation slice."""

from physics_playground.missions.models import MissionDefinition, MissionType
from physics_playground.models.simulations import (
    Difficulty,
    LearningMode,
    SimulationDefinition,
    VisualMetadata,
)

SIMULATION = SimulationDefinition(
    id="torque_levers",
    title="Torque and Levers",
    icon="⚖️",
    description="Balance forces around a pivot and build mechanical advantage.",
    page_module="physics_playground.subjects.mechanics.torque_levers.page",
    mission_group="Torque and Levers",
    modes=tuple(LearningMode),
    central_question="How do force and distance combine to turn a lever?",
    concepts=("Torque", "Levers", "Equilibrium"),
    difficulty=Difficulty.BEGINNER,
    badge_count=3,
    renderer="shared-browser-player",
    model_version="lever-1.0",
    simulation_type="Analytical",
    visual=VisualMetadata(
        "#1565C0",
        "#E3F2FD",
        "↔",
        "A beam balancing on a central pivot",
    ),
)

MISSIONS = (
    MissionDefinition(
        id="lever_predict",
        simulation_id="torque_levers",
        title="Predicted which side turns",
        description="Predict the lever direction before running it.",
        hints=("Compare force times distance from the pivot.",),
        category=MissionType.EXPLANATION,
        difficulty=Difficulty.BEGINNER,
        prerequisites=(),
        hidden=False,
        completion_rule_id="run:lever_predict",
        group="Torque and Levers",
    ),
    MissionDefinition(
        id="lever_balance",
        simulation_id="torque_levers",
        title="Balanced the lever",
        description="Make clockwise and counterclockwise torques match.",
        hints=("Set effort force × arm equal to load force × arm.",),
        category=MissionType.DISCOVERY,
        difficulty=Difficulty.BEGINNER,
        prerequisites=("lever_predict",),
        hidden=False,
        completion_rule_id="run:lever_balance",
        group="Torque and Levers",
    ),
    MissionDefinition(
        id="lever_advantage",
        simulation_id="torque_levers",
        title="Built a powerful lever",
        description="Create mechanical advantage of at least three.",
        hints=("Use a long effort arm and short load arm.",),
        category=MissionType.COMPARISON,
        difficulty=Difficulty.INTERMEDIATE,
        prerequisites=("lever_predict",),
        hidden=False,
        completion_rule_id="run:lever_advantage",
        group="Torque and Levers",
    ),
)
