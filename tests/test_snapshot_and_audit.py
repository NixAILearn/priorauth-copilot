"""Snapshots (D-068) and the reviewer tables in the audit log (D-070)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from priorauth import snapshot
from priorauth.audit import AuditLog
from priorauth.snapshot import SNAPSHOTS

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def oracle():
    return snapshot.load(SNAPSHOTS / "oracle.jsonl")


def test_committed_oracle_snapshot_matches_labels(oracle):
    assert oracle.header.backend == "oracle" and not oracle.header.scorecard
    assert "not model output" in oracle.header.label
    assert len(oracle.cases) == 60
    for cid, c in oracle.cases.items():
        label = json.loads((ROOT / "data" / "cases" / cid / "label.json").read_text())
        assert c.rec.route.value == label["expected_route"], cid


def test_committed_oracle_snapshot_is_current(tmp_path, oracle):
    """Rebuild it: the committed file must match what today's pipeline produces."""
    fresh = snapshot.load(snapshot.build_oracle(tmp_path / "o.jsonl"))
    for cid, c in fresh.cases.items():
        old = oracle.cases[cid].rec
        assert (c.rec.route, c.rec.findings, c.rec.flags, c.rec.missing) == (
            old.route,
            old.findings,
            old.flags,
            old.missing,
        ), f"{cid}: run `make snapshot-oracle`"


def test_export_round_trips_an_audit_log(tmp_path, oracle):
    db = tmp_path / "run-lmstudio.sqlite"
    log = AuditLog(db)
    for c in list(oracle.cases.values())[:3]:
        log.record(
            c.rec,
            policy_sha256=c.policy_sha256,
            prompt_version="p1",
            backend="lmstudio",
            official=True,
        )
    log.db.close()
    out = snapshot.export(db, tmp_path / "s.jsonl")
    s = snapshot.load(out)
    assert s.header.backend == "lmstudio" and s.header.scorecard
    assert len(s.cases) == 3


def test_default_snapshot_prefers_a_scorecard_run(tmp_path, oracle):
    import sys

    sys.path.insert(0, str(ROOT / "app"))
    from common import default_snapshot  # noqa: PLC0415

    o = snapshot.write(tmp_path / "oracle.jsonl", oracle.header, [])
    assert default_snapshot([o]) == o
    q_header = snapshot.SnapshotHeader(
        **{**oracle.header.__dict__, "backend": "lmstudio", "name": "qwen"}
    )
    q = snapshot.write(tmp_path / "qwen.jsonl", q_header, [])
    assert default_snapshot([o, q]) == q


def _run(log, oracle):
    c = oracle.cases["CASE-021-20"]
    return log.record(
        c.rec, policy_sha256=c.policy_sha256, prompt_version="p", backend="oracle", official=False
    )


def test_reviewer_actions_need_a_reason_and_have_no_deny(oracle):
    log = AuditLog()
    run = _run(log, oracle)
    with pytest.raises(ValueError):
        log.reviewer_action(run, "Priya", "deny", "x")
    with pytest.raises(ValueError):
        log.reviewer_action(run, "Priya", "approve", "  ")
    log.reviewer_action(run, "Priya", "refer_md", "injection in D03")
    assert [a["action"] for a in log.actions(run)] == ["refer_md"]


def test_overrides_are_logged_with_from_and_to(oracle):
    log = AuditLog()
    run = _run(log, oracle)
    log.finding_review(run, "Priya", "flag:0", None, "injection", "injection", "seen")
    log.finding_review(run, "Priya", "021-C4", None, "insufficient", "met", "DISE in D04")
    with pytest.raises(ValueError):
        log.finding_review(run, "Priya", "021-C4", None, "insufficient", "met", "")
    rows = log.finding_reviews(run)
    assert [r["kind"] for r in rows] == ["reviewed", "override"]
    assert (rows[1]["from_status"], rows[1]["to_status"]) == ("insufficient", "met")
    # Overrides never touch the stored recommendation.
    assert json.loads(log.runs()[0]["recommendation_json"])["route"] == "clinician_review"


def test_export_takes_the_commit_from_the_runs_report():
    db = Path("evals/runs/20261104T144821-all-lmstudio.sqlite")  # the v0.1 run's log name
    assert snapshot.run_commit(db) == "5423805"
    assert snapshot.run_commit(Path("nope.sqlite")) == "unknown"
