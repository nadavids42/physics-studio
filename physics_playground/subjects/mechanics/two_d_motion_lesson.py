"""Bridge lesson: combining independent horizontal and vertical motion.

Sits between Vectors and components (m06) and Projectile motion from components,
so the projectile lesson does not have to introduce component independence and a
full range derivation in the same pass.
"""

from physics_playground.education.assessments import AssessmentDefinition
from physics_playground.education.models import (
    ActivityPhase,
    CheckpointQuestion,
    Concept,
    KnownValue,
    LearningObjective,
    Lesson,
    LessonSection,
    MisconceptionCallout,
    Prerequisite,
    PrerequisiteKind,
    Quantity,
    QuestionKind,
    ReasoningStep,
    SimulationActivity,
    Substitution,
    WorkedExample,
)
from physics_playground.models.simulations import LearningMode
from physics_playground.subjects.mechanics.kinematics_lessons import VECTORS_LESSON

TWO_D_MOTION_CONCEPTS = (
    Concept(
        "component_independence",
        "Independence of horizontal and vertical motion",
        "Horizontal and vertical motion share only elapsed time; each component obeys its own constant-velocity or constant-acceleration relation.",
        ("x(t)", "y(t)"),
        ("vectors", "kinematics"),
    ),
)

OBJECTIVES = (
    LearningObjective(
        "m07-independence",
        "State that horizontal and vertical motion evolve independently except for shared elapsed time.",
        "An explanation of why changing vertical acceleration does not change horizontal velocity.",
    ),
    LearningObjective(
        "m07-combine",
        "Combine constant-velocity horizontal motion with constant-acceleration vertical motion to find position at a given time.",
        "A correct two-component position calculation with units.",
    ),
)

ACTIVITIES = (
    SimulationActivity(
        "m07-predict-independence",
        ActivityPhase.PREDICTION,
        "cannonball",
        "Predict what changes when gravity changes",
        (
            "Keep launch speed and angle fixed.",
            "Predict whether increasing gravity changes the horizontal distance covered in the first second.",
            "Record a reason based on which component gravity accelerates.",
        ),
        LearningMode.EXPLORE,
        "Does a vertical force change a horizontal velocity?",
        "A prediction naming which component gravity affects.",
        objective_ids=("m07-independence",),
    ),
    SimulationActivity(
        "m07-analyze-components",
        ActivityPhase.ANALYSIS,
        "cannonball",
        "Track both components over time",
        (
            "Run one ideal launch and record horizontal position at t=0.5 s, 1.0 s, and 1.5 s.",
            "Record vertical position at the same three instants.",
            "Check that horizontal position grows linearly while vertical position does not.",
        ),
        LearningMode.ANALYZE,
        "Which position–time trace is a straight line and which is curved?",
        "Three timestamped horizontal and vertical position pairs.",
        objective_ids=("m07-independence", "m07-combine"),
        evidence_prompt="Record horizontal and vertical positions at three times",
    ),
    SimulationActivity(
        "m07-transfer-dropped-ball",
        ActivityPhase.REFLECTION,
        "cannonball",
        "Transfer to a ball released from a moving cart",
        (
            "A ball is released from a cart moving horizontally at constant velocity.",
            "Explain what the ball's horizontal and vertical motion look like after release, viewed from the ground.",
            "Name which component of its motion changes after release and which stays constant.",
        ),
        None,
        "Does releasing the ball change its horizontal velocity at that instant?",
        "A component-based transfer explanation.",
        objective_ids=("m07-independence",),
    ),
)

COMBINE_EXAMPLE = WorkedExample(
    "m07-combine-example",
    "Position from independent components",
    "A projectile has a constant horizontal velocity v_x=6.0 m/s and an initial vertical velocity v_y0=8.0 m/s, accelerating at a_y=-9.81 m/s^2. Find its position at t=0.50 s.",
    (
        KnownValue(Quantity("v_x", "horizontal velocity", "m/s"), 6.0),
        KnownValue(Quantity("v_y0", "initial vertical velocity", "m/s"), 8.0),
        KnownValue(Quantity("a_y", "vertical acceleration", "m/s^2"), -9.81),
        KnownValue(Quantity("t", "elapsed time", "s"), 0.50),
    ),
    Quantity("x, y", "position", "m"),
    (
        ReasoningStep(
            "m07-x-relation",
            "x = v_x t",
            "Horizontal velocity is constant, so horizontal position is a simple product.",
        ),
        ReasoningStep(
            "m07-y-relation",
            "y = v_y0 t + (1/2) a_y t^2",
            "Vertical position follows the constant-acceleration relation with its own acceleration; v_x does not appear.",
        ),
    ),
    (
        Substitution("x = (6.0 m/s)(0.50 s)", "x = 3.0 m"),
        Substitution("y = (8.0 m/s)(0.50 s) + 0.5(-9.81 m/s^2)(0.50 s)^2", "y ≈ 2.77 m"),
    ),
    "m/s multiplied by s gives m in both relations.",
    "x = 3.0 m, y ≈ 2.77 m",
    "The two positions come from two separate one-dimensional calculations that share only the elapsed time.",
)

TWO_D_MOTION_LESSON = Lesson(
    "m07-two-dimensional-motion",
    "2D motion: combining independent components",
    "Combine constant-velocity horizontal motion with constant-acceleration vertical motion before treating full projectile motion.",
    OBJECTIVES,
    (
        Prerequisite(
            "requires-m06-vectors-and-components",
            PrerequisiteKind.LESSON,
            VECTORS_LESSON.id,
            "Combining components requires resolving a launch velocity into v_x and v_y first.",
        ),
    ),
    ("component_independence", "vectors", "kinematics"),
    ("cannonball",),
    (
        LessonSection(
            "m07-independence-section",
            "Horizontal and vertical motion do not interact",
            "Once launched, the ideal projectile's horizontal velocity stays constant while gravity accelerates only the vertical component. The two components share elapsed time and nothing else.",
            (
                ACTIVITIES[0],
                MisconceptionCallout(
                    "m07-falls-slower-misconception",
                    "A projectile launched at an angle falls to the ground more slowly than one dropped straight down because it is also moving forward.",
                    "Vertical motion depends only on v_y0 and a_y. A projectile launched horizontally (v_y0=0) and one dropped from the same height land at the same time.",
                    "Does the horizontal velocity component appear anywhere in the vertical position relation?",
                ),
            ),
        ),
        LessonSection(
            "m07-combine-section",
            "Combining two one-dimensional models",
            "Position at any time is two independent calculations: constant-velocity horizontal motion x=v_x t, and constant-acceleration vertical motion y=v_y0 t + (1/2) a_y t^2.",
            (
                COMBINE_EXAMPLE,
                ACTIVITIES[1],
                CheckpointQuestion(
                    "m07-position-check",
                    "A projectile is launched horizontally (v_y0=0 m/s) with a_y=-9.81 m/s^2. What is its vertical position at t=0.40 s, taking down as negative?",
                    QuestionKind.NUMERIC,
                    ("m07-combine",),
                    unit_options=("m",),
                ),
            ),
        ),
        LessonSection(
            "m07-transfer-section",
            "Transfer beyond a launcher",
            "The same component independence applies to any two-dimensional constant-acceleration motion, not only cannon launches.",
            (ACTIVITIES[2],),
        ),
    ),
    ACTIVITIES,
    estimated_minutes=40,
    next_lesson_id="projectile-motion-from-components",
    next_lesson_title="Projectile motion from components",
)

TWO_D_MOTION_ASSESSMENTS = (
    AssessmentDefinition(
        "m07-position-check",
        TWO_D_MOTION_LESSON.id,
        QuestionKind.NUMERIC,
        ("m07-combine",),
        "Correct: y = 0 + 0.5(-9.81)(0.40)^2 ≈ -0.78 m.",
        "Use only the vertical relation; horizontal velocity does not enter it.",
        expected_numeric_value=-0.78,
        canonical_unit="m",
        absolute_tolerance=0.02,
        hints=("Compute 0.5 × (-9.81) × 0.40^2 and keep the sign.",),
    ),
)
