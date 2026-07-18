# Learning pathways

Physics Studio's first complete pathway is **Projectile motion from components**, delivered inside
the Cannonball Launcher page. It uses the presentation-independent lesson manifest in
`physics_playground/subjects/mechanics/cannonball/lesson.py` and the shared Streamlit renderer in
`physics_playground/presentation/pathway_ui.py`.

The pathway sequences prediction, exploration, controlled comparison, graph analysis, modeling,
and reflection. Equations are introduced through observed component motion, tested against the
range-versus-angle graph, derived progressively, checked dimensionally, and challenged with a drag
model. The simulation's Explore, Compare, Analyze, and Model controls remain directly available
below the pathway.

## Progress and persistence

`PathwayProgress` is a renderer-independent immutable value. It records completed activities,
completed checkpoints, the saved prediction, the notebook reflection, and overall completion.
Streamlit stores a map of these values under `SHARED_STATE_KEYS.education_progress`.

Every pathway change publishes a typed `EducationProgressEvent` through the existing application
callback seam. The profile subscriber serializes the progress map into `LocalProfile`; loading or
switching a profile reconstructs typed progress values. No pathway service imports profile or
Streamlit code.

A completed prediction is shown to returning learners instead of presenting a required input again.
The explicit **Reset prediction** action removes only that prediction and its activity completion,
allowing another attempt without erasing unrelated work.

Lesson reflections are stored as `LessonReflection` entries in the existing experiment notebook.
Saving a new reflection for the same lesson replaces the earlier response, so restoration remains
deterministic and the notebook does not accumulate accidental duplicates.

## Adding another pathway

1. Author and validate a complete `Lesson` manifest as described in `LESSON_AUTHORING.md`.
2. Enroll the lesson in the curriculum catalog.
3. Render it from the appropriate simulation slice with `render_learning_pathway()`.
4. Ensure activity mode links use the simulation's standard namespaced `learning_mode` key.
5. Add sequencing, completion, reset, profile restoration, notebook reflection, and AppTest coverage.

Pathways currently use explicit sequencing. Adaptive recommendations, grading policy, and teacher
dashboards remain outside this layer.
