"""Streamlit renderer for typed educational pathways."""

from __future__ import annotations

from contextlib import nullcontext
from datetime import UTC, datetime
from uuid import uuid4

import streamlit as st

from physics_playground.application_callbacks import NotebookChanged, publish
from physics_playground.education.assessments import AssessmentAttempt, evaluate_response
from physics_playground.education.audience import (
    AudienceLevel,
    AudiencePreferences,
    MathematicalDepth,
    VisualDensity,
    applies_at_depth,
)
from physics_playground.education.catalog import ASSESSMENTS_BY_ID
from physics_playground.education.models import (
    ActivityPhase,
    CheckpointQuestion,
    EducationEventKind,
    EducationProgressEvent,
    GuidedDerivation,
    Lesson,
    MisconceptionCallout,
    SimulationActivity,
    WorkedExample,
)
from physics_playground.education.progress import PathwayProgress
from physics_playground.presentation.accessibility_ui import get_accessibility_settings
from physics_playground.presentation.profile_ui import get_notebook
from physics_playground.state_keys import SHARED_STATE_KEYS, feature_key, simulation_key


def _requirements(
    lesson: Lesson, depth: MathematicalDepth
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    visible_sections = tuple(
        section for section in lesson.sections if applies_at_depth(section, depth)
    )
    visible_activity_ids = {
        component.id
        for section in visible_sections
        for component in section.components
        if isinstance(component, SimulationActivity) and applies_at_depth(component, depth)
    }
    activities = tuple(
        activity.id for activity in lesson.activity_sequence if activity.id in visible_activity_ids
    )
    checkpoints = tuple(
        component.id
        for section in visible_sections
        for component in section.components
        if isinstance(component, CheckpointQuestion) and applies_at_depth(component, depth)
    )
    return activities, checkpoints


def _progress_map() -> dict[str, PathwayProgress]:
    value = st.session_state.setdefault(SHARED_STATE_KEYS.education_progress, {})
    if not isinstance(value, dict):
        value = {}
        st.session_state[SHARED_STATE_KEYS.education_progress] = value
    return value


def get_pathway_progress(lesson: Lesson) -> PathwayProgress:
    progress = _progress_map().get(lesson.id)
    if not isinstance(progress, PathwayProgress):
        progress = PathwayProgress(lesson.id)
        _progress_map()[lesson.id] = progress
    return progress


def _save_progress(
    progress: PathwayProgress,
    *,
    kind: EducationEventKind,
    activity_id: str | None = None,
    checkpoint_id: str | None = None,
) -> None:
    _progress_map()[progress.lesson_id] = progress
    publish(
        EducationProgressEvent(
            id=uuid4().hex,
            kind=EducationEventKind.LESSON_COMPLETED if progress.completed else kind,
            learner_id=str(st.session_state.get(SHARED_STATE_KEYS.profiles_active_id, "session")),
            lesson_id=progress.lesson_id,
            occurred_at=datetime.now(UTC),
            activity_id=activity_id,
            checkpoint_id=checkpoint_id,
            completed=progress.completed,
        )
    )


def _render_worked_example(example: WorkedExample, preferences: AudiencePreferences) -> None:
    st.markdown(f"#### Worked example: {example.title}")
    st.write(example.prompt)
    st.markdown("**Known values**")
    for known in example.known_values:
        value = known.display_value or f"{known.value:g} {known.quantity.unit}"
        st.markdown(f"- {known.quantity.symbol} ({known.quantity.name}) = {value}")
    st.markdown(
        f"**Unknown:** {example.unknown.symbol}, {example.unknown.name} ({example.unknown.unit})"
    )
    st.markdown("**Symbolic reasoning**")
    reasoning = (
        example.symbolic_reasoning[:1]
        if preferences.mathematical_depth is MathematicalDepth.CONCEPTUAL
        else example.symbolic_reasoning
    )
    for step in reasoning:
        st.latex(step.expression)
        st.caption(step.explanation)
    st.markdown("**Substitute only after the symbolic setup**")
    for substitution in example.substitutions:
        st.code(f"{substitution.expression}\n{substitution.result}")
    st.info(f"Unit check: {example.unit_check}")
    st.success(example.final_answer)
    st.write(example.final_interpretation)
    if preferences.mathematical_depth is MathematicalDepth.EXTENDED:
        st.caption(
            "Extension: compare this analytic value with progressively smaller numerical time steps before attributing a discrepancy to the physical model."
        )


def _render_derivation(derivation: GuidedDerivation) -> None:
    st.markdown(f"#### Guided derivation: {derivation.title}")
    st.write(derivation.goal)
    st.markdown("**Assumptions used in this derivation**")
    for assumption in derivation.assumptions:
        st.markdown(f"- {assumption}")
    for step in derivation.steps:
        with st.expander(f"Reveal step {step.reveal_order}: {step.prompt}"):
            if step.hint:
                st.caption(f"Hint: {step.hint}")
            st.latex(step.expression)
            st.write(step.explanation)
    st.info(derivation.conclusion)


def _render_checkpoint(
    lesson: Lesson,
    question: CheckpointQuestion,
    progress: PathwayProgress,
    preferences: AudiencePreferences,
) -> PathwayProgress:
    definition = ASSESSMENTS_BY_ID[question.id]
    st.markdown(f"#### Checkpoint: {question.prompt}")
    if question.id in progress.completed_checkpoint_ids:
        st.success("Checkpoint complete.")
        st.write(definition.success_feedback)
        return progress
    answer_key = feature_key("education", f"{lesson.id}.{question.id}.answer")
    answer = st.radio(
        "Choose an answer",
        [choice.id for choice in question.choices],
        format_func={choice.id: choice.text for choice in question.choices}.get,
        key=answer_key,
    )
    if st.button("Check answer", key=feature_key("education", f"{question.id}.submit")):
        correct = evaluate_response(definition, answer)
        attempt = AssessmentAttempt(
            id=uuid4().hex,
            learner_id="local",
            lesson_id=lesson.id,
            assessment_id=question.id,
            response=answer,
            correct=correct,
            submitted_at=datetime.now(UTC),
        )
        attempts_key = feature_key("education", "assessment_attempts")
        attempts = st.session_state.setdefault(attempts_key, [])
        attempts.append(attempt)
        if correct:
            activities, checkpoints = _requirements(lesson, preferences.mathematical_depth)
            updated = progress.complete_checkpoint(
                question.id,
                required_activity_ids=activities,
                required_checkpoint_ids=checkpoints,
                objective_ids=question.objective_ids,
                attempt_id=attempt.id,
            )
            _save_progress(
                updated,
                kind=EducationEventKind.CHECKPOINT_ATTEMPTED,
                checkpoint_id=question.id,
            )
            st.success(definition.success_feedback)
            return updated
        st.error("Not yet. Review the evidence and try again.")
        if definition.hints:
            st.info(f"Hint: {definition.hints[min(len(attempts) - 1, len(definition.hints) - 1)]}")
    return progress


def _render_activity(
    lesson: Lesson,
    activity: SimulationActivity,
    progress: PathwayProgress,
    preferences: AudiencePreferences,
) -> PathwayProgress:
    complete = activity.id in progress.completed_activity_ids
    st.markdown(f"#### {activity.phase.value.title()}: {activity.title}")
    for index, instruction in enumerate(activity.instructions, start=1):
        prefix = f"{index}." if preferences.audience is AudienceLevel.EXPLORER else "-"
        st.markdown(f"{prefix} {instruction}")
    if activity.observation_prompt:
        st.info(activity.observation_prompt)
    if preferences.visual_density is VisualDensity.DETAILED and activity.completion_evidence:
        st.caption(f"Evidence to record: {activity.completion_evidence}")
    activities, checkpoints = _requirements(lesson, preferences.mathematical_depth)
    if activity.phase is ActivityPhase.PREDICTION:
        if progress.prediction is not None:
            st.success(f"Saved prediction: {progress.prediction}")
            if st.button(
                "Reset prediction",
                key=feature_key("education", f"{lesson.id}.reset_prediction"),
            ):
                updated = progress.reset_prediction(activity.id)
                _save_progress(
                    updated,
                    kind=EducationEventKind.ACTIVITY_COMPLETED,
                    activity_id=activity.id,
                )
                return updated
            return progress
        prediction_key = feature_key("education", f"{lesson.id}.prediction")
        prediction = st.text_area("Record your prediction and physical reason", key=prediction_key)
        if st.button(
            "Save prediction",
            disabled=not prediction.strip(),
            key=feature_key("education", f"{lesson.id}.save_prediction"),
        ):
            updated = progress.save_prediction(
                prediction,
                activity.id,
                required_activity_ids=activities,
                required_checkpoint_ids=checkpoints,
            )
            _save_progress(
                updated,
                kind=EducationEventKind.ACTIVITY_COMPLETED,
                activity_id=activity.id,
            )
            return updated
        return progress
    if activity.phase is ActivityPhase.REFLECTION:
        reflection_key = feature_key("education", f"{lesson.id}.reflection")
        initial = progress.reflection or ""
        if reflection_key not in st.session_state:
            st.session_state[reflection_key] = initial
        response = st.text_area("Notebook reflection", key=reflection_key)
        if complete:
            st.success("Reflection saved to your notebook.")
        if st.button(
            "Save notebook reflection",
            disabled=not response.strip(),
            key=feature_key("education", f"{lesson.id}.save_reflection"),
        ):
            updated = progress.save_reflection(
                response,
                activity.id,
                required_activity_ids=activities,
                required_checkpoint_ids=checkpoints,
            )
            reflection = get_notebook().save_lesson_reflection(
                lesson_id=lesson.id,
                prompt=activity.observation_prompt,
                response=response,
            )
            _save_progress(
                updated,
                kind=EducationEventKind.ACTIVITY_COMPLETED,
                activity_id=activity.id,
            )
            publish(NotebookChanged(reflection.id))
            return updated
        return progress
    if activity.mode is not None and st.button(
        f"Open {activity.mode.value} mode",
        key=feature_key("education", f"{activity.id}.open_mode"),
    ):
        st.session_state[simulation_key(activity.simulation_id, "learning_mode")] = (
            activity.mode.value
        )
        st.toast(f"{activity.mode.value} mode selected below.")
    if complete:
        st.success("Activity complete.")
    elif st.button(
        "Mark activity complete",
        key=feature_key("education", f"{activity.id}.complete"),
    ):
        updated = progress.complete_activity(
            activity.id,
            required_activity_ids=activities,
            required_checkpoint_ids=checkpoints,
        )
        _save_progress(
            updated,
            kind=EducationEventKind.ACTIVITY_COMPLETED,
            activity_id=activity.id,
        )
        return updated
    return progress


def render_learning_pathway(lesson: Lesson) -> None:
    """Render a complete pathway while leaving simulation modes directly accessible."""

    progress = get_pathway_progress(lesson)
    preferences = get_accessibility_settings().instructional
    activities, checkpoints = _requirements(lesson, preferences.mathematical_depth)
    total = len(activities) + len(checkpoints)
    completed = len(progress.completed_activity_ids) + len(progress.completed_checkpoint_ids)
    requested_lesson = st.session_state.get(SHARED_STATE_KEYS.navigation_active_lesson)
    with st.expander(f"Learning pathway: {lesson.title}", expanded=requested_lesson == lesson.id):
        st.caption(f"About {lesson.estimated_minutes} minutes · {lesson.profile.depth.value}")
        introduction = {
            AudienceLevel.EXPLORER: "Begin with the path you can observe. Change one quantity at a time, record what changes, and use the equation to explain that evidence.",
            AudienceLevel.CORE: lesson.summary,
            AudienceLevel.ADVANCED: "Connect the measured trajectory and graphs to the analytic model, then test its assumptions and numerical limits.",
        }[preferences.audience]
        st.write(introduction)
        st.caption(
            f"{preferences.audience.value.title()} audience · {preferences.voice.value} voice · "
            f"{preferences.mathematical_depth.value} mathematics · {preferences.visual_density.value} density"
        )
        st.progress(completed / total if total else 0, text=f"{completed}/{total} steps complete")
        st.markdown("### Learning objectives")
        for objective in lesson.objectives:
            st.markdown(f"- {objective.statement}")
            if preferences.visual_density is VisualDensity.DETAILED:
                st.caption(f"Evidence: {objective.evidence}")
        st.markdown("### Prerequisites")
        for prerequisite in lesson.prerequisites:
            st.markdown(f"- {prerequisite.rationale}")
        for section in lesson.sections:
            if not applies_at_depth(section, preferences.mathematical_depth):
                continue
            st.divider()
            context = (
                st.expander(section.title)
                if preferences.visual_density is VisualDensity.FOCUSED
                else nullcontext()
            )
            with context:
                if preferences.visual_density is not VisualDensity.FOCUSED:
                    st.markdown(f"### {section.title}")
                st.write(section.narrative)
                for component in section.components:
                    if not applies_at_depth(component, preferences.mathematical_depth):
                        continue
                    if isinstance(component, SimulationActivity):
                        progress = _render_activity(lesson, component, progress, preferences)
                    elif isinstance(component, GuidedDerivation):
                        _render_derivation(component)
                    elif isinstance(component, WorkedExample):
                        _render_worked_example(component, preferences)
                    elif isinstance(component, MisconceptionCallout):
                        st.warning(
                            f"Common misconception: {component.misconception}\n\n"
                            f"Correction: {component.correction}"
                        )
                    elif isinstance(component, CheckpointQuestion):
                        progress = _render_checkpoint(lesson, component, progress, preferences)
        if progress.completed:
            st.success("Pathway complete. Your progress is saved with your active profile.")
        st.markdown(f"### Next lesson: {lesson.next_lesson_title}")
        st.caption(
            "Continue when you are ready; Explore, Compare, Analyze, and Model remain available below at any time."
        )
