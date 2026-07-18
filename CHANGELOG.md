# Changelog

Notable project changes are recorded here. This project follows the structure of
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), although historical development was
not consistently tagged as releases.

## Unreleased

### Added

- Contributor-facing packaging, Ruff, MyPy, pytest, pre-commit, and GitHub Actions configuration.
- Architecture, expansion, development, contribution, and migration documentation.
- Apache-2.0 licensing.

### Changed

- Reformatted Python source and established lint and type-checking ratchets without changing
  simulation behavior.
- Replaced the historical implementation log in the README with a concise project overview.
- Assigned canonical responsibility-based names to shared binding, accessibility, visual,
  mission-UI, and canvas-embedding modules while retaining thin import compatibility shims.

## 1.0.0 - 2026-07-18

This entry summarizes the current baseline. Earlier work landed incrementally and was not
maintained as a versioned changelog.

### Added

- A 22-simulation registry spanning mechanics, oscillations, gravity, waves, optics,
  electromagnetism, fluids, gases, and diffusion.
- Explore, Compare, Analyze, and Model modes across registered simulations.
- Typed parameter/result models, numerical validation, computation budgets, deterministic seeds,
  and model-focused tests.
- Shared requestAnimationFrame browser player with responsive high-DPI canvas rendering, playback
  controls, stepping, scrubbing, reduced-motion handling, and teardown.
- Shared scientific design tokens, semantic vectors, reusable assets, three presentation levels,
  chart styling, and structural visual regression coverage.
- Structured missions and badges, experiment notebook capture and reuse, local SQLite profiles,
  profile import/export, and HTML/Markdown/CSV/JSON lab reports.
- Accessibility preferences for reduced motion, high contrast, and larger text, plus keyboard and
  nonvisual chart/result support.
- Subject-oriented vertical slices and validated expansion manifests for 15 simulations.

### Architecture notes

- Seven earlier simulations remain in the horizontal `models/`, `pages/`, `canvas/`, `missions/`,
  and `presentation/` layout. Their migration is planned and they remain supported.
- Streamlit remains the current delivery platform. Physics models are deliberately independent of
  it so presentation can evolve separately.
