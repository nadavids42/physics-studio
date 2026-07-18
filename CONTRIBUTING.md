# Contributing to Physics Studio

Thank you for helping make physics more explorable. Contributions should preserve scientific
correctness, educational clarity, accessibility, and the clean boundary between physics and UI.

The primary audience is high-school through introductory undergraduate learners. Material may
also support motivated younger learners, but default language and visuals should remain playful
without becoming childish.

## Before you begin

For a substantial change, open an issue or discussion before investing in implementation. This
is especially important for new simulations, public API changes, new dependencies, persistence
schema changes, or modifications to physical models.

Read these guides as relevant:

- [Architecture](docs/ARCHITECTURE.md)
- [Adding a simulation](docs/EXPANSION_ARCHITECTURE.md)
- [Visual system](docs/VISUAL_SYSTEM.md)
- [Development setup and type ratchet](docs/DEVELOPMENT.md)

## Development setup

Python 3.11 is the baseline version recorded in `.python-version`. CI also runs the complete test
suite on Python 3.12 and 3.13.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Start the application with:

```bash
streamlit run app.py
```

## Make a focused change

- Keep physics calculations in pure modules with no Streamlit, Matplotlib, or canvas imports.
- Use frozen, slotted dataclasses and existing typed contracts where practical.
- Keep educational content separate from calculation logic.
- Preserve Explore, Compare, Analyze, and Model behavior.
- Reuse shared assets, design tokens, chart helpers, and animation infrastructure.
- State assumptions, coordinate choices, units, limitations, and limiting cases.
- Add deterministic tests for formulas, validation boundaries, missions, serialization, and
  presentation payloads affected by the change.
- Do not update structural hashes or string assertions without verifying the behavior they are
  intended to protect.

## Run checks locally

Apply formatting and safe lint fixes:

```bash
ruff format .
ruff check --fix .
```

Run the same quality gates used by CI:

```bash
ruff format --check .
ruff check .
mypy
pytest
python -m build
```

The MyPy configuration is a ratchet over explicitly listed modules, not a claim that the whole
repository is fully typed. Add a newly typed module to `tool.mypy.files`; do not introduce global
`ignore_errors` or blanket exclusions.

The browser player currently has no separate npm toolchain. Run the focused browser-rendering
contract checks with:

```bash
pytest tests/canvas tests/test_visual_system.py tests/test_visual_regression.py
```

These tests verify payloads, geometry, lifecycle markers, and deterministic visual inputs. They
do not replace manual browser inspection for layout, interaction, contrast, or label overlap.

Optional local hooks are available:

```bash
pre-commit install
pre-commit run --all-files
```

## Pull-request checklist

- Explain the learner-facing outcome and implementation boundary.
- List changed physics assumptions or state explicitly that physics is unchanged.
- Include tests and report their real results.
- Confirm keyboard, reduced-motion, high-contrast, and narrow-screen behavior when presentation
  code changes.
- Update architecture or contributor documentation when public paths or commands change.
- Add a changelog entry under `Unreleased` for a learner-visible or contributor-visible change.

By contributing, you agree that your contribution is licensed under Apache-2.0.
