# Learning persistence and hosted-backend seam

## Current design

`SQLiteLearningStore` is the authoritative local persistence service. Streamlit session state is
an active-learner UI cache: it is hydrated from the store when a learner is selected and flushed
transactionally through the application callback boundary. A browser rerun or lost session can be
reconstructed from persisted records.

The storage domains are separate:

| Domain | SQLite representation | Growth pattern |
| --- | --- | --- |
| Learner identity | one `learners` row | low |
| Preferences | one versioned `preferences` row | low |
| Lesson progress | one versioned row per learner and lesson | medium |
| Assessment attempts | one versioned row per attempt | high |
| Experiment trials | one versioned row per trial | high |
| Notebook entries | one versioned row per entry | high |
| Achievements | one row per earned achievement | medium |
| Objective evidence | one versioned row per evidence record | high |

Each repository has a backend-neutral `Protocol` in `learning_store.py`. The SQLite implementation
provides targeted transactional writes as well as an atomic `LearnerData` snapshot operation used
by the current Streamlit compatibility adapter.

`LocalProfile` and `ProfileStore` remain supported compatibility projections for the current UI,
legacy JSON imports, and existing callers. They are not the platform domain or database shape.
Profile schema versions 1–3 migrate to normalized store schema 4 without deleting the legacy
profile table. New writes target normalized tables.

## Integrity, recovery, and interchange

SQLite connections enable foreign keys, WAL journaling, a 30-second busy timeout, and explicit
`BEGIN IMMEDIATE` transactions. Snapshot replacement either commits every domain or rolls back.
Attempt and trial IDs provide idempotent upserts for event-oriented writes.

Records are independently serialized. A malformed attempt, trial, notebook entry, or evidence row
is skipped and copied to `rejected_records`; valid identity and other learning data remain usable.
This prevents one corrupt child record from making an entire learner profile unreadable.

Export format version 1 contains identity plus each domain as a separate collection. Import assigns
a new local learner ID, validates the outer schema, retains valid child records, and drops malformed
children. Legacy monolithic profile JSON remains importable through the compatibility facade.

## Hosted-backend seam

A hosted implementation should satisfy the repository protocols rather than reproduce
`LocalProfile` or SQLite tables. Likely mappings are an identity service plus progress, attempt,
trial, notebook, achievement, evidence, and preference repositories backed by a transactional SQL
database. Authentication, tenancy, authorization, cloud deployment, synchronization, and conflict
resolution are deliberately outside this change.

The hosted boundary must preserve:

- stable learner and record IDs;
- record and export schema versions;
- idempotent record writes;
- atomic multi-domain operations when a user action spans domains;
- ordered attempt/trial history;
- quarantine or per-record errors instead of whole-learner failure;
- the same export/import semantics.

Before replacing SQLite in any environment, contract tests should run unchanged against the hosted
adapter. Streamlit should receive the repository service through its application boundary; session
state must remain a cache and never become the only copy of a completed attempt, trial, notebook
entry, achievement, preference change, or lesson-progress event.
