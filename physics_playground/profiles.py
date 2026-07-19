"""SQLite-backed local learner profiles with schema migration and JSON export."""

from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from uuid import uuid4

from physics_playground.learning_store import (
    STORE_SCHEMA_VERSION,
    LearnerData,
    LearnerIdentity,
    SQLiteLearningStore,
)
from physics_playground.version import APPLICATION_VERSION

SCHEMA_VERSION = STORE_SCHEMA_VERSION


class PersistenceUnavailable(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class LocalProfile:
    """Compatibility projection for the current Streamlit UI and legacy exports."""

    id: str
    display_name: str
    badges_earned: tuple[str, ...] = ()
    trial_notebook: Mapping[str, object] = field(default_factory=dict)
    last_used_simulation: str | None = None
    last_used_parameters: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    favorite_simulation: str | None = None
    total_experiment_count: int = 0
    learner_observations: tuple[str, ...] = ()
    application_version: str = APPLICATION_VERSION
    profile_schema_version: int = SCHEMA_VERSION
    accessibility_settings: Mapping[str, object] = field(default_factory=dict)
    educational_progress: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    assessment_attempts: tuple[Mapping[str, object], ...] = ()
    objective_evidence: tuple[Mapping[str, object], ...] = ()

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=str(data.get("id") or uuid4().hex),
            display_name=str(data.get("display_name") or "Scientist"),
            badges_earned=tuple(data.get("badges_earned", ())),
            trial_notebook=dict(data.get("trial_notebook", {})),
            last_used_simulation=data.get("last_used_simulation"),
            last_used_parameters=dict(data.get("last_used_parameters", {})),
            favorite_simulation=data.get("favorite_simulation"),
            total_experiment_count=int(data.get("total_experiment_count", 0)),
            learner_observations=tuple(data.get("learner_observations", ())),
            application_version=str(data.get("application_version", "unknown")),
            profile_schema_version=SCHEMA_VERSION,
            accessibility_settings=dict(data.get("accessibility_settings", {})),
            educational_progress=dict(data.get("educational_progress", {})),
            assessment_attempts=tuple(
                dict(item) for item in data.get("assessment_attempts", ()) if isinstance(item, dict)
            ),
            objective_evidence=tuple(
                dict(item) for item in data.get("objective_evidence", ()) if isinstance(item, dict)
            ),
        )


class ProfileStore:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(
            path
            or os.environ.get(
                "PHYSICS_PLAYGROUND_DB", Path.home() / ".physics_playground" / "profiles.sqlite3"
            )
        )
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.learning = SQLiteLearningStore(self.path)
        except (OSError, sqlite3.Error) as error:
            raise PersistenceUnavailable(str(error)) from error

    def connect(self):
        return self.learning.connect()

    def list_profiles(self):
        return [
            self._to_profile(self.learning.load(item.id))
            for item in self.learning.list_identities()
        ]

    def load(self, profile_id):
        return self._to_profile(self.learning.load(profile_id))

    def save(self, profile):
        self.learning.save(self._from_profile(profile))

    def create(self, display_name):
        name = display_name.strip()
        if not name:
            raise ValueError("Scientist display name cannot be blank.")
        profile = LocalProfile(uuid4().hex, name)
        self.save(profile)
        return profile

    def reset(self, profile_id):
        current = self.load(profile_id)
        profile = LocalProfile(
            current.id, current.display_name, favorite_simulation=current.favorite_simulation
        )
        self.save(profile)
        return profile

    def export_profile(self, profile_id):
        return self.learning.export_learner(profile_id)

    def import_profile(self, text):
        data = json.loads(text)
        if isinstance(data, dict) and data.get("export_schema_version") == 1:
            imported = self.learning.import_learner(text, new_id=uuid4().hex)
            return self._to_profile(imported)
        profile = LocalProfile.from_dict({**data, "id": uuid4().hex})
        self.save(profile)
        return profile

    @staticmethod
    def _from_profile(profile: LocalProfile) -> LearnerData:
        notebook = profile.trial_notebook if isinstance(profile.trial_notebook, Mapping) else {}
        return LearnerData(
            LearnerIdentity(profile.id, profile.display_name),
            dict(profile.accessibility_settings),
            tuple((key, dict(value)) for key, value in profile.educational_progress.items()),
            tuple(dict(item) for item in profile.assessment_attempts),
            tuple(dict(item) for item in notebook.get("trials", ()) if isinstance(item, Mapping)),
            tuple(
                dict(item)
                for item in notebook.get("lesson_reflections", ())
                if isinstance(item, Mapping)
            ),
            profile.badges_earned,
            {
                "last_used_simulation": profile.last_used_simulation,
                "last_used_parameters": profile.last_used_parameters,
                "favorite_simulation": profile.favorite_simulation,
                "total_experiment_count": profile.total_experiment_count,
                "learner_observations": profile.learner_observations,
                "application_version": profile.application_version,
                "pinned_run_a_id": notebook.get("pinned_run_a_id"),
                "next_trial_number": notebook.get("next_trial_number", 1),
            },
            tuple(dict(item) for item in profile.objective_evidence),
        )

    @staticmethod
    def _to_profile(data: LearnerData) -> LocalProfile:
        state = data.ui_state
        notebook = {
            "trials": list(data.experiment_trials),
            "lesson_reflections": list(data.notebook_entries),
            "pinned_run_a_id": state.get("pinned_run_a_id"),
            "next_trial_number": state.get("next_trial_number", len(data.experiment_trials) + 1),
        }
        last_parameters = state.get("last_used_parameters", {})
        return LocalProfile(
            id=data.identity.id,
            display_name=data.identity.display_name,
            badges_earned=data.achievements,
            trial_notebook=notebook,
            last_used_simulation=(
                str(state["last_used_simulation"]) if state.get("last_used_simulation") else None
            ),
            last_used_parameters=(
                dict(last_parameters) if isinstance(last_parameters, Mapping) else {}
            ),
            favorite_simulation=(
                str(state["favorite_simulation"]) if state.get("favorite_simulation") else None
            ),
            total_experiment_count=int(
                state.get("total_experiment_count", len(data.experiment_trials))
            ),
            learner_observations=tuple(str(item) for item in state.get("learner_observations", ())),
            application_version=str(state.get("application_version", APPLICATION_VERSION)),
            accessibility_settings=data.preferences,
            educational_progress=dict(data.lesson_progress),
            assessment_attempts=data.assessment_attempts,
            objective_evidence=data.objective_evidence,
        )
