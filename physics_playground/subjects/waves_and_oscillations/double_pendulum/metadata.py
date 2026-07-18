"""Registry and mission metadata owned by this simulation slice."""

from physics_playground.missions.models import MissionDefinition, MissionType
from physics_playground.models.simulations import (
    Difficulty,
    InteractiveMode,
    SimulationDefinition,
    VisualMetadata,
)

SIMULATION = SimulationDefinition(
    id="double_pendulum",
    title="Double Pendulum of Chaos",
    icon="🌀",
    description="Watch a tiny difference grow into completely different motion.",
    page_module="physics_playground.subjects.waves_and_oscillations.double_pendulum.page",
    mission_group="Double Pendulum of Chaos",
    modes=tuple(InteractiveMode),
    central_question="How can nearly identical starts produce different futures?",
    concepts=("Chaos", "Nonlinear dynamics", "Energy"),
    difficulty=Difficulty.ADVANCED,
    badge_count=3,
    renderer="shared-browser-player",
    model_version="double-pendulum-rk4-2.0",
    simulation_type="Numerical",
    visual=VisualMetadata(
        "#8E24AA",
        "#F3E5F5",
        "〽️",
        "Two nearly identical double pendulums",
    ),
)

MISSIONS = (
    MissionDefinition(
        id="chaos_predict",
        simulation_id="double_pendulum",
        title="Guessed what happens to nearly-identical swings",
        description="Predict sensitive dependence on initial conditions.",
        hints=("Tiny differences can grow in nonlinear systems.",),
        category=MissionType.EXPLANATION,
        difficulty=Difficulty.INTERMEDIATE,
        prerequisites=(),
        hidden=False,
        completion_rule_id="run:chaos_predict",
        group="Double Pendulum of Chaos",
    ),
    MissionDefinition(
        id="chaos_diverge",
        simulation_id="double_pendulum",
        title="Watched two close swings split apart",
        description="Produce more than 0.5 m final separation.",
        hints=(
            "Give the systems a tiny nonzero perturbation.",
            "Try energetic starting angles and more time.",
        ),
        category=MissionType.DISCOVERY,
        difficulty=Difficulty.INTERMEDIATE,
        prerequisites=("chaos_predict",),
        hidden=False,
        completion_rule_id="run:chaos_diverge",
        group="Double Pendulum of Chaos",
    ),
    MissionDefinition(
        id="chaos_flip",
        simulation_id="double_pendulum",
        title="Made the second arm flip all the way around",
        description="Drive arm two beyond π radians.",
        hints=("Use a high-energy initial configuration.",),
        category=MissionType.DISCOVERY,
        difficulty=Difficulty.ADVANCED,
        prerequisites=("chaos_predict",),
        hidden=True,
        completion_rule_id="run:chaos_flip",
        group="Double Pendulum of Chaos",
    ),
)
