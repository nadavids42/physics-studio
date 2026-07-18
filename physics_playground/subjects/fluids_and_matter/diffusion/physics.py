"""Pure seeded one- and two-dimensional random walks with bounded output."""

import math
from dataclasses import dataclass
from enum import IntEnum

import numpy as np

from physics_playground.validation import PhysicsValidationError

MAX_PARTICLES = 5000
MAX_STEPS = 2000
MAX_UPDATES = 1_000_000
MAX_VISUAL_PARTICLES = 300
MAX_TRAJECTORIES = 12


class WalkDimension(IntEnum):
    ONE_D = 1
    TWO_D = 2


@dataclass(frozen=True, slots=True)
class DiffusionParameters:
    particle_count: int = 500
    dimensions: WalkDimension = WalkDimension.TWO_D
    steps: int = 300
    step_size_m: float = 0.1
    timestep_s: float = 0.05
    bias_x: float = 0.0
    bias_y: float = 0.0
    seed: int = 20263401

    def validate(self) -> None:
        if (
            isinstance(self.particle_count, bool)
            or not isinstance(self.particle_count, int)
            or not 1 <= self.particle_count <= MAX_PARTICLES
        ):
            raise PhysicsValidationError(
                f"Particle count must be an integer from 1 to {MAX_PARTICLES}."
            )
        if (
            isinstance(self.steps, bool)
            or not isinstance(self.steps, int)
            or not 1 <= self.steps <= MAX_STEPS
        ):
            raise PhysicsValidationError(f"Step count must be an integer from 1 to {MAX_STEPS}.")
        if self.particle_count * self.steps > MAX_UPDATES:
            raise PhysicsValidationError(
                f"This setup requests too much work. Keep particles × steps at or below {MAX_UPDATES:,}."
            )
        try:
            dimension = WalkDimension(self.dimensions)
        except (ValueError, TypeError) as exc:
            raise PhysicsValidationError("Choose a one- or two-dimensional walk.") from exc
        values = (self.step_size_m, self.timestep_s, self.bias_x, self.bias_y)
        if not all(math.isfinite(v) for v in values):
            raise PhysicsValidationError("Walk parameters must be finite.")
        if self.step_size_m <= 0 or self.timestep_s <= 0:
            raise PhysicsValidationError("Step size and timestep must be greater than zero.")
        if not -1 <= self.bias_x <= 1 or not -1 <= self.bias_y <= 1:
            raise PhysicsValidationError("Bias components must be between −1 and 1.")
        if dimension is WalkDimension.ONE_D and self.bias_y != 0:
            raise PhysicsValidationError("A one-dimensional walk cannot have vertical bias.")
        if dimension is WalkDimension.TWO_D and math.hypot(self.bias_x, self.bias_y) > 1:
            raise PhysicsValidationError(
                "The two-dimensional bias vector cannot have magnitude greater than 1."
            )
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise PhysicsValidationError("Random seed must be an integer.")

    def to_dict(self):
        return {
            **{k: getattr(self, k) for k in self.__dataclass_fields__},
            "dimensions": int(self.dimensions),
        }


@dataclass(frozen=True, slots=True)
class DiffusionResult:
    parameters: DiffusionParameters
    elapsed_time_s: float
    mean_displacement_x_m: float
    mean_displacement_y_m: float
    mean_squared_displacement_m2: float
    expected_mean_x_m: float
    diffusion_coefficient_m2_s: float
    final_x_m: tuple[float, ...]
    final_y_m: tuple[float, ...]
    sample_trajectories: tuple[tuple[tuple[float, float], ...], ...]
    sampled_particle_count: int
    outcome: str


def simulate(p: DiffusionParameters) -> DiffusionResult:
    p.validate()
    dimension = WalkDimension(p.dimensions)
    rng = np.random.default_rng(p.seed)
    n = p.particle_count
    s = p.steps
    length = p.step_size_m
    if dimension is WalkDimension.ONE_D:
        probability = (1 + p.bias_x) / 2
        dx = np.where(rng.random((s, n)) < probability, length, -length)
        dy = np.zeros_like(dx)
    else:
        # Isotropic random directions plus a bounded drift component. Scaling the
        # random part preserves a clear zero-noise limit as |bias| approaches 1.
        magnitude = math.hypot(p.bias_x, p.bias_y)
        angles = rng.uniform(0, 2 * math.pi, (s, n))
        noise = math.sqrt(max(0, 1 - magnitude * magnitude))
        dx = length * (noise * np.cos(angles) + p.bias_x)
        dy = length * (noise * np.sin(angles) + p.bias_y)
    x = dx.sum(axis=0)
    y = dy.sum(axis=0)
    mean_x = float(x.mean())
    mean_y = float(y.mean())
    msd = float(np.mean(x * x + y * y))
    elapsed = s * p.timestep_s
    visual = min(n, MAX_VISUAL_PARTICLES)
    trajectory_count = min(n, MAX_TRAJECTORIES)
    indices = np.linspace(0, n - 1, trajectory_count, dtype=int)
    stride = max(1, s // 200)
    trajectories = []
    for index in indices:
        px = np.concatenate(([0.0], np.cumsum(dx[:, index])))[::stride]
        py = np.concatenate(([0.0], np.cumsum(dy[:, index])))[::stride]
        trajectories.append(tuple((float(a), float(b)) for a, b in zip(px, py, strict=True)))
    coefficient = length * length / (2 * int(dimension) * p.timestep_s)
    expected_x = s * length * p.bias_x
    return DiffusionResult(
        p,
        elapsed,
        mean_x,
        mean_y,
        msd,
        expected_x,
        coefficient,
        tuple(float(v) for v in x[:visual]),
        tuple(float(v) for v in y[:visual]),
        tuple(trajectories),
        visual,
        f"After {s} steps, the particles have mean displacement ({mean_x:.3f}, {mean_y:.3f}) m and mean-squared displacement {msd:.3f} m².",
    )
