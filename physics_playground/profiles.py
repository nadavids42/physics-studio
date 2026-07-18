"""SQLite-backed local learner profiles with schema migration and JSON export."""

from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from physics_playground.serialization import dumps
from physics_playground.version import APPLICATION_VERSION

SCHEMA_VERSION = 2


class PersistenceUnavailable(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class LocalProfile:
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
    accessibility_settings: Mapping[str, bool] = field(default_factory=dict)

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
            self._initialize()
        except (OSError, sqlite3.Error) as error:
            raise PersistenceUnavailable(str(error)) from error

    def connect(self):
        return sqlite3.connect(self.path)

    def _initialize(self):
        with self.connect() as db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version == 0:
                db.execute(
                    "CREATE TABLE IF NOT EXISTS profiles (id TEXT PRIMARY KEY, display_name TEXT NOT NULL, payload TEXT NOT NULL, updated_at TEXT NOT NULL)"
                )
                db.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
            elif version < SCHEMA_VERSION:
                self._migrate(db, version)
            elif version > SCHEMA_VERSION:
                raise PersistenceUnavailable(
                    f"Profile database schema {version} is newer than supported schema {SCHEMA_VERSION}."
                )

    def _migrate(self, db, version):
        if version == 1:
            columns = {row[1] for row in db.execute("PRAGMA table_info(profiles)")}
            if "updated_at" not in columns:
                db.execute("ALTER TABLE profiles ADD COLUMN updated_at TEXT NOT NULL DEFAULT ''")
            db.execute("PRAGMA user_version=2")
            version = 2
        if version != SCHEMA_VERSION:
            raise PersistenceUnavailable(f"No migration path from schema {version}.")

    def list_profiles(self):
        with self.connect() as db:
            rows = db.execute(
                "SELECT payload FROM profiles ORDER BY lower(display_name)"
            ).fetchall()
        return [LocalProfile.from_dict(json.loads(row[0])) for row in rows]

    def load(self, profile_id):
        with self.connect() as db:
            row = db.execute("SELECT payload FROM profiles WHERE id=?", (profile_id,)).fetchone()
        if not row:
            raise KeyError(profile_id)
        return LocalProfile.from_dict(json.loads(row[0]))

    def save(self, profile):
        payload = dumps(profile)
        now = datetime.now(UTC).isoformat()
        with self.connect() as db:
            db.execute(
                "INSERT INTO profiles(id,display_name,payload,updated_at) VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET display_name=excluded.display_name,payload=excluded.payload,updated_at=excluded.updated_at",
                (profile.id, profile.display_name, payload, now),
            )

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
        return dumps(self.load(profile_id), indent=2)

    def import_profile(self, text):
        data = json.loads(text)
        profile = LocalProfile.from_dict({**data, "id": uuid4().hex})
        self.save(profile)
        return profile
