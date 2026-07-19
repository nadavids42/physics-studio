# Educational-content model sufficiency review

This review tests the typed education model against the 24-lesson Introductory Mechanics roadmap.
It describes implemented contracts, not adaptive-learning plans or lesson UI.

## Capability evaluation

| Capability | Current representation after review | Change required? | Mechanics evidence |
| --- | --- | --- | --- |
| Explanatory narrative | Ordered `LessonSection.narrative` blocks with content profiles | No | Every planned lesson needs system, law, validation, and limitation sections |
| Progressive concept introduction | Subject concepts, ordered units/lessons, lesson concept references, and prerequisites | No | Vector → 1-D → 2-D motion and force → energy sequences |
| Diagrams | Versioned `DiagramSpec` with stable asset ID, caption, alt text, and objective references | Yes | Vector components, motion graphs, free-body diagrams, torque arms |
| Guided derivations | `GuidedDerivation` with ordered reveal steps, assumptions, hints, and conclusion | No | Kinematics, projectile range, work-energy, orbit relations |
| Worked examples | Typed knowns, unknown, symbolic reasoning, substitutions, unit check, answer, interpretation | No | Required in all 24 roadmap lessons |
| Formative assessment | Learner-visible `CheckpointQuestion` plus private `AssessmentDefinition` | Yes: separation only | Every lesson has conceptual and quantitative checks |
| Quantitative tolerance and units | Private numeric answer definition contains tolerance and unit | Retained, moved | Kinematics, energy, momentum, rotation, and gravitation problems |
| Hints | Derivation-step hints and private assessment hints | Yes for assessments | Projectile roots, friction thresholds, collisions, and orbits |
| Multiple attempts | Serialized `AssessmentAttempt` records; progress stores attempt IDs only | Yes | Repeated prediction/diagnostic checks throughout the course |
| Misconception diagnosis | `MisconceptionCallout` plus diagnostic checkpoints | No | Free-fall, friction, collisions, torque, and orbit lessons |
| Simulation presets | Typed `SimulationActivity.parameter_preset` and learning mode | No | Eight selectively assigned simulation activities |
| Evidence collection | Activity evidence text, objective-linked activities/diagrams/checkpoints, and notebook trials | Yes: objective links | Projectile, incline, coaster, collision, and rotation investigations |
| Remediation | Private assessment definitions reference existing lesson IDs and provide hints | Yes | Projectile root/component review; friction/FBD review; collision/impulse review |
| Lesson completion | `PathwayProgress` derives completion from required activity/checkpoint IDs | No | Existing Cannonball pathway |
| Prerequisite mastery | Required lesson prerequisites are checked against separate completed progress | Yes | Every unit after Foundations and all cumulative lessons |
| Cumulative review | Ordinary lessons with multiple prerequisite edges and objective-linked evidence | No special field | Lessons 6, 9, 15, 18, 21, and 24 |

## Separation and serialization boundaries

Learner-visible content contains prompts and answer choices but no scoring answers. Correct answers,
numeric tolerances, success feedback, hints, and remediation references live in private
`AssessmentDefinition` objects. Learner responses live in `AssessmentAttempt`; completion lives in
`PathwayProgress`; assessment status and objective evidence are derived separately from trusted
answer rules and attempt history. These records do not import Streamlit or a renderer.

Curriculum, lessons, diagrams, checkpoints, assessment definitions, attempts, and progress now
carry explicit schema versions at their serialization boundaries. Checkpoint serialization is safe
for a learner-facing client because it cannot emit a correct answer or private feedback.

Saved pathway progress without a version is treated as schema 1 and migrates through schema 3 with
empty evidence references and resumable-section state. The legacy mastered-objective field remains
readable but is no longer written. Unknown future schemas fail explicitly.

## Validation invariants

Validation now enforces:

- unique curriculum, subject, unit, lesson, objective, section, component, activity, checkpoint,
  answer-choice, and assessment IDs;
- supported content and assessment schema versions;
- known concept, simulation, lesson prerequisite, remediation, activity-objective, diagram-objective,
  checkpoint-objective, and assessment-objective references;
- an acyclic lesson prerequisite graph;
- exact unit coverage of lesson objectives and complete lesson-objective coverage by evidence-bearing
  components;
- matching learner-visible checkpoints and private assessment definitions;
- answer-choice membership for multiple choice and tolerance plus units for numeric answers;
- existing activity mode ordering, worked-example units, derivation ordering, and lesson completion
  requirements.

## Explicit non-goals

No adaptive sequencing, mastery probability, large question banks, attempt limits, hint unlocking,
automatic remediation selection, grading service, or renderer behavior was added. Those are not
required to represent the current Mechanics roadmap and would be speculative.
