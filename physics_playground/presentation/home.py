"""Registry- and curriculum-driven Physics Studio discovery surface."""

from __future__ import annotations

import streamlit as st

from physics_playground.education.models import CheckpointQuestion, Lesson
from physics_playground.education.progress import PathwayProgress
from physics_playground.missions.definitions import MISSION_DEFINITIONS
from physics_playground.models.simulations import Difficulty, SimulationDefinition
from physics_playground.presentation.navigation import NAVIGATION_SUBJECTS, recommended_lesson
from physics_playground.presentation.titles import scientific_title
from physics_playground.registry import SIMULATION_REGISTRY
from physics_playground.state_keys import SHARED_STATE_KEYS, feature_key


def _progress(definition: SimulationDefinition) -> tuple[int, int, float]:
    earned = sum(
        1
        for mission in MISSION_DEFINITIONS.values()
        if mission.group == definition.mission_group
        and mission.id in st.session_state[SHARED_STATE_KEYS.missions_completed]
    )
    total = definition.badge_count
    return earned, total, (earned / total if total else 0)


def _open_simulation(simulation_id: str, lesson_id: str | None = None) -> None:
    st.session_state[SHARED_STATE_KEYS.navigation_active] = simulation_id
    st.session_state[SHARED_STATE_KEYS.navigation_active_lesson] = lesson_id
    st.query_params["simulation"] = simulation_id
    if lesson_id:
        st.query_params["lesson"] = lesson_id
    elif "lesson" in st.query_params:
        del st.query_params["lesson"]


def _simulation_card(item: SimulationDefinition) -> None:
    earned, total, fraction = _progress(item)
    with st.container(border=True):
        st.markdown(f"### {scientific_title(item)}")
        st.markdown(f"**{item.central_question}**")
        st.write(item.description)
        st.caption(f"{item.difficulty.value} · {item.simulation_type}")
        st.markdown(" · ".join(f"`{concept}`" for concept in item.concepts))
        st.progress(fraction, text=f"{earned}/{total} achievements · {fraction:.0%} complete")
        st.button(
            f"{'Continue' if earned else 'Open'} {scientific_title(item)}",
            key=feature_key("home", f"open.{item.id}"),
            type="primary",
            use_container_width=True,
            on_click=_open_simulation,
            args=(item.id,),
        )


def _lesson_progress(lesson: Lesson) -> PathwayProgress:
    stored = st.session_state.get(SHARED_STATE_KEYS.education_progress, {})
    if isinstance(stored, dict) and isinstance(stored.get(lesson.id), PathwayProgress):
        return stored[lesson.id]
    return PathwayProgress(lesson.id)


def _lesson_card(lesson: Lesson, subject_title: str, unit_title: str) -> None:
    progress = _lesson_progress(lesson)
    complete_count = len(progress.completed_activity_ids) + len(progress.completed_checkpoint_ids)
    total = len(lesson.activity_sequence) + sum(
        1
        for section in lesson.sections
        for component in section.components
        if isinstance(component, CheckpointQuestion)
    )
    with st.container(border=True):
        st.markdown(f"### {lesson.title}")
        st.caption(f"{subject_title} · {unit_title} · about {lesson.estimated_minutes} minutes")
        st.write(lesson.summary)
        st.progress(
            1.0 if progress.completed else min(complete_count / max(total, 1), 1.0),
            text="Complete"
            if progress.completed
            else f"{complete_count}/{total} activities complete",
        )
        simulation_id = lesson.simulation_ids[0]
        st.button(
            f"{'Review' if progress.completed else 'Continue' if complete_count else 'Start'} lesson",
            key=feature_key("home", f"lesson.{lesson.id}"),
            type="primary",
            use_container_width=True,
            on_click=_open_simulation,
            args=(simulation_id, lesson.id),
        )


def _filters() -> tuple[str, str, str, str, str]:
    subject_options = ["all", *[subject.id for subject in NAVIGATION_SUBJECTS]]
    subject_titles = {
        "all": "All subjects",
        **{item.id: item.title for item in NAVIGATION_SUBJECTS},
    }
    requested_subject = st.session_state.get(SHARED_STATE_KEYS.navigation_subject_filter, "all")
    if requested_subject not in subject_options:
        requested_subject = "all"
    c1, c2 = st.columns(2)
    with c1:
        search = st.text_input(
            "Search lessons and simulations",
            placeholder="Try momentum, waves, or projectile motion",
            key=feature_key("home", "search"),
        )
    with c2:
        subject = st.selectbox(
            "Subject",
            subject_options,
            index=subject_options.index(requested_subject),
            format_func=subject_titles.get,
            key=feature_key("home", "subject"),
        )
    concepts = sorted(
        {
            concept
            for nav_subject in NAVIGATION_SUBJECTS
            if subject == "all" or nav_subject.id == subject
            for concept in nav_subject.concepts
        }
    )
    c3, c4, c5 = st.columns(3)
    with c3:
        concept = st.selectbox("Concept", ["All concepts", *concepts])
    with c4:
        difficulty = st.selectbox(
            "Difficulty", ["All levels", *[item.value for item in Difficulty]]
        )
    with c5:
        status = st.selectbox("Progress", ["All progress", "Completed", "In progress"])
    return search.strip().casefold(), subject, concept, difficulty, status


def _matching_simulations(filters: tuple[str, str, str, str, str]):
    search, subject, concept, difficulty, status = filters
    subject_ids = {
        item.id: {simulation.id for simulation in item.simulations} for item in NAVIGATION_SUBJECTS
    }
    for item in SIMULATION_REGISTRY:
        earned, _, fraction = _progress(item)
        searchable = " ".join((item.title, item.description, *item.concepts)).casefold()
        if search and search not in searchable:
            continue
        if subject != "all" and item.id not in subject_ids[subject]:
            continue
        if concept != "All concepts" and concept not in item.concepts:
            continue
        if difficulty != "All levels" and difficulty != item.difficulty.value:
            continue
        if status == "Completed" and fraction < 1:
            continue
        if status == "In progress" and (not earned or fraction >= 1):
            continue
        yield item


def render_home() -> None:
    st.title("Physics Studio")
    st.caption(
        f"Explore {len(SIMULATION_REGISTRY)} interactive simulations and guided lessons. "
        "Recommendations are optional; every simulation remains available."
    )
    recommendation = recommended_lesson(
        st.session_state.get(SHARED_STATE_KEYS.education_progress, {})
    )
    if recommendation:
        with st.container(border=True):
            st.markdown("### Recommended next")
            st.write(recommendation.title)
            st.caption("Continue the guided pathway, or browse anything below.")
            st.button(
                "Open recommended lesson",
                key=feature_key("home", "recommended_lesson"),
                on_click=_open_simulation,
                args=(recommendation.simulation_ids[0], recommendation.id),
            )

    st.markdown("## Discover")
    filters = _filters()
    lessons_tab, simulations_tab, progress_tab = st.tabs(
        ("Lessons", "Simulations", "Learner progress")
    )
    with lessons_tab:
        matching_lessons = []
        for subject in NAVIGATION_SUBJECTS:
            if filters[1] not in ("all", subject.id):
                continue
            for lesson in subject.lessons:
                text = f"{lesson.title} {lesson.summary}".casefold()
                if filters[0] and filters[0] not in text:
                    continue
                matching_lessons.append((lesson, subject.title, subject.units[0]))
        if not matching_lessons:
            st.info("No lessons match these filters yet. Try the Simulations tab.")
        for lesson, subject_title, unit_title in matching_lessons:
            _lesson_card(lesson, subject_title, unit_title)
    with simulations_tab:
        items = list(_matching_simulations(filters))
        if not items:
            st.info("No simulations match these filters.")
        columns = st.columns(2)
        for index, item in enumerate(items):
            with columns[index % 2]:
                _simulation_card(item)
    with progress_tab:
        completed_lessons = sum(
            _lesson_progress(lesson).completed
            for subject in NAVIGATION_SUBJECTS
            for lesson in subject.lessons
        )
        total_lessons = sum(len(subject.lessons) for subject in NAVIGATION_SUBJECTS)
        completed_simulations = sum(_progress(item)[2] >= 1 for item in SIMULATION_REGISTRY)
        st.metric("Lessons completed", f"{completed_lessons}/{total_lessons}")
        st.metric(
            "Simulation achievement sets completed",
            f"{completed_simulations}/{len(SIMULATION_REGISTRY)}",
        )
