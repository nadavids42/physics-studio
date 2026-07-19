"""Backend-neutral learning repositories and a single-learner local SQLite implementation.

Each domain (attempts, trials, notebook entries, evidence, ...) is a table keyed by
learner and record ID, storing the record as a JSON payload blob plus a small number
of columns promoted for filtering. This is local, single-learner storage with schema
versioning, not a normalized relational schema, and it makes no claim about
multi-learner or classroom-scale query performance.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from physics_playground.serialization import dumps

STORE_SCHEMA_VERSION = 5
EXPORT_SCHEMA_VERSION = 1
Record = Mapping[str, object]


@dataclass(frozen=True, slots=True)
class LearnerIdentity:
    id: str
    display_name: str
    schema_version: int = 1


@dataclass(frozen=True, slots=True)
class LearnerData:
    identity: LearnerIdentity
    preferences: Record = field(default_factory=dict)
    lesson_progress: tuple[tuple[str, Record], ...] = ()
    assessment_attempts: tuple[Record, ...] = ()
    experiment_trials: tuple[Record, ...] = ()
    notebook_entries: tuple[Record, ...] = ()
    achievements: tuple[str, ...] = ()
    ui_state: Record = field(default_factory=dict)
    objective_evidence: tuple[Record, ...] = ()
    schema_version: int = 1


class LearnerIdentityRepository(Protocol):
    def list_identities(self) -> tuple[LearnerIdentity, ...]: ...
    def get_identity(self, learner_id: str) -> LearnerIdentity: ...
    def save_identity(self, identity: LearnerIdentity) -> None: ...


class LessonProgressRepository(Protocol):
    def get_lesson_progress(self, learner_id: str) -> tuple[tuple[str, Record], ...]: ...
    def put_lesson_progress(self, learner_id: str, lesson_id: str, progress: Record) -> None: ...


class AssessmentAttemptRepository(Protocol):
    def get_assessment_attempts(self, learner_id: str) -> tuple[Record, ...]: ...
    def append_assessment_attempt(self, learner_id: str, attempt: Record) -> None: ...


class ExperimentTrialRepository(Protocol):
    def get_experiment_trials(self, learner_id: str) -> tuple[Record, ...]: ...
    def append_experiment_trial(self, learner_id: str, trial: Record) -> None: ...


class NotebookEntryRepository(Protocol):
    def get_notebook_entries(self, learner_id: str) -> tuple[Record, ...]: ...
    def put_notebook_entry(self, learner_id: str, entry: Record) -> None: ...


class AchievementRepository(Protocol):
    def get_achievements(self, learner_id: str) -> tuple[str, ...]: ...
    def add_achievement(self, learner_id: str, achievement_id: str) -> None: ...


class PreferenceRepository(Protocol):
    def get_preferences(self, learner_id: str) -> Record: ...
    def put_preferences(self, learner_id: str, preferences: Record) -> None: ...


class SQLiteLearningStore:
    """Transactional local SQLite store for one learner's JSON-payload records at a time."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=30)
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=30000")
        db.execute("PRAGMA journal_mode=WAL")
        return db

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        db = self.connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _initialize(self) -> None:
        with self.transaction() as db:
            version = int(db.execute("PRAGMA user_version").fetchone()[0])
            if version > STORE_SCHEMA_VERSION:
                raise RuntimeError(
                    f"Learning database schema {version} is newer than supported schema {STORE_SCHEMA_VERSION}."
                )
            self._ensure_legacy_profile_table(db, version)
            self._create_tables(db)
            self._ensure_assessment_attempt_columns(db)
            if version < STORE_SCHEMA_VERSION:
                self._migrate_legacy_profiles(db)
                self._backfill_assessment_attempt_columns(db)
                db.execute(f"PRAGMA user_version={STORE_SCHEMA_VERSION}")

    @staticmethod
    def _ensure_legacy_profile_table(db: sqlite3.Connection, version: int) -> None:
        db.execute(
            "CREATE TABLE IF NOT EXISTS profiles (id TEXT PRIMARY KEY, display_name TEXT NOT NULL, payload TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT '')"
        )
        if version == 1:
            columns = {row[1] for row in db.execute("PRAGMA table_info(profiles)")}
            if "updated_at" not in columns:
                db.execute("ALTER TABLE profiles ADD COLUMN updated_at TEXT NOT NULL DEFAULT ''")

    @staticmethod
    def _create_tables(db: sqlite3.Connection) -> None:
        statements = (
            "CREATE TABLE IF NOT EXISTS learners (id TEXT PRIMARY KEY, display_name TEXT NOT NULL, schema_version INTEGER NOT NULL)",
            "CREATE TABLE IF NOT EXISTS preferences (learner_id TEXT PRIMARY KEY REFERENCES learners(id) ON DELETE CASCADE, payload TEXT NOT NULL, schema_version INTEGER NOT NULL)",
            "CREATE TABLE IF NOT EXISTS lesson_progress (learner_id TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE, lesson_id TEXT NOT NULL, payload TEXT NOT NULL, schema_version INTEGER NOT NULL, PRIMARY KEY(learner_id,lesson_id))",
            "CREATE TABLE IF NOT EXISTS assessment_attempts (learner_id TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE, record_id TEXT NOT NULL, payload TEXT NOT NULL, schema_version INTEGER NOT NULL, lesson_id TEXT NOT NULL DEFAULT '', submitted_at TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT '', PRIMARY KEY(learner_id,record_id))",
            "CREATE TABLE IF NOT EXISTS experiment_trials (learner_id TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE, record_id TEXT NOT NULL, payload TEXT NOT NULL, schema_version INTEGER NOT NULL, PRIMARY KEY(learner_id,record_id))",
            "CREATE TABLE IF NOT EXISTS notebook_entries (learner_id TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE, record_id TEXT NOT NULL, payload TEXT NOT NULL, schema_version INTEGER NOT NULL, PRIMARY KEY(learner_id,record_id))",
            "CREATE TABLE IF NOT EXISTS achievements (learner_id TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE, achievement_id TEXT NOT NULL, schema_version INTEGER NOT NULL, PRIMARY KEY(learner_id,achievement_id))",
            "CREATE TABLE IF NOT EXISTS learner_state (learner_id TEXT PRIMARY KEY REFERENCES learners(id) ON DELETE CASCADE, payload TEXT NOT NULL, schema_version INTEGER NOT NULL)",
            "CREATE TABLE IF NOT EXISTS objective_evidence (learner_id TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE, record_id TEXT NOT NULL, payload TEXT NOT NULL, schema_version INTEGER NOT NULL, PRIMARY KEY(learner_id,record_id))",
            "CREATE TABLE IF NOT EXISTS rejected_records (id INTEGER PRIMARY KEY AUTOINCREMENT, learner_id TEXT, domain TEXT NOT NULL, raw_payload TEXT NOT NULL, reason TEXT NOT NULL)",
        )
        for statement in statements:
            db.execute(statement)

    @staticmethod
    def _ensure_assessment_attempt_columns(db: sqlite3.Connection) -> None:
        """Add the columns promoted from the payload for existing databases.

        ``CREATE TABLE IF NOT EXISTS`` above leaves an already-created table untouched,
        so a database created before schema 5 needs these columns added explicitly.
        """

        columns = {row[1] for row in db.execute("PRAGMA table_info(assessment_attempts)")}
        for column in ("lesson_id", "submitted_at", "status"):
            if column not in columns:
                db.execute(
                    f"ALTER TABLE assessment_attempts ADD COLUMN {column} TEXT NOT NULL DEFAULT ''"
                )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_assessment_attempts_lesson_id "
            "ON assessment_attempts(learner_id, lesson_id)"
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_assessment_attempts_submitted_at "
            "ON assessment_attempts(submitted_at)"
        )

    @staticmethod
    def _backfill_assessment_attempt_columns(db: sqlite3.Connection) -> None:
        """Populate the promoted columns for rows written before schema 5."""

        rows = db.execute(
            "SELECT learner_id, record_id, payload FROM assessment_attempts "
            "WHERE lesson_id='' AND submitted_at='' AND status=''"
        ).fetchall()
        for learner_id, record_id, raw in rows:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, dict):
                continue
            lesson_id, submitted_at, status = SQLiteLearningStore._assessment_attempt_columns(
                payload
            )
            db.execute(
                "UPDATE assessment_attempts SET lesson_id=?, submitted_at=?, status=? "
                "WHERE learner_id=? AND record_id=?",
                (lesson_id, submitted_at, status, learner_id, record_id),
            )

    @staticmethod
    def _assessment_attempt_columns(value: Record) -> tuple[str, str, str]:
        lesson_id = value.get("lesson_id")
        submitted_at = value.get("submitted_at")
        status = value.get("status")
        return (
            lesson_id if isinstance(lesson_id, str) else "",
            submitted_at if isinstance(submitted_at, str) else "",
            status if isinstance(status, str) else "",
        )

    def _migrate_legacy_profiles(self, db: sqlite3.Connection) -> None:
        for profile_id, display_name, raw in db.execute(
            "SELECT id,display_name,payload FROM profiles"
        ).fetchall():
            try:
                payload = json.loads(raw)
                if not isinstance(payload, dict):
                    raise ValueError("profile payload is not an object")
            except (json.JSONDecodeError, ValueError) as error:
                self._reject(db, str(profile_id), "profile", str(raw), str(error))
                payload = {}
            data = self._legacy_data(str(profile_id), str(display_name), payload, db)
            self._write(db, data)

    def _legacy_data(
        self,
        learner_id: str,
        display_name: str,
        payload: Mapping[str, object],
        db: sqlite3.Connection,
    ) -> LearnerData:
        notebook = payload.get("trial_notebook", {})
        notebook = notebook if isinstance(notebook, Mapping) else {}
        progress = payload.get("educational_progress", {})
        progress_items = (
            tuple(
                (str(key), value) for key, value in progress.items() if isinstance(value, Mapping)
            )
            if isinstance(progress, Mapping)
            else ()
        )
        attempts = self._valid_records(
            db, learner_id, "assessment_attempt", payload.get("assessment_attempts", ())
        )
        trials = self._valid_records(db, learner_id, "experiment_trial", notebook.get("trials", ()))
        entries = self._valid_records(
            db, learner_id, "notebook_entry", notebook.get("lesson_reflections", ())
        )
        evidence = self._valid_records(
            db, learner_id, "objective_evidence", payload.get("objective_evidence", ())
        )
        preferences = payload.get("accessibility_settings", {})
        badges = payload.get("badges_earned", ())
        badges_earned = (
            tuple(str(item) for item in badges if isinstance(item, str))
            if isinstance(badges, (list, tuple))
            else ()
        )
        return LearnerData(
            LearnerIdentity(learner_id, display_name),
            dict(preferences) if isinstance(preferences, Mapping) else {},
            progress_items,
            attempts,
            trials,
            entries,
            badges_earned,
            {
                key: value
                for key, value in payload.items()
                if key
                not in {
                    "id",
                    "display_name",
                    "accessibility_settings",
                    "educational_progress",
                    "assessment_attempts",
                    "objective_evidence",
                    "badges_earned",
                    "trial_notebook",
                }
            }
            | {
                "pinned_run_a_id": notebook.get("pinned_run_a_id"),
                "next_trial_number": notebook.get("next_trial_number", len(trials) + 1),
            },
            evidence,
        )

    def _valid_records(
        self, db: sqlite3.Connection, learner_id: str, domain: str, values: object
    ) -> tuple[Record, ...]:
        if not isinstance(values, Iterable) or isinstance(values, str | bytes | Mapping):
            self._reject(db, learner_id, domain, repr(values), "record collection is not an array")
            return ()
        records = []
        for value in values:
            if isinstance(value, Mapping) and isinstance(value.get("id"), str):
                records.append(dict(value))
            else:
                self._reject(db, learner_id, domain, repr(value), "record requires a string id")
        return tuple(records)

    @staticmethod
    def _reject(
        db: sqlite3.Connection, learner_id: str, domain: str, raw: str, reason: str
    ) -> None:
        db.execute(
            "INSERT INTO rejected_records(learner_id,domain,raw_payload,reason) VALUES(?,?,?,?)",
            (learner_id, domain, raw, reason),
        )

    def save(self, data: LearnerData) -> None:
        with self.transaction() as db:
            self._write(db, data)

    def _write(self, db: sqlite3.Connection, data: LearnerData) -> None:
        learner_id = data.identity.id
        if not learner_id or not data.identity.display_name.strip():
            raise ValueError("Learner identity requires an ID and display name.")
        db.execute(
            "INSERT INTO learners VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET display_name=excluded.display_name,schema_version=excluded.schema_version",
            (learner_id, data.identity.display_name.strip(), data.identity.schema_version),
        )
        self._replace_single(db, "preferences", learner_id, data.preferences)
        self._replace_single(db, "learner_state", learner_id, data.ui_state)
        self._replace_keyed(db, "lesson_progress", learner_id, data.lesson_progress)
        self._replace_assessment_attempts(db, learner_id, data.assessment_attempts)
        self._replace_records(db, "experiment_trials", learner_id, data.experiment_trials)
        self._replace_records(db, "notebook_entries", learner_id, data.notebook_entries)
        self._replace_records(db, "objective_evidence", learner_id, data.objective_evidence)
        db.execute("DELETE FROM achievements WHERE learner_id=?", (learner_id,))
        db.executemany(
            "INSERT INTO achievements VALUES(?,?,1)",
            ((learner_id, item) for item in dict.fromkeys(data.achievements)),
        )

    @staticmethod
    def _replace_single(
        db: sqlite3.Connection, table: str, learner_id: str, payload: Record
    ) -> None:
        db.execute(
            f"INSERT INTO {table} VALUES(?,?,1) ON CONFLICT(learner_id) DO UPDATE SET payload=excluded.payload,schema_version=1",
            (learner_id, dumps(payload)),
        )

    @staticmethod
    def _replace_keyed(
        db: sqlite3.Connection,
        table: str,
        learner_id: str,
        values: tuple[tuple[str, Record], ...],
    ) -> None:
        db.execute(f"DELETE FROM {table} WHERE learner_id=?", (learner_id,))
        db.executemany(
            f"INSERT INTO {table} VALUES(?,?,?,?,?)".replace("?,?,?,?,?", "?,?,?,1"),
            ((learner_id, key, dumps(value)) for key, value in values),
        )

    @staticmethod
    def _replace_records(
        db: sqlite3.Connection, table: str, learner_id: str, values: tuple[Record, ...]
    ) -> None:
        db.execute(f"DELETE FROM {table} WHERE learner_id=?", (learner_id,))
        rows = []
        for value in values:
            record_id = value.get("id")
            if not isinstance(record_id, str) or not record_id:
                raise ValueError(f"{table} records require a string id.")
            rows.append((learner_id, record_id, dumps(value)))
        db.executemany(f"INSERT INTO {table} VALUES(?,?,?,1)", rows)

    @classmethod
    def _replace_assessment_attempts(
        cls, db: sqlite3.Connection, learner_id: str, values: tuple[Record, ...]
    ) -> None:
        db.execute("DELETE FROM assessment_attempts WHERE learner_id=?", (learner_id,))
        rows = []
        for value in values:
            record_id = value.get("id")
            if not isinstance(record_id, str) or not record_id:
                raise ValueError("assessment_attempts records require a string id.")
            lesson_id, submitted_at, status = cls._assessment_attempt_columns(value)
            rows.append((learner_id, record_id, dumps(value), lesson_id, submitted_at, status))
        db.executemany(
            "INSERT INTO assessment_attempts"
            "(learner_id,record_id,payload,schema_version,lesson_id,submitted_at,status) "
            "VALUES(?,?,?,1,?,?,?)",
            rows,
        )

    def list_identities(self) -> tuple[LearnerIdentity, ...]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT id,display_name,schema_version FROM learners ORDER BY lower(display_name)"
            ).fetchall()
        return tuple(LearnerIdentity(str(row[0]), str(row[1]), int(row[2])) for row in rows)

    def get_identity(self, learner_id: str) -> LearnerIdentity:
        with self.connect() as db:
            row = db.execute(
                "SELECT id,display_name,schema_version FROM learners WHERE id=?", (learner_id,)
            ).fetchone()
        if row is None:
            raise KeyError(learner_id)
        return LearnerIdentity(str(row[0]), str(row[1]), int(row[2]))

    def save_identity(self, identity: LearnerIdentity) -> None:
        if not identity.id or not identity.display_name.strip():
            raise ValueError("Learner identity requires an ID and display name.")
        with self.transaction() as db:
            db.execute(
                "INSERT INTO learners VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET display_name=excluded.display_name,schema_version=excluded.schema_version",
                (identity.id, identity.display_name.strip(), identity.schema_version),
            )

    def _load_json_rows(self, table: str, learner_id: str) -> tuple[Record, ...]:
        with self.transaction() as db:
            rows = db.execute(
                f"SELECT payload FROM {table} WHERE learner_id=? ORDER BY rowid", (learner_id,)
            ).fetchall()
            valid = []
            for (raw,) in rows:
                try:
                    value = json.loads(raw)
                    if not isinstance(value, dict):
                        raise ValueError("record is not an object")
                    valid.append(value)
                except (json.JSONDecodeError, ValueError) as error:
                    self._reject(db, learner_id, table, str(raw), str(error))
            return tuple(valid)

    def get_preferences(self, learner_id: str) -> Record:
        rows = self._load_json_rows("preferences", learner_id)
        return rows[0] if rows else {}

    def put_preferences(self, learner_id: str, preferences: Record) -> None:
        with self.transaction() as db:
            self._replace_single(db, "preferences", learner_id, preferences)

    def get_lesson_progress(self, learner_id: str) -> tuple[tuple[str, Record], ...]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT lesson_id,payload FROM lesson_progress WHERE learner_id=? ORDER BY lesson_id",
                (learner_id,),
            ).fetchall()
        valid = []
        for lesson_id, raw in rows:
            try:
                value = json.loads(raw)
                if isinstance(value, dict):
                    valid.append((str(lesson_id), value))
            except json.JSONDecodeError:
                continue
        return tuple(valid)

    def put_lesson_progress(self, learner_id: str, lesson_id: str, progress: Record) -> None:
        if not lesson_id.strip():
            raise ValueError("Lesson progress requires a lesson ID.")
        with self.transaction() as db:
            db.execute(
                "INSERT INTO lesson_progress VALUES(?,?,?,1) ON CONFLICT(learner_id,lesson_id) DO UPDATE SET payload=excluded.payload,schema_version=1",
                (learner_id, lesson_id, dumps(progress)),
            )

    def get_assessment_attempts(self, learner_id: str) -> tuple[Record, ...]:
        return self._load_json_rows("assessment_attempts", learner_id)

    def append_assessment_attempt(self, learner_id: str, attempt: Record) -> None:
        record_id = attempt.get("id")
        if not isinstance(record_id, str) or not record_id:
            raise ValueError("assessment_attempts records require a string id.")
        lesson_id, submitted_at, status = self._assessment_attempt_columns(attempt)
        with self.transaction() as db:
            db.execute(
                "INSERT INTO assessment_attempts"
                "(learner_id,record_id,payload,schema_version,lesson_id,submitted_at,status) "
                "VALUES(?,?,?,1,?,?,?) "
                "ON CONFLICT(learner_id,record_id) DO UPDATE SET "
                "payload=excluded.payload,schema_version=1,lesson_id=excluded.lesson_id,"
                "submitted_at=excluded.submitted_at,status=excluded.status",
                (learner_id, record_id, dumps(attempt), lesson_id, submitted_at, status),
            )

    def get_experiment_trials(self, learner_id: str) -> tuple[Record, ...]:
        return self._load_json_rows("experiment_trials", learner_id)

    def append_experiment_trial(self, learner_id: str, trial: Record) -> None:
        self._append_record("experiment_trials", learner_id, trial)

    def get_notebook_entries(self, learner_id: str) -> tuple[Record, ...]:
        return self._load_json_rows("notebook_entries", learner_id)

    def put_notebook_entry(self, learner_id: str, entry: Record) -> None:
        self._append_record("notebook_entries", learner_id, entry)

    def _append_record(self, table: str, learner_id: str, record: Record) -> None:
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            raise ValueError(f"{table} records require a string id.")
        with self.transaction() as db:
            db.execute(
                f"INSERT INTO {table} VALUES(?,?,?,1) ON CONFLICT(learner_id,record_id) DO UPDATE SET payload=excluded.payload,schema_version=1",
                (learner_id, record_id, dumps(record)),
            )

    def get_achievements(self, learner_id: str) -> tuple[str, ...]:
        with self.connect() as db:
            return tuple(
                str(row[0])
                for row in db.execute(
                    "SELECT achievement_id FROM achievements WHERE learner_id=? ORDER BY achievement_id",
                    (learner_id,),
                )
            )

    def add_achievement(self, learner_id: str, achievement_id: str) -> None:
        if not achievement_id.strip():
            raise ValueError("Achievement ID cannot be blank.")
        with self.transaction() as db:
            db.execute(
                "INSERT OR IGNORE INTO achievements VALUES(?,?,1)",
                (learner_id, achievement_id),
            )

    def load(self, learner_id: str) -> LearnerData:
        state_rows = self._load_json_rows("learner_state", learner_id)
        return LearnerData(
            self.get_identity(learner_id),
            self.get_preferences(learner_id),
            self.get_lesson_progress(learner_id),
            self.get_assessment_attempts(learner_id),
            self.get_experiment_trials(learner_id),
            self.get_notebook_entries(learner_id),
            self.get_achievements(learner_id),
            state_rows[0] if state_rows else {},
            self._load_json_rows("objective_evidence", learner_id),
        )

    def delete_learning_data(self, learner_id: str) -> None:
        identity = self.get_identity(learner_id)
        self.save(LearnerData(identity))

    def export_learner(self, learner_id: str) -> str:
        data = self.load(learner_id)
        return dumps(
            {
                "export_schema_version": EXPORT_SCHEMA_VERSION,
                "learner": {
                    "identity": {
                        "id": data.identity.id,
                        "display_name": data.identity.display_name,
                        "schema_version": data.identity.schema_version,
                    },
                    "preferences": data.preferences,
                    "lesson_progress": dict(data.lesson_progress),
                    "assessment_attempts": data.assessment_attempts,
                    "experiment_trials": data.experiment_trials,
                    "notebook_entries": data.notebook_entries,
                    "achievements": data.achievements,
                    "ui_state": data.ui_state,
                    "objective_evidence": data.objective_evidence,
                },
            },
            indent=2,
        )

    def import_learner(self, text: str, *, new_id: str) -> LearnerData:
        value = json.loads(text)
        if not isinstance(value, dict) or value.get("export_schema_version") != 1:
            raise ValueError("Unsupported learner export schema.")
        learner = value.get("learner")
        if not isinstance(learner, dict) or not isinstance(learner.get("identity"), dict):
            raise ValueError("Learner export requires identity data.")
        identity = learner["identity"]

        def records(name: str) -> tuple[Record, ...]:
            raw = learner.get(name, ())
            if not isinstance(raw, list):
                return ()
            return tuple(
                dict(item)
                for item in raw
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            )

        data = LearnerData(
            LearnerIdentity(new_id, str(identity.get("display_name") or "Scientist")),
            dict(learner.get("preferences", {})),
            tuple(
                (str(key), dict(item))
                for key, item in learner.get("lesson_progress", {}).items()
                if isinstance(item, dict)
            ),
            records("assessment_attempts"),
            records("experiment_trials"),
            records("notebook_entries"),
            tuple(str(item) for item in learner.get("achievements", ()) if isinstance(item, str)),
            dict(learner.get("ui_state", {})),
            records("objective_evidence"),
        )
        self.save(data)
        return data
