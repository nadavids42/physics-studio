# Physics Studio architecture

## Architectural intent

Physics Studio separates scientific authority from delivery. Physics models own numerical and
analytical meaning. Presentation code turns immutable results into learning modes, charts, and
browser scenes. Streamlit is the current presentation shell; it is replaceable and is not part of
the physics domain.

The repository currently contains two simulation layouts. Seven established simulations use a
horizontal technical-layer layout, while 15 newer simulations use subject-oriented vertical
slices. Both are active and tested. New work should use vertical slices; existing horizontal
simulations should move only through compatibility-preserving migrations.

## Runtime map

```text
app.py
  -> physics_playground/registry.py
       -> lazy import of SimulationDefinition.page_module
            -> Streamlit page and four learning modes
                 -> pure physics model
                 -> mission evaluator
                 -> notebook/profile adapters
                 -> chart helpers
                 -> canvas document builder
                      -> shared browser player and visual assets
```

Cross-cutting state is provided by:

- `physics_playground/missions/` for definitions, pure evaluation, and Streamlit integration;
- `physics_playground/notebook.py` for UI-independent trial records;
- `physics_playground/profiles.py` for local SQLite/JSON profile persistence;
- `physics_playground/accessibility.py` for UI-independent accessibility preferences;
- `physics_playground/presentation/` for Streamlit-facing adapters and charts.

## Pure physics-model boundary

Pure models live in either `physics_playground/models/` or a vertical slice's `physics.py`.
They may depend on contracts, validation, numerical helpers, NumPy, and Python's standard library.
They must not import Streamlit, Matplotlib, presentation modules, or canvas modules.

A model should:

1. accept a typed parameter object;
2. validate ranges, finiteness, and computational budgets;
3. compute deterministic results for identical inputs and seeds;
4. return typed results with explicit units and model metadata;
5. expose assumptions, limitations, warnings, and numerical diagnostics where relevant.

This boundary lets tests call physics without initializing a web application. It also means a
future frontend or service can consume the same results without reimplementing equations.

## Presentation and browser boundary

Pages coordinate the four learning modes and translate model results into text, charts, notebook
records, mission evidence, and rendering payloads. Python canvas adapters serialize precomputed
samples into HTML documents. JavaScript interpolates and draws those samples; it does not own the
physics integration or alter recorded results.

The shared player is in `physics_playground/canvas/player.py`. Shared scientific assets and tokens
are under `physics_playground/visual/`. JavaScript is currently embedded in Python string literals,
so there is no standalone frontend build or npm check. Existing pytest coverage validates payload
structure, deterministic geometry, scaling semantics, and lifecycle markers. Manual browser
inspection is still required for appearance and interaction quality.

## Vertical slices

New simulations live at:

```text
physics_playground/subjects/<subject>/<simulation>/
  __init__.py
  physics.py
  missions.py
  page.py
```

A subject may share canvas or UI helpers at its package root. A slice should own simulation-specific
physics, mission evidence, and page composition. Reusable rendering, state, chart, or validation
logic belongs in shared modules rather than being copied into slices.

The supported subject identifiers are defined by `SubjectArea` in
`physics_playground/models/expansion.py`.

## Manifests, validation, and registry

Subject `manifests.py` modules create `ExpansionDefinition` records. The combined catalog in
`physics_playground/expansion_catalog.py` covers the 15 vertical-slice simulations. Validation in
`physics_playground/expansion_validation.py` requires:

- complete metadata and stable IDs;
- all four learning modes and their required capabilities;
- typed parameter, result, physics, and page entrypoints;
- at least three missions with matching simulation ownership;
- assumptions and limitations;
- declared physics-invariant and validation-test coverage;
- a prediction capability in Explore mode.

`physics_playground/registry.py` is the runtime source for navigation, cards, stable page IDs, lazy
page imports, and visual metadata. Today the registry and expansion catalog are parallel explicit
catalogs: validation tests ensure consistency, but manifests do not generate registry entries.
Contributors adding a simulation must update both and run the integration tests. Do not describe a
simulation as enrolled until it is present in the runtime registry and all validation tests pass.

## Compatibility and state

Stable simulation IDs, mission IDs, model versions, notebook fields, profile schemas, and existing
import paths are compatibility surfaces. Streamlit session-state keys are also observable during a
session. Change them only with migration reads or forwarding imports where appropriate.

The current architecture migration plan is documented in
`docs/ARCHITECTURE_MIGRATION.md`. It favors one runnable, testable stage at a time and does not
authorize changing physics during file moves.

## Tests and quality gates

The complete local gate is:

```bash
ruff format --check .
ruff check .
mypy
pytest
python -m build
```

MyPy currently checks a documented ratchet of typed foundation modules. See
`docs/DEVELOPMENT.md` for how to expand that boundary.
