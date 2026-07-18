"""Registry and mission metadata owned by this simulation slice."""

from physics_playground.missions.models import MissionDefinition, MissionType
from physics_playground.models.simulations import (
    Difficulty,
    InteractiveMode,
    SimulationDefinition,
    VisualMetadata,
)

SIMULATION = SimulationDefinition(
    id="earth_tunnel",
    title="The Big Fall",
    icon="🕳️",
    description="Fall through a tunnel across an idealized planet.",
    page_module="physics_playground.subjects.mechanics.earth_tunnel.page",
    mission_group="The Big Fall",
    modes=tuple(InteractiveMode),
    central_question="How long would it take to fall through an entire planet?",
    concepts=("Gravity", "Simple harmonic motion", "Energy"),
    difficulty=Difficulty.INTERMEDIATE,
    badge_count=3,
    renderer="shared-browser-player",
    model_version="tunnel-2.0",
    simulation_type="Analytical + numerical",
    visual=VisualMetadata(
        "#7E57C2",
        "#EDE7F6",
        "🌍",
        "A traveler falling through a planet",
    ),
)

MISSIONS = (
    MissionDefinition(
        id="tunnel_predict",
        simulation_id="earth_tunnel",
        title="Guessed how long the Big Fall takes",
        description="Predict the ideal Earth-tunnel travel time.",
        hints=(
            "Think in minutes, not hours.",
            "The motion behaves like a planet-sized oscillator.",
        ),
        category=MissionType.EXPLANATION,
        difficulty=Difficulty.BEGINNER,
        prerequisites=(),
        hidden=False,
        completion_rule_id="run:tunnel_predict",
        group="The Big Fall",
    ),
    MissionDefinition(
        id="tunnel_halfway",
        simulation_id="earth_tunnel",
        title="Solved the Halfway Mystery",
        description="Run a fall beginning halfway down.",
        hints=("Change the starting point.", "Distance changes, but so does maximum speed."),
        category=MissionType.COMPARISON,
        difficulty=Difficulty.BEGINNER,
        prerequisites=("tunnel_predict",),
        hidden=False,
        completion_rule_id="run:tunnel_halfway",
        group="The Big Fall",
    ),
    MissionDefinition(
        id="tunnel_speedy",
        simulation_id="earth_tunnel",
        title="Made the fall take under 20 minutes",
        description="Design a fast custom planet.",
        hints=("Use a custom planet.", "Try a smaller radius and stronger gravity."),
        category=MissionType.DISCOVERY,
        difficulty=Difficulty.INTERMEDIATE,
        prerequisites=("tunnel_predict",),
        hidden=False,
        completion_rule_id="run:tunnel_speedy",
        group="The Big Fall",
    ),
)
