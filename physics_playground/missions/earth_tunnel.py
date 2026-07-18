from physics_playground.contracts import MissionEvaluation
from physics_playground.models.earth_tunnel import TunnelResult


def evaluate_tunnel_missions(r: TunnelResult):
    return (
        MissionEvaluation(
            "tunnel_halfway", r.parameters.start_fraction < 1, "Start halfway down the tunnel."
        ),
        MissionEvaluation(
            "tunnel_speedy",
            r.parameters.radius_m not in (6371000, 1737000, 3390000) and r.opposite_time_s < 1200,
            "Design a custom fall under 20 minutes.",
        ),
    )
