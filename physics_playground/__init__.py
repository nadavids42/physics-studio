"""Legacy Python package for the Physics Studio application."""

from physics_playground.contracts import Simulation
from physics_playground.registry import SIMULATION_REGISTRY

__all__ = ["SIMULATION_REGISTRY", "Simulation"]
