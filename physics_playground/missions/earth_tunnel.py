from physics_playground.contracts import MissionEvaluation
from physics_playground.models.earth_tunnel import TunnelResult
from physics_playground.units import EARTH_RADIUS_M, MARS_RADIUS_M, MOON_RADIUS_M


def evaluate_tunnel_missions(r: TunnelResult):
    return (
        MissionEvaluation(
            "tunnel_halfway", r.parameters.start_fraction < 1, "Start halfway down the tunnel."
        ),
        MissionEvaluation(
            "tunnel_speedy",
            r.parameters.radius_m not in (EARTH_RADIUS_M, MOON_RADIUS_M, MARS_RADIUS_M)
            and r.opposite_time_s < 1200,
            "Design a custom fall under 20 minutes.",
        ),
    )
