# Development guide

Physics Studio supports Python 3.11 and newer. Python 3.11 is the development and CI
baseline recorded in `.python-version`; compatibility with newer supported Python releases
should be preserved. Raising the minimum version requires an explicit project decision and a
release note.

## Set up a development environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

`requirements.txt` contains runtime dependencies for Streamlit deployments. The `dev` extra
adds tests, formatting, linting, type checking, pre-commit, and package-build tools.

## Run the checks

```bash
ruff format --check .
ruff check .
mypy
pytest
python -m build
```

Apply safe automatic formatting and import fixes with:

```bash
ruff format .
ruff check --fix .
```

Ruff formats Python syntax but does not reformat JavaScript stored inside Python string
literals. Changes to embedded JavaScript still require focused player and visual-system tests.

To run the optional local commit hooks:

```bash
pre-commit install
pre-commit run --all-files
```

## Type-checking ratchet

The current code predates repository-wide type enforcement. MyPy therefore checks an explicit
set of typed, UI-independent foundation modules listed in `pyproject.toml`; those modules use
`disallow_untyped_defs` and related strictness options. This is a coverage boundary, not a broad
error suppression.

When a module's public functions and data boundaries have complete annotations:

1. run `mypy path/to/module.py` and fix every reported issue;
2. add the module to `tool.mypy.files` in `pyproject.toml`;
3. keep it in the ratchet permanently.

Prioritize pure physics, serialization, persistence, mission evaluation, and rendering-payload
builders. Do not add global `ignore_errors`, blanket `# type: ignore`, or broad package exclusions
to make the check green.

## Constants and session-state conventions

- Put reusable physical assumptions in `physics_playground/units.py`, include units in names, and
  test that replacing a literal leaves established defaults unchanged.
- Do not turn intentionally configurable quantities into constants.
- Use `SHARED_STATE_KEYS` for established application features.
- Use `simulation_key("simulation_id", "control_name")` for new simulation-local Streamlit state
  and `feature_key(...)` for new cross-cutting controls.
- Do not add raw globally scoped shared keys or a simulation-specific state manager.
