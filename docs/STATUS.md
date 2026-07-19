# Status

Verifiable facts about the current state of this repository. Run the commands yourself to check
any line here.

## What exists

- 22 simulations (`python3 -c "from physics_playground.registry import SIMULATION_REGISTRY as r; print(len(r))"`),
  each with Explore, Compare, Analyze, and Model modes.
- 6 curriculum lessons (`python3 -c "from physics_playground.education.catalog import LESSONS_BY_ID as l; print(len(l))"`):
  measurement/models, position/velocity, motion graphs, constant acceleration, vectors and
  components, and projectile motion from components. All Mechanics; no other subject has an
  authored lesson.
- One browser-side payload view: the Cannonball linked-projectile representation
  (`physics_playground/subjects/mechanics/cannonball/linked_payload.py`), with exactly one
  consumer, enforced by `tests/test_cannonball_linked_payload.py`.
- Local SQLite persistence (`physics_playground/learning_store.py`) for one learner's profile,
  progress, attempts, trials, and notebook at a time.

## Test suite

- `pytest -ra` without `CHROMIUM_BIN` set: 546 passed, 3 skipped (the browser-only tests, with an
  explicit loud skip reason and a terminal warning; see `tests/conftest.py`).
- `pytest -ra` with `CHROMIUM_BIN` set to a real Chromium binary: 549 passed, 0 skipped.
- `mypy`: checks 16 of 225 `.py` files under `physics_playground/` (an explicit ratchet list in
  `pyproject.toml`, not the whole package).
- Frontend: `npm test` runs 21 Vitest tests across 5 files; `npm run lint` and `npm run
  build:check` also pass.
- `ruff format --check .` and `ruff check .` pass on the whole tree.

## Known limitations

- Persistence is single-learner, local SQLite. No accounts, no multi-tenant service, no hosted
  backend.
- The frontend build (`frontend/scripts/build.mjs`) produces one self-contained IIFE bundle per
  entry point (`bundle: true`, no `splitting`); shared code is duplicated across bundles rather
  than extracted into a shared chunk.
- The application shell (sidebar, page chrome, theming) is Streamlit's default styling with CSS
  overrides layered on top, not a custom-designed interface.
- Lesson and assessment content is authored as Python literals in source files
  (`physics_playground/subjects/**/lesson.py`, `kinematics_lessons.py`, etc.). There is no
  authoring UI or content database.
