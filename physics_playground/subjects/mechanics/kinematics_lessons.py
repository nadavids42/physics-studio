"""Connected introductory kinematics lessons following Mechanics lesson 1."""

from physics_playground.education.assessments import AssessmentDefinition
from physics_playground.education.models import (
    ActivityPhase,
    AnswerChoice,
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

KINEMATICS_CONCEPTS = (
    Concept(
        "motion_coordinates",
        "Position and displacement",
        "Position locates an object relative to an origin; displacement is final position minus initial position.",
        ("x", "delta x", "d"),
        ("kinematics", "motion_graphs"),
    ),
    Concept(
        "motion_graphs",
        "Motion graphs",
        "Position, velocity, and acceleration graphs are linked by slope and signed area.",
        ("x(t)", "v(t)", "a(t)"),
        ("motion_coordinates", "kinematics"),
    ),
)


def lesson_prerequisite(lesson_id: str, title: str) -> Prerequisite:
    """Create the shared required-lesson prerequisite used by this sequence."""

    return Prerequisite(
        f"requires-{lesson_id}",
        PrerequisiteKind.LESSON,
        lesson_id,
        f"Complete {title} before continuing this representation sequence.",
    )


POSITION_OBJECTIVES = (
    LearningObjective(
        "m02-position-displacement",
        "Distinguish position, displacement, and distance in a stated coordinate system.",
        "A signed displacement and nonnegative distance supported by a diagram or simulation record.",
    ),
    LearningObjective(
        "m02-speed-velocity",
        "Distinguish average velocity from average speed using units and direction.",
        "A transfer calculation that reports velocity with sign and speed as a nonnegative scalar.",
    ),
)

POSITION_ACTIVITIES = (
    SimulationActivity(
        "m02-predict-round-trip",
        ActivityPhase.PREDICTION,
        "bumper_cars",
        "Predict a round-trip result",
        (
            "Imagine a cart moving 4 m right and then 4 m left.",
            "Predict its displacement, distance, average velocity, and average speed before running a comparison.",
        ),
        LearningMode.EXPLORE,
        {},
        "Which quantities remember direction and which accumulate path length?",
        "A signed prediction with units and a reason.",
        objective_ids=("m02-position-displacement", "m02-speed-velocity"),
    ),
    SimulationActivity(
        "m02-observe-carts",
        ActivityPhase.EXPLORATION,
        "bumper_cars",
        "Track two cart positions",
        (
            "Choose an origin and positive direction on the collision track.",
            "Record each cart's initial and final position for one run.",
            "Calculate displacement from endpoints and explain why the traveled distance may differ.",
        ),
        LearningMode.EXPLORE,
        {},
        "State the coordinate choice before interpreting a negative value.",
        "Positions, signed displacements, units, and a distance comparison.",
        objective_ids=("m02-position-displacement",),
        evidence_prompt="Record the coordinate choice, positions, displacement, and distance reasoning",
    ),
    SimulationActivity(
        "m02-transfer",
        ActivityPhase.REFLECTION,
        "bumper_cars",
        "Transfer to a walking route",
        (
            "A learner walks 30 m east and 10 m west in 20 s.",
            "Explain how the cart representation transfers to this route.",
            "Report distance, displacement, average speed, and average velocity with units.",
        ),
        None,
        {},
        "Which answer changes if east is declared negative?",
        "A complete transfer solution with a coordinate convention.",
        objective_ids=("m02-position-displacement", "m02-speed-velocity"),
    ),
)

POSITION_EXAMPLE = WorkedExample(
    "m02-round-trip-example",
    "A partial return trip",
    "A cart moves from x=−2 m to x=5 m and then returns to x=1 m in 6 s.",
    (
        KnownValue(Quantity("x_i", "initial position", "m"), -2.0),
        KnownValue(Quantity("x_turn", "turning position", "m"), 5.0),
        KnownValue(Quantity("x_f", "final position", "m"), 1.0),
        KnownValue(Quantity("delta t", "elapsed time", "s"), 6.0),
    ),
    Quantity("v_avg", "average velocity", "m/s"),
    (
        ReasoningStep(
            "m02-displacement", "delta x = x_f - x_i", "Only endpoints determine displacement."
        ),
        ReasoningStep(
            "m02-distance", "d = |5-(-2)| + |1-5|", "Distance adds each path segment without signs."
        ),
        ReasoningStep(
            "m02-velocity",
            "v_avg = delta x / delta t",
            "Average velocity keeps the displacement sign.",
        ),
    ),
    (
        Substitution("delta x = 1 m - (-2 m)", "delta x = +3 m"),
        Substitution("d = 7 m + 4 m", "d = 11 m"),
        Substitution("v_avg = 3 m / 6 s", "v_avg = +0.50 m/s"),
    ),
    "metres divided by seconds gives m/s; displacement and distance remain in metres.",
    "delta x = +3 m, d = 11 m, v_avg = +0.50 m/s",
    "The cart traveled 11 m but ended only 3 m to the right of where it began.",
)

POSITION_LESSON = Lesson(
    "m02-position-velocity",
    "Position, displacement, velocity, and speed",
    "Build signed motion quantities from an explicit origin and coordinate direction.",
    POSITION_OBJECTIVES,
    (lesson_prerequisite("m01-measurement-models", "Models, Measurements, and Representations"),),
    ("motion_coordinates", "kinematics"),
    ("bumper_cars",),
    (
        LessonSection(
            "m02-coordinate-model",
            "Position needs an origin",
            "Position is a coordinate, not a distance traveled. Choose an origin and positive direction before assigning signs. Displacement delta x=x_f−x_i depends only on endpoints; distance accumulates the path and cannot be negative.",
            (POSITION_ACTIVITIES[0],),
        ),
        LessonSection(
            "m02-velocity-speed",
            "Velocity retains direction",
            "Average velocity is displacement divided by elapsed time. Average speed is distance divided by elapsed time. A negative velocity means motion in the negative coordinate direction; it does not by itself mean the object is slowing down.",
            (
                POSITION_EXAMPLE,
                MisconceptionCallout(
                    "m02-negative-slowing",
                    "Negative velocity means an object is slowing down.",
                    "Velocity sign gives direction. Speed decreases only when velocity and acceleration point in opposite directions.",
                    "Can a left-moving object with increasingly negative velocity be speeding up?",
                ),
                POSITION_ACTIVITIES[1],
                CheckpointQuestion(
                    "m02-round-trip-check",
                    "A runner completes one lap and stops at the starting line. Which statement is correct?",
                    QuestionKind.MULTIPLE_CHOICE,
                    ("m02-position-displacement", "m02-speed-velocity"),
                    (
                        AnswerChoice(
                            "zero-v-positive-speed",
                            "Displacement and average velocity are zero; distance and average speed are positive.",
                        ),
                        AnswerChoice("all-zero", "All four quantities are zero."),
                        AnswerChoice(
                            "negative-speed",
                            "Average speed is negative because part of the lap reverses direction.",
                        ),
                    ),
                ),
            ),
        ),
        LessonSection(
            "m02-transfer-section",
            "Transfer beyond the track",
            "Coordinate choices may change signs, but they do not change the physical path. Use a fresh context to test whether the distinctions transfer.",
            (POSITION_ACTIVITIES[2],),
        ),
    ),
    POSITION_ACTIVITIES,
    estimated_minutes=50,
    next_lesson_id="m03-motion-graphs",
    next_lesson_title="Velocity, acceleration, and motion graphs",
)

GRAPH_OBJECTIVES = (
    LearningObjective(
        "m03-graph-links",
        "Connect position, velocity, and acceleration graphs using slope and signed area.",
        "A graph interpretation that identifies quantities, signs, intervals, and units.",
    ),
    LearningObjective(
        "m03-acceleration",
        "Reason about acceleration as change in velocity rather than direction of motion.",
        "A qualitative prediction and numerical average-acceleration calculation.",
    ),
)

GRAPH_ACTIVITIES = (
    SimulationActivity(
        "m03-predict-apex",
        ActivityPhase.PREDICTION,
        "cannonball",
        "Predict velocity and acceleration at the apex",
        (
            "Predict the vertical velocity at the highest point.",
            "Predict the vertical acceleration at that same instant and explain why.",
        ),
        LearningMode.EXPLORE,
        {"initial_speed_m_s": 20.0, "launch_angle_deg": 60.0, "drag_enabled": False},
        "Does an instant of zero vertical velocity switch gravity off?",
        "A prediction distinguishing velocity from acceleration.",
        objective_ids=("m03-acceleration",),
    ),
    SimulationActivity(
        "m03-analyze-graphs",
        ActivityPhase.ANALYSIS,
        "cannonball",
        "Connect trajectory measurements",
        (
            "Use an ideal run and identify intervals where vertical velocity is positive, zero, and negative.",
            "Relate the slope of vertical position to vertical velocity and the slope of velocity to acceleration.",
            "Record graph evidence; do not infer acceleration from the direction of travel alone.",
        ),
        LearningMode.ANALYZE,
        {"initial_speed_m_s": 20.0, "launch_angle_deg": 60.0, "drag_enabled": False},
        "How are x(t), v(t), and a(t) connected without treating the graphs as pictures of the path?",
        "A three-representation explanation with signed intervals and units.",
        objective_ids=("m03-graph-links", "m03-acceleration"),
        evidence_prompt="Record your position–velocity–acceleration graph evidence",
    ),
    SimulationActivity(
        "m03-transfer-braking",
        ActivityPhase.REFLECTION,
        "cannonball",
        "Transfer to a braking vehicle",
        (
            "A car moves in the positive direction while its velocity decreases.",
            "Sketch or describe the signs and trends of position, velocity, and acceleration.",
            "Contrast this with a negative-velocity object that is speeding up.",
        ),
        None,
        {},
        "Which graph feature—not the sign of velocity—shows slowing?",
        "A coherent verbal or sketched three-graph transfer.",
        objective_ids=("m03-graph-links", "m03-acceleration"),
    ),
)

ACCELERATION_EXAMPLE = WorkedExample(
    "m03-acceleration-example",
    "Average acceleration from velocity data",
    "Velocity changes from −2.0 m/s to −8.0 m/s in 3.0 s.",
    (
        KnownValue(Quantity("v_i", "initial velocity", "m/s"), -2.0),
        KnownValue(Quantity("v_f", "final velocity", "m/s"), -8.0),
        KnownValue(Quantity("delta t", "time interval", "s"), 3.0),
    ),
    Quantity("a_avg", "average acceleration", "m/s^2"),
    (
        ReasoningStep(
            "m03-definition",
            "a_avg=(v_f-v_i)/delta t",
            "Acceleration measures velocity change, including sign.",
        ),
    ),
    (Substitution("a_avg=[-8.0-(-2.0)] m/s / 3.0 s", "a_avg=-2.0 m/s^2"),),
    "(m/s)/s = m/s^2.",
    "a_avg = −2.0 m/s²",
    "Velocity and acceleration are both negative, so the magnitude of velocity increases: the object speeds up.",
)

GRAPH_LESSON = Lesson(
    "m03-motion-graphs",
    "Velocity, acceleration, and motion graphs",
    "Link position, velocity, and acceleration as coordinated representations of one motion.",
    GRAPH_OBJECTIVES,
    (lesson_prerequisite(POSITION_LESSON.id, POSITION_LESSON.title),),
    ("motion_graphs", "kinematics"),
    ("cannonball",),
    (
        LessonSection(
            "m03-prediction",
            "An instant is not an interval",
            "Velocity describes how position changes; acceleration describes how velocity changes. They can be zero or nonzero independently.",
            (
                GRAPH_ACTIVITIES[0],
                MisconceptionCallout(
                    "m03-zero-v-zero-a",
                    "Zero velocity means zero acceleration.",
                    "At a projectile's apex, vertical velocity is momentarily zero while downward acceleration remains approximately −9.81 m/s².",
                    "What happens to vertical velocity immediately after the apex?",
                ),
            ),
        ),
        LessonSection(
            "m03-linked-graphs",
            "Slope and signed area",
            "The slope of x(t) is velocity; the slope of v(t) is acceleration. Signed area under v(t) gives displacement, and signed area under a(t) gives velocity change. Axis units determine slope and area units.",
            (
                ACCELERATION_EXAMPLE,
                GRAPH_ACTIVITIES[1],
                CheckpointQuestion(
                    "m03-direction-check",
                    "An object has negative velocity and negative acceleration. What happens to its speed?",
                    QuestionKind.MULTIPLE_CHOICE,
                    ("m03-acceleration",),
                    (
                        AnswerChoice(
                            "speed-up",
                            "It speeds up because velocity and acceleration point in the same direction.",
                        ),
                        AnswerChoice("slow-down", "It slows down because velocity is negative."),
                        AnswerChoice(
                            "cannot-move",
                            "It cannot move because acceleration must point with positive motion.",
                        ),
                    ),
                ),
            ),
        ),
        LessonSection(
            "m03-transfer",
            "Transfer among representations",
            "Translate a motion story into compatible position, velocity, and acceleration trends. Acceleration need not point in the direction of motion; it points in the direction of velocity change.",
            (
                MisconceptionCallout(
                    "m03-accel-motion",
                    "Acceleration always points in the direction of motion.",
                    "Acceleration points in the direction velocity changes. Braking acceleration opposes motion.",
                    "What direction is acceleration while a right-moving car brakes?",
                ),
                GRAPH_ACTIVITIES[2],
            ),
        ),
    ),
    GRAPH_ACTIVITIES,
    estimated_minutes=55,
    next_lesson_id="m05-constant-acceleration",
    next_lesson_title="Constant-acceleration models",
)

CONSTANT_OBJECTIVES = (
    LearningObjective(
        "m05-derive",
        "Derive constant-acceleration relationships from graph slope and area.",
        "A symbolic chain from constant acceleration to velocity and position with units.",
    ),
    LearningObjective(
        "m05-apply",
        "Apply and critique a constant-acceleration model in one and two dimensions.",
        "A controlled simulation comparison and transfer solution with assumptions and limits.",
    ),
)

CONSTANT_ACTIVITIES = (
    SimulationActivity(
        "m05-predict-mass",
        ActivityPhase.PREDICTION,
        "inclined_plane",
        "Predict the effect of mass",
        (
            "For a frictionless incline, predict whether a heavier block has greater acceleration.",
            "Name the forces and state what is held fixed.",
        ),
        LearningMode.EXPLORE,
        {},
        "Does greater gravitational force necessarily mean greater acceleration?",
        "A force-and-mass prediction with a model assumption.",
        objective_ids=("m05-apply",),
    ),
    SimulationActivity(
        "m05-observe-incline",
        ActivityPhase.EXPLORATION,
        "inclined_plane",
        "Test constant acceleration",
        (
            "Hold angle and friction fixed and compare two masses.",
            "Record acceleration with units for each run.",
            "Explain the result using F_net=ma and identify one limitation of the model.",
        ),
        LearningMode.EXPLORE,
        {},
        "Changing mass is evidence only when the comparison and reasoning are recorded.",
        "Two controlled measurements and a force-law explanation.",
        objective_ids=("m05-derive", "m05-apply"),
        evidence_prompt="Record the controlled mass comparison, units, reasoning, and limitation",
    ),
    SimulationActivity(
        "m05-transfer-projectile",
        ActivityPhase.REFLECTION,
        "inclined_plane",
        "Transfer constant acceleration to two dimensions",
        (
            "Explain why horizontal and vertical projectile components can share time but have different accelerations.",
            "State the assumptions needed for constant downward acceleration.",
            "Predict what drag changes.",
        ),
        None,
        {},
        "How does one-dimensional constant-acceleration reasoning become a two-component model?",
        "A component-based transfer argument with assumptions.",
        objective_ids=("m05-derive", "m05-apply"),
    ),
)

CONSTANT_EXAMPLE = WorkedExample(
    "m05-stopping-example",
    "Stopping distance",
    "A cart moving at 12.0 m/s brakes at a constant −3.0 m/s². Find its stopping distance.",
    (
        KnownValue(Quantity("v_i", "initial velocity", "m/s"), 12.0),
        KnownValue(Quantity("v_f", "final velocity", "m/s"), 0.0),
        KnownValue(Quantity("a", "acceleration", "m/s^2"), -3.0),
    ),
    Quantity("delta x", "stopping displacement", "m"),
    (
        ReasoningStep(
            "m05-select",
            "v_f^2=v_i^2+2a delta x",
            "This relation follows by eliminating time from constant-acceleration graph relationships.",
        ),
        ReasoningStep(
            "m05-solve", "delta x=(v_f^2-v_i^2)/(2a)", "Solve symbolically before substitution."
        ),
    ),
    (Substitution("delta x=[0-(12.0 m/s)^2]/[2(-3.0 m/s^2)]", "delta x=24.0 m"),),
    "(m²/s²)/(m/s²)=m.",
    "delta x = 24.0 m",
    "The positive displacement matches forward motion while negative acceleration reduces the speed.",
)

CONSTANT_LESSON = Lesson(
    "m05-constant-acceleration",
    "Constant-acceleration reasoning",
    "Derive, apply, and test a constant-acceleration model before transferring it to projectile components.",
    CONSTANT_OBJECTIVES,
    (lesson_prerequisite(GRAPH_LESSON.id, GRAPH_LESSON.title),),
    ("kinematics", "motion_graphs"),
    ("inclined_plane",),
    (
        LessonSection(
            "m05-model",
            "From graphs to equations",
            "For constant acceleration, the velocity graph has constant slope: v=v_0+at. Its signed area gives displacement, producing delta x=v_0t+(1/2)at². These relations describe a model interval, not every motion.",
            (CONSTANT_ACTIVITIES[0],),
        ),
        LessonSection(
            "m05-example",
            "Symbolic and numerical reasoning",
            "Select a relation only after defining coordinates, interval, known quantities, and the constant-acceleration assumption.",
            (
                CONSTANT_EXAMPLE,
                CheckpointQuestion(
                    "m05-stop-check",
                    "A car moving right slows at a constant rate. Which sign combination is consistent with +x to the right?",
                    QuestionKind.MULTIPLE_CHOICE,
                    ("m05-derive",),
                    (
                        AnswerChoice(
                            "positive-negative", "Positive velocity and negative acceleration."
                        ),
                        AnswerChoice(
                            "negative-negative", "Negative velocity and negative acceleration."
                        ),
                        AnswerChoice(
                            "positive-positive", "Positive velocity and positive acceleration."
                        ),
                    ),
                ),
            ),
        ),
        LessonSection(
            "m05-evidence",
            "Test assumptions and transfer",
            "On a frictionless incline, both the downslope force and inertia scale with mass, so mass cancels from acceleration. In ideal projectile motion, the same constant-acceleration reasoning applies separately to horizontal and vertical components.",
            (
                MisconceptionCallout(
                    "m05-heavy-faster",
                    "Heavier projectiles fall faster in the ideal model.",
                    "With the same gravitational field and negligible drag, gravitational acceleration is independent of projectile mass.",
                    "Which factor cancels when F_g=mg is inserted into F=ma?",
                ),
                CONSTANT_ACTIVITIES[1],
                CONSTANT_ACTIVITIES[2],
            ),
        ),
    ),
    CONSTANT_ACTIVITIES,
    estimated_minutes=60,
    next_lesson_id="projectile-motion-from-components",
    next_lesson_title="Projectile motion from components",
)

KINEMATICS_LESSONS = (POSITION_LESSON, GRAPH_LESSON, CONSTANT_LESSON)

KINEMATICS_ASSESSMENTS = (
    AssessmentDefinition(
        "m02-round-trip-check",
        POSITION_LESSON.id,
        QuestionKind.MULTIPLE_CHOICE,
        ("m02-position-displacement", "m02-speed-velocity"),
        "Correct: endpoint displacement is zero while path length is positive.",
        "Separate endpoint change from accumulated path length.",
        correct_choice_ids=("zero-v-positive-speed",),
        misconception_by_choice=(
            ("all-zero", "distance-equals-displacement"),
            ("negative-speed", "speed-has-direction"),
        ),
    ),
    AssessmentDefinition(
        "m03-direction-check",
        GRAPH_LESSON.id,
        QuestionKind.MULTIPLE_CHOICE,
        ("m03-acceleration",),
        "Correct: matching velocity and acceleration signs increase speed.",
        "Use the relative directions of velocity and acceleration, not whether a sign is negative.",
        correct_choice_ids=("speed-up",),
        misconception_by_choice=(
            ("slow-down", "negative-velocity-means-slowing"),
            ("cannot-move", "acceleration-follows-motion"),
        ),
    ),
    AssessmentDefinition(
        "m05-stop-check",
        CONSTANT_LESSON.id,
        QuestionKind.MULTIPLE_CHOICE,
        ("m05-derive",),
        "Correct: acceleration opposes the positive velocity while the car slows.",
        "Apply the stated coordinate direction separately to velocity and velocity change.",
        correct_choice_ids=("positive-negative",),
        misconception_by_choice=(
            ("negative-negative", "negative-velocity-means-slowing"),
            ("positive-positive", "acceleration-follows-motion"),
        ),
    ),
)
