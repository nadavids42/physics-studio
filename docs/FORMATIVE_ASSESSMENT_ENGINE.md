# Formative assessment engine

Physics Studio's formative assessment engine is a renderer-independent domain service scoped to
the Introductory Mechanics course. Streamlit collects keyboard-operable native inputs and displays
the returned status, feedback, hints, and evidence; it does not decide correctness.

## Supported grading

- Multiple choice is graded against one private choice ID.
- Multiple select requires the exact private set: missing or extra choices are incorrect.
- Numeric responses require an explicit supported unit. The engine converts compatible Mechanics
  units into the answer's canonical unit before applying the larger of an absolute and relative
  tolerance. It compares unrounded values and never infers tolerance from typed decimal places.
- Short constructed responses are recorded as `self_review`. The system does not claim they are
  correct and does not create automatic objective evidence from them.
- Deterministic variants use a stable hash of definition ID, learner ID, and attempt number. Public
  prompt variants and private answer variants must have matching IDs.

Supported unit dimensions are deliberately small: length, time, speed, acceleration, force,
energy, momentum, and angle. Unknown or dimensionally incompatible units are rejected rather than
guessed.

## Attempts, evidence, and assessment status

The client submits only `AssessmentResponse`; it has no correctness field. `submit_response`
creates the immutable `AssessmentAttempt`, misconception tags, feedback, next hint, objective
evidence, and objective assessment status from the trusted definition and prior attempt history.

Objective status uses each definition's explicit recent-attempt rule and is named `not assessed`,
`developing`, or `demonstrated`. Completing an activity, section, or lesson is not called mastery.
Legacy `mastered_objective_ids` in pathway progress remains readable for saved-profile migration but
new submissions do not write it.

Attempts and objective evidence serialize independently from pathway progress and persist in the
existing local profile payload. Profile schema 2 migrates to schema 3 without altering saved lesson
progress.

## Explicit limits

The engine cannot automatically grade the quality of explanations, diagrams, derivations,
experimental design, model criticism, or reflection. It does not provide adaptive sequencing,
psychometric scoring, randomized item banks, proctoring, grades, attempt limits, classroom
administration, or LMS interoperability. Hints are definition-authored and retries are formative.
