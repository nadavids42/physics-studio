import math
from physics_playground.models.orbit import OrbitOutcome,OrbitParameters,simulate_orbit,simulate_orbit_legacy_euler
def test_circular_orbit_speed():
    p=OrbitParameters(20,7,math.sqrt(20/7),.01,6000);r=simulate_orbit(p);assert r.outcome==OrbitOutcome.CIRCULAR;assert r.eccentricity<.03
def test_escape_classification():
    p=OrbitParameters(20,7,math.sqrt(40/7)*1.01,.01,3000,escape_radius=40);assert simulate_orbit(p).outcome==OrbitOutcome.ESCAPE
def test_bound_orbit_classification():
    p=OrbitParameters(20,7,math.sqrt(20/7)*.75,.01,8000);r=simulate_orbit(p);assert r.outcome==OrbitOutcome.ELLIPTICAL;assert r.eccentricity>0
def test_energy_conservation_tolerance():
    p=OrbitParameters(20,7,math.sqrt(20/7),.02,10000);assert simulate_orbit(p).energy_drift_fraction<1e-6
def test_angular_momentum_conservation_tolerance():
    p=OrbitParameters(20,7,math.sqrt(20/7)*.85,.02,10000);assert simulate_orbit(p).angular_momentum_drift_fraction<1e-10
def test_verlet_improves_energy_conservation_over_previous_integrator():
    p=OrbitParameters(20,7,math.sqrt(20/7)*.85,.08,5000);verlet=simulate_orbit(p);euler=simulate_orbit_legacy_euler(p);assert verlet.energy_drift_fraction<euler.energy_drift_fraction*.2
