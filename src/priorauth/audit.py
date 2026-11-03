"""Audit log in SQLite: every run, model call, finding, flag and reviewer action.

Append-only by convention: rows are inserted, never updated. The eval harness (week 4) reads
runs and model calls from here for cost and time per case; the UI will write reviewer
decisions and overrides (an override needs a reason, kickoff section 8).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from priorauth.schemas import Recommendation

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    policy_id TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    policy_source_sha256 TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    backend TEXT NOT NULL,
    official INTEGER NOT NULL,
    route TEXT NOT NULL CHECK (route IN ('approve_ready', 'request_info', 'clinician_review')),
    recommendation_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS model_calls (
    run_id INTEGER NOT NULL REFERENCES runs(run_id),
    backend TEXT NOT NULL,
    model TEXT NOT NULL,
    role TEXT NOT NULL,
    attempt INTEGER NOT NULL,
    ok INTEGER NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cache_read_tokens INTEGER,
    latency_s REAL NOT NULL,
    error TEXT
);
CREATE TABLE IF NOT EXISTS findings (
    run_id INTEGER NOT NULL REFERENCES runs(run_id),
    node_id TEXT NOT NULL,
    unit_id TEXT,
    status TEXT NOT NULL,
    source TEXT NOT NULL,
    citations_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS flags (
    run_id INTEGER NOT NULL REFERENCES runs(run_id),
    kind TEXT NOT NULL,
    route TEXT NOT NULL,
    rule_id TEXT,
    unit_id TEXT,
    detail TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reviewer_actions (
    run_id INTEGER NOT NULL REFERENCES runs(run_id),
    reviewer TEXT NOT NULL,
    action TEXT NOT NULL,
    node_id TEXT,
    reason TEXT NOT NULL CHECK (length(trim(reason)) > 0),
    created_at TEXT NOT NULL
);
"""


class AuditLog:
    def __init__(self, path: str | Path = ":memory:"):
        self.db = sqlite3.connect(str(path))
        self.db.executescript(SCHEMA)

    def record(
        self,
        rec: Recommendation,
        *,
        policy_sha256: str,
        prompt_version: str,
        backend: str,
        official: bool,
    ) -> int:
        with self.db:
            cur = self.db.execute(
                "INSERT INTO runs (case_id, request_id, policy_id, policy_version,"
                " policy_source_sha256, prompt_version, backend, official, route,"
                " recommendation_json, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    rec.case_id,
                    rec.request_id,
                    rec.policy_id,
                    rec.policy_version,
                    policy_sha256,
                    prompt_version,
                    backend,
                    int(official),
                    rec.route.value,
                    rec.model_dump_json(),
                    rec.created_at.isoformat(),
                ),
            )
            run_id = int(cur.lastrowid or 0)
            self.db.executemany(
                "INSERT INTO model_calls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        run_id,
                        c.backend,
                        c.model,
                        c.role,
                        c.attempt,
                        int(c.ok),
                        c.input_tokens,
                        c.output_tokens,
                        c.cache_read_tokens,
                        c.latency_s,
                        c.error,
                    )
                    for c in rec.model_calls
                ],
            )
            self.db.executemany(
                "INSERT INTO findings VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        run_id,
                        f.node_id,
                        f.unit_id,
                        f.status,
                        f.source,
                        json.dumps([c.model_dump() for c in f.citations]),
                    )
                    for f in rec.findings
                ],
            )
            self.db.executemany(
                "INSERT INTO flags VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (run_id, f.kind, f.route.value, f.rule_id, f.unit_id, f.detail)
                    for f in rec.flags
                ],
            )
        return run_id

    def reviewer_action(
        self, run_id: int, reviewer: str, action: str, reason: str, node_id: str | None = None
    ) -> None:
        """A person's decision or override. The reason is required (kickoff section 8)."""
        with self.db:
            self.db.execute(
                "INSERT INTO reviewer_actions VALUES (?, ?, ?, ?, ?, ?)",
                (run_id, reviewer, action, node_id, reason, datetime.now(UTC).isoformat()),
            )

    def runs(self) -> list[sqlite3.Row]:
        self.db.row_factory = sqlite3.Row
        return list(self.db.execute("SELECT * FROM runs ORDER BY run_id"))
