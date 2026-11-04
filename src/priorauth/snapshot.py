"""Snapshots: a committed set of recommendations the reviewer app shows (D-068).

A snapshot is JSONL. Line 1 is a header naming the backend and model that produced it; each
following line is one case: the policy source hash and the full `Recommendation`. Snapshots are
written from an eval run's audit log (`export`) or from the ground-truth replay (`oracle`), so
the hosted demo needs no model and no key.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from priorauth.intake import ROOT
from priorauth.schemas import Recommendation

SNAPSHOTS = ROOT / "app" / "snapshots"
CASES = ROOT / "data" / "cases"
SNAPSHOT_VERSION = "1"
SCORECARD_BACKENDS = ("anthropic", "lmstudio")  # D-057


@dataclass(frozen=True)
class SnapshotHeader:
    name: str
    backend: str
    model: str
    prompt_version: str
    commit: str
    created_at: str
    source: str

    @property
    def scorecard(self) -> bool:
        return self.backend in SCORECARD_BACKENDS

    @property
    def label(self) -> str:
        if self.backend == "oracle":
            return "Ground-truth replay (not model output)"
        return f"{self.model} on {self.backend}"


@dataclass(frozen=True)
class SnapshotCase:
    policy_sha256: str
    prompt_version: str
    rec: Recommendation


@dataclass(frozen=True)
class Snapshot:
    header: SnapshotHeader
    cases: dict[str, SnapshotCase]


def _commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def write(path: Path, header: SnapshotHeader, cases: list[SnapshotCase]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps({"snapshot_version": SNAPSHOT_VERSION, **header.__dict__})]
    for c in sorted(cases, key=lambda c: c.rec.case_id):
        lines.append(
            json.dumps(
                {
                    "policy_sha256": c.policy_sha256,
                    "prompt_version": c.prompt_version,
                    "recommendation": json.loads(c.rec.model_dump_json()),
                }
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def load(path: Path) -> Snapshot:
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not rows or rows[0].get("snapshot_version") != SNAPSHOT_VERSION:
        raise ValueError(f"{path.name}: not a version {SNAPSHOT_VERSION} snapshot")
    meta = dict(rows[0])
    meta.pop("snapshot_version")
    header = SnapshotHeader(**meta)
    cases: dict[str, SnapshotCase] = {}
    for row in rows[1:]:
        rec = Recommendation.model_validate(row["recommendation"])
        cases[rec.case_id] = SnapshotCase(row["policy_sha256"], row["prompt_version"], rec)
    return Snapshot(header, cases)


def available(directory: Path = SNAPSHOTS) -> list[Path]:
    return sorted(directory.glob("*.jsonl"), reverse=True)


def run_commit(db_path: Path, reports: Path = ROOT / "evals" / "reports") -> str:
    """The commit the run was made at, from its eval report (the log is named by start time)."""
    stamp = db_path.stem.split("-", 1)[0]  # e.g. 20261104T144821
    for rep in reports.glob("*.json"):
        try:
            d = json.loads(rep.read_text(encoding="utf-8"))
            started = datetime.fromisoformat(d["started"])
        except (ValueError, KeyError, OSError):
            continue
        if f"{started:%Y%m%dT%H%M%S}" == stamp:
            return str(d.get("commit", "unknown"))
    return "unknown"


def export(db_path: Path, out: Path | None = None, name: str | None = None) -> Path:
    """Write a snapshot from an eval run's audit log (evals/runs/*.sqlite). Latest run per case."""
    db = sqlite3.connect(str(db_path))
    db.row_factory = sqlite3.Row
    runs = list(db.execute("SELECT * FROM runs ORDER BY run_id"))
    if not runs:
        raise ValueError(f"{db_path}: no runs")
    latest = {r["case_id"]: r for r in runs}
    models = [
        m["model"]
        for m in db.execute("SELECT model FROM model_calls WHERE role = 'extract' AND ok = 1")
    ]
    backends = {r["backend"] for r in latest.values()}
    if len(backends) != 1:
        raise ValueError(f"{db_path}: runs from more than one backend {sorted(backends)}")
    backend = backends.pop()
    prompt_versions = sorted({r["prompt_version"] for r in latest.values()})
    stem = name or db_path.stem
    header = SnapshotHeader(
        name=stem,
        backend=backend,
        model=max(set(models), key=models.count) if models else "unknown",
        prompt_version=",".join(prompt_versions),
        commit=run_commit(db_path),
        created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        source=f"export of {db_path.name}",
    )
    cases = [
        SnapshotCase(
            r["policy_source_sha256"],
            r["prompt_version"],
            Recommendation.model_validate_json(r["recommendation_json"]),
        )
        for r in latest.values()
    ]
    return write(out or SNAPSHOTS / f"{stem}.jsonl", header, cases)


def build_oracle(out: Path | None = None) -> Path:
    """Replay the ground truth through the real pipeline for every committed case."""
    from evals.run_eval import oracle_factory, select_cases  # noqa: PLC0415  (repo-only helper)
    from priorauth.extractor import PROMPT_VERSION  # noqa: PLC0415
    from priorauth.intake import load_case  # noqa: PLC0415
    from priorauth.pipeline import review_case  # noqa: PLC0415

    make, _info = oracle_factory()
    cases = []
    for case_id in select_cases("all"):
        rec = review_case(CASES / case_id, make(case_id))
        sha = load_case(CASES / case_id).spec.source_sha256
        cases.append(SnapshotCase(sha, PROMPT_VERSION, rec))
    header = SnapshotHeader(
        name="oracle",
        backend="oracle",
        model="ground-truth replay",
        prompt_version=PROMPT_VERSION,
        commit=_commit(),
        created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        source="python -m priorauth snapshot oracle",
    )
    return write(out or SNAPSHOTS / "oracle.jsonl", header, cases)
