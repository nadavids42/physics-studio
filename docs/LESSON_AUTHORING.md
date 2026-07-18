# Authoring Physics Studio lessons

Physics Studio lessons are immutable, presentation-independent curriculum manifests. They describe
what learners should understand and do without importing Streamlit, page modules, chart renderers,
or browser code. A Streamlit lesson reader—or a future delivery platform—may render the same
content models.

## Repository structure

```text
physics_playground/education/
  models.py                 typed curriculum contracts
  validation.py             reference and sequencing validation
  catalog.py                built-in curriculum manifest and lesson lookup
  lessons/
    cannonball.py           complete example lesson
```

Add a lesson in `education/lessons/`, export it from that package, and enroll it through a `Unit`
and `Subject` in the curriculum catalog. Reference simulations by their registry ID, such as
`"cannonball"`; never import a simulation page. Validation rejects unknown IDs.

## Required lesson anatomy

Every lesson needs:

- measurable learning objectives with expected evidence;
- explicit prerequisites and concept references;
- one or more simulation references;
- ordered sections with substantive narrative;
- an activity sequence whose order follows prediction, exploration, comparison, analysis,
  modeling, and reflection as applicable;
- an estimated duration and a content profile.

Educational quality remains a content responsibility. A complete physics lesson should clearly
state the physical system, assumptions, coordinate choices, governing laws, derivation, units,
result validation, limiting cases, and model limitations. The validator verifies structure and
references; it cannot certify that a scientific claim is correct. Formula and limiting-case tests
must remain in the relevant physics slice.

## Activities and simulation modes

`SimulationActivity` connects learning intent to an existing simulation through a registry ID and
optional renderer-independent parameter preset. The canonical correspondence is:

| Activity phase | Simulation mode |
| --- | --- |
| Prediction | Explore |
| Exploration | Explore |
| Comparison | Compare |
| Analysis | Analyze |
| Modeling | Model |
| Reflection | No mode required |

Each activity appears once in a lesson section and once in `activity_sequence`, in the same order.
Instructions describe learner actions, while `observation_prompt` and `completion_evidence` make
the intended evidence explicit.

## Worked examples

A `WorkedExample` separates:

1. known values, each represented by a quantity, numerical value, and unit;
2. the unknown quantity;
3. symbolic reasoning steps;
4. numerical substitutions;
5. a dimensional or unit check;
6. the final answer and physical interpretation.

Keep symbolic reasoning ahead of substitution. Include enough significant figures to support the
physics without implying false experimental precision.

## Guided derivations and checkpoints

Guided derivations contain ordered `DerivationStep` objects. `reveal_order` starts at one and is
consecutive, allowing a renderer to reveal one prompt, hint, expression, and explanation at a time.

Checkpoint questions reference lesson-objective IDs. Multiple-choice questions need unique choice
IDs and a valid correct choice. Numeric questions need an answer, unit where appropriate, and a
nonnegative tolerance. Explanations should address the reasoning, not simply identify an answer.

## Depth and voice

`ContentProfile` represents pedagogical depth and writing voice independently. A renderer can offer
a foundational, standard, or advanced treatment in an approachable, academic, or concise voice
without changing simulation results or physics contracts. Section-level profiles can override the
lesson default. Do not encode different physical truths as differences in voice.

## Validation and tests

Validate a curriculum against the live registry:

```python
from physics_playground.education.catalog import CURRICULUM
from physics_playground.education.validation import validate_curriculum_manifest
from physics_playground.registry import SIMULATION_REGISTRY

validate_curriculum_manifest(
    CURRICULUM,
    simulation_ids={simulation.id for simulation in SIMULATION_REGISTRY},
)
```

Run the focused and complete checks:

```bash
pytest tests/test_education_content.py
pytest
```

Tests for a new lesson should cover reference validation, objective and checkpoint links, activity
ordering and mode correspondence, progressive derivation reveals, worked-example units, and the
underlying formulas. Adaptive sequencing, teacher dashboards, grading policy, and learner-model
inference are intentionally outside this content model.
