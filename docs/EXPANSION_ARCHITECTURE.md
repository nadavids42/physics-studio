# Adding a simulation to Physics Studio

This guide describes the current vertical-slice path for a registered simulation. It complements
`docs/ARCHITECTURE.md` and the scientific-rendering rules in `docs/VISUAL_SYSTEM.md`.

## 1. Choose ownership and a stable ID

Select an existing `SubjectArea` from `physics_playground/models/expansion.py` and create:

```text
physics_playground/subjects/<subject>/<simulation_id>/
  __init__.py
  physics.py
  missions.py
  page.py
  charts.py       # when charts are simulation-specific
  scene.py        # when the browser scene is simulation-specific
```

Use a lowercase snake-case simulation ID. Treat it as permanent once notebook records, missions,
or profiles can reference it.

## 2. Implement physics first

In `physics.py`, define validated parameter and result dataclasses and a pure simulation entrypoint.
The module must not import Streamlit, Matplotlib, canvas adapters, or presentation helpers.

Document and test:

- the physical system and coordinate convention;
- assumptions and governing laws;
- units for every input and reported result;
- derivation or numerical method;
- at least two analytical results or invariants;
- invalid and boundary inputs;
- determinism, including seeded stochastic behavior;
- limiting cases and model limitations;
- numerical convergence when an approximation or integrator requires it.

Place model tests in `tests/models/test_<simulation_id>.py`.

## 3. Add mission evidence

Define side-effect-free mission evaluation in `missions.py`. Evaluators receive a result and return
`MissionEvaluation` records; they must not mutate Streamlit state. Add the corresponding stable
`MissionDefinition` records to `physics_playground/missions/definitions.py` and test completion,
non-completion, prerequisites, and ownership.

## 4. Build the four-mode page

In `page.py`, compose:

- **Explore:** collect a prediction before revealing the experimental result;
- **Compare:** change one identified variable and show both outcomes clearly;
- **Analyze:** provide a meaningful chart or quantitative investigation;
- **Model:** explain equations, assumptions, limitations, and the connection to observations.

Use helpers in `physics_playground/presentation/learning_modes.py`, record reproducible runs through
`physics_playground/presentation/notebook_ui.py`, and use shared chart/accessibility helpers. Keep
calculation logic in `physics.py`.

## 5. Reuse the visual system

Keep a simulation-specific browser adapter in the slice's `scene.py`. Use an existing shared
adapter under `physics_playground/canvas/` when the rendering pattern serves multiple simulations.
Use assets and semantic colors from `physics_playground/visual/` in either case.

Every scene must remain understandable in Diagram presentation mode, at narrow widths, with reduced
motion, and without color as the only identifier. Vector-like visuals must declare whether their
lengths are physical, normalized for visibility, or schematic. See `docs/VISUAL_SYSTEM.md` for the
complete acceptance checklist.

## 6. Declare the expansion manifest

Add an `ExpansionDefinition` to the relevant subject `manifests.py`. It must declare:

- `SimulationDefinition` metadata;
- subject, parameter model, result model, and importable entrypoints;
- `REQUIRED_MODE_REQUIREMENTS` or an equivalent complete capability declaration;
- centralized mission definitions for the simulation;
- assumptions and limitations;
- honest `TestRequirements` counts and capabilities.

The validator is `validate_expansion_definition()` in
`physics_playground/expansion_validation.py`. The combined catalog is
`physics_playground/expansion_catalog.py`.

## 7. Enroll it in the runtime registry

Add the same stable ID and matching metadata to `SIMULATION_REGISTRY` in
`physics_playground/registry.py`. The registry drives navigation and lazy page loading. Manifests
currently do not generate registry entries, so both catalogs must be updated deliberately.

Add or extend tests that verify:

- the page module and declared entrypoints import successfully;
- manifest and registry IDs and metadata agree;
- all four modes are present;
- widget/session keys do not collide;
- mission, notebook, accessibility, and serialization expectations hold.

Existing integration coverage is located in:

```text
tests/test_expansion_architecture.py
tests/test_cross_simulation_integration.py
tests/test_expansion_widget_keys.py
tests/test_registry.py
```

## 8. Run focused and complete checks

During development, run the new model, mission, canvas, and expansion tests directly. Before
requesting review, run:

```bash
ruff format .
ruff check --fix .
ruff format --check .
ruff check .
mypy
pytest
python -m build
```

There is no separate frontend package today. Browser-rendering contract tests run under pytest; if
you change the shared player or visuals, also run:

```bash
pytest tests/canvas tests/test_visual_system.py tests/test_visual_regression.py
```

Inspect the simulation manually in light and dark themes, Diagram and Illustrated levels, reduced
motion, high contrast, large text, and representative desktop and narrow-screen widths.

## Definition of done

A simulation is complete only when it is registry-enrolled, manifest-valid, scientifically tested,
available in all four modes, notebook-compatible, mission-integrated, accessible without relying
on animation or color, and passing the complete repository check suite.
