# Physics Mission Control

A Streamlit playground containing twenty-two kid-friendly physics simulations and expert-mode extensions.

Future subject-area simulations follow the contracts, package layout, and acceptance checklist in `EXPANSION_ARCHITECTURE.md`. They remain outside the registry until their `ExpansionDefinition` passes shared validation.

## Mechanics foundations

The mechanics expansion adds Inclined Plane with Friction, Torque and Levers, Center of Mass, Roller-Coaster Energy, and Rotational Motion under `physics_playground/subjects/mechanics/`. Each has pure typed physics, four learning modes, shared-player animation, structured missions, notebook/report integration, and an expansion manifest. Run focused checks with `pytest -q tests/models/test_inclined_plane.py tests/models/test_torque_levers.py tests/models/test_center_of_mass.py tests/models/test_roller_coaster.py tests/models/test_rotational_motion.py tests/test_mechanics_expansion.py`.

Wave Interference is the first waves-and-oscillations expansion. It uses `canvas/scalar_field.py`, a reusable precomputed scalar-field adapter layered on the shared browser player. Focused checks: `pytest -q tests/models/test_wave_interference.py tests/canvas/test_scalar_field.py tests/test_wave_expansion.py`.

Sound and Doppler Effect adds classical moving-source and moving-observer calculations plus the reusable `canvas/wavefronts.py` animation adapter. Focused checks: `pytest -q tests/models/test_doppler_effect.py tests/canvas/test_wavefronts.py tests/test_wave_expansion.py`.

Geometric Optics adds Reflection and Refraction plus Thin Lenses. Both use the reusable responsive `canvas/ray_diagram.py` renderer. Focused checks: `pytest -q tests/models/test_reflection_refraction.py tests/models/test_thin_lenses.py tests/canvas/test_ray_diagram.py tests/test_optics_expansion.py`.

Electric Fields adds bounded point-charge field, potential, and force calculations plus `canvas/vector_field.py`. Dense grids are capped at 2,401 samples (49×49) and singular neighborhoods are excluded explicitly. Focused checks: `pytest -q tests/models/test_electric_fields.py tests/canvas/test_vector_field.py tests/test_electric_field_expansion.py`.

Magnetic Forces covers moving point charges and current-carrying wires using signed cross products and the reusable `canvas/vector_diagram.py` direction renderer. Focused checks: `pytest -q tests/models/test_magnetic_forces.py tests/canvas/test_vector_diagram.py tests/test_magnetic_force_expansion.py`.

Buoyancy and Fluid Pressure begin the Fluids and Matter expansion and share `canvas/fluid_container.py`. Focused checks: `pytest -q tests/models/test_buoyancy.py tests/models/test_fluid_pressure.py tests/canvas/test_fluid_container.py tests/test_fluids_expansion.py`.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Verify the structural checkpoint

```bash
python -m compileall app.py physics_playground tests
pytest -q
```

The original uploaded files remain untouched in `upload/`. The runnable copies live in `physics_playground/pages/`; their current calculations and interfaces are preserved while newer typed contracts are introduced for later migration steps.

## Shared simulation contract

New simulations implement `physics_playground.contracts.Simulation` with a
serializable `ParameterSet` and `ContractResult`. Results may include summary
metrics, events, analytical plot data, animation tracks, model assumptions,
and side-effect-free mission evaluations. `TrialHistory` retains reproducible
runs for later comparison or storage in Streamlit session state.

See `physics_playground/examples/free_fall.py` for a minimal complete example.
It is intentionally not added to the seven-item application registry.

## Reference simulation

Bumper Cars is the first simulation migrated to the shared contract. Its pure
collision model is in `physics_playground/models/collision.py`; mission rules,
canvas generation, analytical charts, and Streamlit rendering live in their
respective package layers. Observational badges are evaluated only when the
user presses the run button.

## Shared browser animation player

`physics_playground/canvas/player.py` owns playback, pause, replay, scrubbing,
playback rate, responsive and high-DPI sizing, reduced-motion behavior,
keyboard controls, trails, fraction-based events, seeded particles, completion
messages, and accessible status announcements. Bumper Cars supplies only its
typed trajectory payload and scene drawing adapter. The other six simulations
continue using the legacy canvas helper until their individual migrations.

## Four-mode learning experience

Reusable components in `physics_playground/presentation/learning_modes.py`
define Explore, Compare, Analyze, and Model. Bumper Cars is the reference page:
Explore preserves its prediction and badge loop; Compare synchronizes Run A
and Run B; Analyze presents charts and conservation checks; Model documents
equations, assumptions, limitations, and optional advanced controls.

## Experiment notebook

The sidebar notebook persists structured trials for the current Streamlit
session. It supports filtering, two-trial comparison, pinning Run A, setup
reuse, deletion, confirmed reset, learner observations, and JSON/CSV exports.
`physics_playground/notebook.py` is UI-independent; migrated simulations call
the reusable helpers in `physics_playground/presentation/notebook_ui.py`.
Bumper Cars records Explore launches and both sides of Compare runs.

## Cannonball Launcher

Cannonball is migrated to the same four-mode architecture and shared player.
Its pure model provides an analytic no-drag solution and an RK4 quadratic-drag
solution with interpolated ground impact and explicit non-landing outcomes.
Explore targets are deterministic and reusable; comparison overlays cover
30°/60°, drag/no-drag, and Earth/Moon. Completed Explore and Compare runs are
stored in the experiment notebook.

## Boing Machine

Boing now uses pure analytic ideal SHM and RK4 damped/driven models, the shared
player, four learning modes, launch-gated badges, and notebook trials. It adds
half/natural/twice-natural drive presets, four comparison experiments, position,
velocity, energy, phase-space, and cached resonance-response charts.

## Swing Machine

Swing Machine now provides analytical small-angle and RK4 nonlinear pendulum
models, model overlays, four learning modes, notebook trials, a shared responsive
player with rope length shown to scale, and angle, angular-velocity, energy,
phase-space, and approximation-error charts.

## Planet Launcher

Planet Launcher now uses velocity-Verlet integration, structured crash/circular/
elliptical/escape outcomes, four learning modes, notebook trials, comparison
overlays, timestep warnings, and full energy, angular-momentum, eccentricity,
periapsis, apoapsis, and numerical-drift diagnostics.

## The Big Fall

The Big Fall now labels uniform density as its default analytical SHM model and
adds an advanced center-heavy radial-density model integrated with RK4. Both use
the shared player, four learning modes, notebook trials, launch-gated badges,
comparison overlays, and position, velocity, acceleration, and energy charts.

## Double Pendulum of Chaos

Double Pendulum now integrates a paired baseline and perturbed system in one
typed model, with adjustable perturbation and timestep, shared animation,
four learning modes, notebook trials, convergence warnings, launch-gated
badges, energy and phase-space charts, separation diagnostics, and an
approximate finite-time divergence rate.

## Registry and home screen

The complete simulation registry is now the single source of truth for stable
IDs, page renderers, modes, concepts, difficulty, badge counts, model versions,
simulation type, and visual metadata. Mission Control renders filterable cards
from that registry, while the same definitions drive persistent sidebar
navigation after a simulation is opened.

## Structured missions

All 25 original achievements are structured mission definitions with stable
IDs, simulation ownership, descriptions, progressive hints, type, difficulty,
prerequisites, visibility, and rule identifiers. Prediction quizzes create
pending explanation missions; the shared service awards them only after an
experiment run. Secret achievements remain hidden until unlocked, and shared
summaries drive per-simulation and overall completion percentages.

## Local profiles

Optional local profiles persist display name, badges, notebook trials, last
simulation and parameters, favorite, experiment count, observations, and app
version in SQLite. No account, email, or demographic data is collected. Set
`PHYSICS_PLAYGROUND_DB` to override the default
`~/.physics_playground/profiles.sqlite3`. If the database cannot be opened, the
app continues in session-only mode. Profile JSON supports local backup and
import as a new profile identity.

## Accessibility and responsive design

The shared settings panel provides persisted reduced-motion, high-contrast,
and larger-text preferences. Browser players are responsive and high-DPI,
include visible focus, keyboard play/pause/replay/scrub controls, accessible
labels and live status, and honor both user settings and operating-system motion
preferences. Pages prevent horizontal overflow, charts use colorblind-safe
colors plus distinct line styles and markers, and every chart and result has a
text description.

## Performance and reliability

All parameter models now share finite-value checks and computational budgets.
Cached deterministic Streamlit entry points serve every simulation; resonance,
projectile-angle, collision-energy, and static HTML generation use bounded
caches. Notebooks retain at most 500 trials, numerical models expose timestep
recommendations or warnings, and a developer diagnostics panel reports recent
compute timings, cache statistics, and active budgets without learner data.

## Lab reports

The experiment notebook can generate multi-trial lab reports through a neutral
report model and independent printable HTML, Markdown, CSV, and JSON renderers.
Reports include the scientist name, registry question and title, predictions,
parameters, models, summaries, measurements, comparisons, a chart, badges,
observations, assumptions, and a conclusion prompt. A future PDF renderer can
implement the same `ReportRenderer` protocol without changing simulations.
