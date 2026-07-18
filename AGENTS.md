# Physics Playground Agent Guidance

## Product direction

Physics Playground is evolving from an interactive simulation collection into an educational physics platform.

The simulation engine is valuable existing infrastructure and should be preserved. New work should connect physical intuition, diagrams, derivations, worked examples, guided practice, analytic solutions, and numerical simulations.

## Educational quality bar

Every lesson must explain:

- the physical system
- assumptions
- coordinate choices
- relevant laws
- derivation
- units
- result validation
- limiting cases
- model limitations

Diagrams are first-class components and must be responsive and accessible.

Avoid shallow prose, unexplained formulas, and one-off lesson implementations.

## Engineering rules

- Inspect relevant code before editing.
- Preserve backward compatibility unless a migration is approved.
- Use shared typed models and renderers.
- Keep educational content separate from calculation logic.
- Add tests for formulas, content validation, presets, and navigation.
- Run the full test suite before finishing.
- Return a summary of modified files, decisions, and test results.
