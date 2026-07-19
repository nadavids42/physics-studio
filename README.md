# Physics Studio

Physics Studio is an interactive physics textbook built around the idea that every figure can
be alive. It currently contains 22 browser-rendered simulations with four learning modes:
Explore, Compare, Analyze, and Model.

The default audience is high-school through introductory undergraduate learners. The interface
is accessible enough for motivated younger learners and may be playful, but it is not intended
to be childish by default.

## What exists today

- Pure, typed physics models with deterministic tests and explicit validation.
- Mechanics, waves, optics, electromagnetism, fluids, matter, oscillation, and orbital examples.
- A shared scientific visual system with responsive canvas rendering.
- Prediction prompts, missions, local profiles, experiment notebooks, and lab-report exports.
- Reduced-motion, high-contrast, large-text, keyboard, and nonvisual-description support.
- A typed curriculum model and six connected, evidence-gated Mechanics lessons from models and
  measurement through projectile motion.
- All 22 simulations use the same plain vertical-slice page pattern.
- A framework-free JavaScript workspace with executable player and scene tests.

Physics Studio is not yet a complete Mechanics course or course platform. The implemented lesson
sequence stops after projectile motion; the remaining roadmap is specification only. The app does
not currently provide accounts, teacher dashboards, adaptive assessment, or classroom management.

## Run the application

Python 3.11 is the development and CI baseline. Python 3.11 through 3.13 is tested in CI.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
streamlit run app.py
```

For a runtime-only deployment, install `requirements.txt` instead:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Run the checks

```bash
ruff format --check .
ruff check .
mypy
pytest
python -m build
```

Browser rendering is authored as ES modules and assembled into packaged static assets. Install and
verify the framework-free frontend workspace with:

```bash
cd frontend
npm ci
npm run check
```

Built assets are committed under `physics_playground/static/js/`, so runtime deployments do not
need Node.js. Real-browser accessibility and perceptual checks require Chromium:

```bash
CHROMIUM_BIN=/path/to/chromium pytest -q \
  tests/test_browser_accessibility.py tests/test_visual_screenshots.py
```

## Architecture in brief

Physics calculations are independent of Streamlit. Pure models accept validated parameter
objects and return immutable result objects; they do not import UI, chart, or canvas code.
Streamlit is the current delivery platform and presentation shell, not part of the physics
domain. A future delivery layer can reuse the model outputs without rewriting the equations.

All simulations use subject-oriented vertical slices under
`physics_playground/subjects/<subject>/<simulation>/`. Each slice normally contains physics,
missions, registry metadata, page composition, and package exports. Central catalogs discover and
validate slice metadata. Expansion manifests describe integration requirements, while the runtime
registry drives navigation and lazy page loading.

The product is Physics Studio. The historical `physics_playground` Python import package remains
as deliberate compatibility debt; see the architecture guide for its eventual decision boundary.

Read [the architecture guide](docs/ARCHITECTURE.md) and
[the expansion guide](docs/EXPANSION_ARCHITECTURE.md) before adding a simulation.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow and review expectations.
The visual vocabulary and scientific-rendering rules are documented in
[docs/VISUAL_SYSTEM.md](docs/VISUAL_SYSTEM.md). The historical migration audit is preserved in
[docs/ARCHITECTURE_MIGRATION.md](docs/ARCHITECTURE_MIGRATION.md). Verifiable current facts about
test coverage and known limitations are in [docs/STATUS.md](docs/STATUS.md).

## License

Physics Studio is licensed under the [Apache License 2.0](LICENSE).

Project history is maintained in [CHANGELOG.md](CHANGELOG.md).
