"""Cumulative assessment covering the full Mechanics lesson sequence.

Draws fresh numeric and multiple-choice items on content from six earlier lessons
(position/velocity, motion graphs, constant acceleration, vectors and components,
2D motion, and projectile motion) and grades them with the existing assessment
engine and the standard mastery rule. No new grading mechanism is introduced.
"""

from physics_playground.education.assessments import AssessmentDefinition
from physics_playground.education.models import (
    ActivityPhase,
    AnswerChoice,
    CheckpointQuestion,
    LearningObjective,
    Lesson,
    LessonSection,
    Prerequisite,
    PrerequisiteKind,
    QuestionKind,
    SimulationActivity,
)

# A literal lesson ID, not an import, to avoid a cycle: cannonball/lesson.py imports this
# module's lesson to assemble the curriculum's final unit.
PROJECTILE_LESSON_ID = "projectile-motion-from-components"

OBJECTIVES = (
    LearningObjective(
        "cum-velocity",
        "Compute average velocity from signed endpoint positions and elapsed time.",
        "A correct average-velocity calculation with sign and units.",
    ),
    LearningObjective(
        "cum-acceleration",
        "Compute average acceleration from a signed velocity change.",
        "A correct average-acceleration calculation with sign and units.",
    ),
    LearningObjective(
        "cum-stopping-distance",
        "Apply the time-independent constant-acceleration relation to find a displacement.",
        "A correct stopping-distance calculation using v_f^2=v_i^2+2a delta x.",
    ),
    LearningObjective(
        "cum-components",
        "Resolve a launch velocity into a vertical component using sine.",
        "A correct v_y calculation with units for a stated speed and angle.",
    ),
    LearningObjective(
        "cum-two-d-position",
        "Combine an initial vertical velocity and constant vertical acceleration to find position at a given time.",
        "A correct vertical-position calculation independent of the horizontal component.",
    ),
    LearningObjective(
        "cum-model-limits",
        "Identify which change breaks the assumptions of the ideal projectile range relation.",
        "A correct identification of a physically invalidating change versus a cosmetic one.",
    ),
    LearningObjective(
        "cum-independence",
        "Apply independence of horizontal and vertical motion to compare two projectile scenarios.",
        "A correct comparison that isolates the vertical motion from the horizontal motion.",
    ),
)

ACTIVITIES = (
    SimulationActivity(
        "cum-review-launch",
        ActivityPhase.REFLECTION,
        "cannonball",
        "One last look before the cumulative check",
        (
            "Run one projectile launch of your choice.",
            "Name one quantity from this course that the trajectory demonstrates.",
        ),
        None,
        "Which concept from the course does this run illustrate best?",
        "A one-sentence connection between the run and a course concept.",
        objective_ids=("cum-model-limits",),
    ),
)

CUMULATIVE_ASSESSMENT_LESSON = Lesson(
    "cumulative-mechanics-check",
    "Cumulative check: models through projectile motion",
    "A single cumulative check drawing on position and velocity, motion graphs, constant acceleration, vectors and components, 2D motion, and projectile motion.",
    OBJECTIVES,
    (
        Prerequisite(
            "requires-projectile-motion-from-components",
            PrerequisiteKind.LESSON,
            PROJECTILE_LESSON_ID,
            "This check draws on every lesson in the sequence, so it follows the last of them.",
        ),
    ),
    (
        "motion_coordinates",
        "motion_graphs",
        "kinematics",
        "vectors",
        "component_independence",
        "projectile_motion",
    ),
    ("cannonball",),
    (
        LessonSection(
            "cum-review-section",
            "Review run",
            "Revisit the Cannonball simulation once before answering questions drawn from the whole course.",
            (ACTIVITIES[0],),
        ),
        LessonSection(
            "cum-check-section",
            "Cumulative check",
            "Each item draws on a different lesson from the sequence. Numeric items expect a value and a unit; multiple-choice items expect one best answer.",
            (
                CheckpointQuestion(
                    "cum-velocity-check",
                    "A cart moves from x=-3.0 m to x=9.0 m in 4.0 s. What is its average velocity?",
                    QuestionKind.NUMERIC,
                    ("cum-velocity",),
                    unit_options=("m/s",),
                ),
                CheckpointQuestion(
                    "cum-acceleration-check",
                    "Velocity changes from 5.0 m/s to -1.0 m/s in 2.0 s. What is the average acceleration?",
                    QuestionKind.NUMERIC,
                    ("cum-acceleration",),
                    unit_options=("m/s^2",),
                ),
                CheckpointQuestion(
                    "cum-stopping-distance-check",
                    "A cart moving at 8.0 m/s brakes at a constant -4.0 m/s^2 until it stops. What is its stopping displacement?",
                    QuestionKind.NUMERIC,
                    ("cum-stopping-distance",),
                    unit_options=("m",),
                ),
                CheckpointQuestion(
                    "cum-components-check",
                    "A launcher fires at 10.0 m/s at 30 degrees above horizontal. What is the vertical component of the velocity?",
                    QuestionKind.NUMERIC,
                    ("cum-components",),
                    unit_options=("m/s",),
                ),
                CheckpointQuestion(
                    "cum-two-d-position-check",
                    "A projectile has an initial vertical velocity of 5.0 m/s (upward) and a_y=-9.81 m/s^2. What is its vertical position at t=0.30 s?",
                    QuestionKind.NUMERIC,
                    ("cum-two-d-position",),
                    unit_options=("m",),
                ),
                CheckpointQuestion(
                    "cum-model-limits-check",
                    "A projectile is launched with the same speed and angle in two trials, one with negligible air resistance and one with significant air resistance. Which quantity differs between the trials because of a change in the underlying physical model, not just measurement precision?",
                    QuestionKind.MULTIPLE_CHOICE,
                    ("cum-model-limits",),
                    (
                        AnswerChoice(
                            "range-changes",
                            "The range, because drag removes the constant-horizontal-velocity assumption.",
                        ),
                        AnswerChoice(
                            "angle-changes",
                            "The launch angle, because drag changes the angle at which the projectile leaves the launcher.",
                        ),
                        AnswerChoice(
                            "speed-changes",
                            "The initial speed, because drag acts before launch.",
                        ),
                    ),
                ),
                CheckpointQuestion(
                    "cum-independence-check",
                    "A ball is thrown horizontally from a height at the same instant a second ball is simply dropped from the same height. Ignoring air resistance, which ball reaches the ground first?",
                    QuestionKind.MULTIPLE_CHOICE,
                    ("cum-independence",),
                    (
                        AnswerChoice(
                            "same-time",
                            "They land at the same time, because both share the same initial vertical velocity and vertical acceleration.",
                        ),
                        AnswerChoice(
                            "thrown-first",
                            "The thrown ball lands first because its higher speed increases its downward acceleration.",
                        ),
                        AnswerChoice(
                            "dropped-first",
                            "The dropped ball lands first because it has no horizontal motion to slow its fall.",
                        ),
                    ),
                ),
            ),
        ),
    ),
    ACTIVITIES,
    estimated_minutes=30,
    next_lesson_id=None,
    next_lesson_title="Forces on an inclined plane",
)

CUMULATIVE_ASSESSMENTS = (
    AssessmentDefinition(
        "cum-velocity-check",
        CUMULATIVE_ASSESSMENT_LESSON.id,
        QuestionKind.NUMERIC,
        ("cum-velocity",),
        "Correct: average velocity is [9.0-(-3.0)]/4.0 = 3.0 m/s.",
        "Subtract initial position from final position before dividing by elapsed time.",
        expected_numeric_value=3.0,
        canonical_unit="m/s",
        absolute_tolerance=0.05,
        hints=("Compute [9.0-(-3.0)]/4.0.",),
    ),
    AssessmentDefinition(
        "cum-acceleration-check",
        CUMULATIVE_ASSESSMENT_LESSON.id,
        QuestionKind.NUMERIC,
        ("cum-acceleration",),
        "Correct: average acceleration is (-1.0-5.0)/2.0 = -3.0 m/s^2.",
        "Subtract initial velocity from final velocity before dividing by elapsed time.",
        expected_numeric_value=-3.0,
        canonical_unit="m/s^2",
        absolute_tolerance=0.05,
        hints=("Compute (-1.0-5.0)/2.0 and keep the sign.",),
    ),
    AssessmentDefinition(
        "cum-stopping-distance-check",
        CUMULATIVE_ASSESSMENT_LESSON.id,
        QuestionKind.NUMERIC,
        ("cum-stopping-distance",),
        "Correct: 0=8.0^2+2(-4.0) delta x gives a stopping displacement of 8.0 m.",
        "Use the time-independent constant-acceleration relation and keep the acceleration sign.",
        expected_numeric_value=8.0,
        canonical_unit="m",
        absolute_tolerance=0.1,
        hints=("Solve delta x=(v^2-v_0^2)/(2a) before inserting values.",),
    ),
    AssessmentDefinition(
        "cum-components-check",
        CUMULATIVE_ASSESSMENT_LESSON.id,
        QuestionKind.NUMERIC,
        ("cum-components",),
        "Correct: v_y=v_0 sin(theta)=10.0 sin(30 degrees)=5.0 m/s.",
        "Resolve the velocity arrow along the vertical axis using sine.",
        expected_numeric_value=5.0,
        canonical_unit="m/s",
        absolute_tolerance=0.1,
        hints=("Use the side opposite the angle: v_y=v_0 sin(theta).",),
    ),
    AssessmentDefinition(
        "cum-two-d-position-check",
        CUMULATIVE_ASSESSMENT_LESSON.id,
        QuestionKind.NUMERIC,
        ("cum-two-d-position",),
        "Correct: y=5.0(0.30)+0.5(-9.81)(0.30)^2 approximately 1.06 m.",
        "Apply the vertical constant-acceleration relation only; the horizontal component is irrelevant.",
        expected_numeric_value=1.06,
        canonical_unit="m",
        absolute_tolerance=0.05,
        hints=("Compute 5.0(0.30)+0.5(-9.81)(0.30)^2.",),
    ),
    AssessmentDefinition(
        "cum-model-limits-check",
        CUMULATIVE_ASSESSMENT_LESSON.id,
        QuestionKind.MULTIPLE_CHOICE,
        ("cum-model-limits",),
        "Correct: drag changes the acceleration model, so the range relation no longer applies directly.",
        "Ask which option changes a physical assumption rather than a cosmetic detail.",
        correct_choice_ids=("range-changes",),
        hints=("Air resistance changes forces, not the launcher's angle or the muzzle speed.",),
        misconception_by_choice=(
            ("angle-changes", "drag-changes-launch-conditions"),
            ("speed-changes", "drag-acts-before-launch"),
        ),
    ),
    AssessmentDefinition(
        "cum-independence-check",
        CUMULATIVE_ASSESSMENT_LESSON.id,
        QuestionKind.MULTIPLE_CHOICE,
        ("cum-independence",),
        "Correct: both balls share v_y0=0 and a_y=-g, so their vertical motion, and therefore fall time, is identical.",
        "Compare only the vertical component; horizontal speed does not affect vertical motion.",
        correct_choice_ids=("same-time",),
        hints=(
            "Write each ball's vertical velocity and acceleration separately from its horizontal motion.",
        ),
        misconception_by_choice=(
            ("thrown-first", "horizontal-speed-affects-fall"),
            ("dropped-first", "horizontal-motion-slows-fall"),
        ),
    ),
)
