"""Shared state for the reviewer app: snapshot, demo clock, case loading, audit log."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime, time
from pathlib import Path

import streamlit as st

from priorauth import reviewdesk as rd
from priorauth import snapshot as snap
from priorauth.audit import AuditLog
from priorauth.intake import ROOT, CaseInput, load_case
from priorauth.schemas import Recommendation

CASES = ROOT / "data" / "cases"
# Reviewer actions for this demo, one SQLite per snapshot; git-ignored. Tests point it elsewhere.
STATE = Path(os.environ.get("PRIORAUTH_APP_STATE") or ROOT / "app" / ".state")

BANNER = (
    "**Synthetic data only.** Northwind Health Plan, its policies, codes and members are "
    "fictional. Not a medical device. The copilot recommends; a person makes every decision, "
    "and it never denies. Do not enter real patient data."
)


def banner() -> None:
    st.warning(BANNER, icon="🧪")


# --- Snapshot ----------------------------------------------------------------------------------


def default_snapshot(paths: list[Path]) -> Path:
    """Newest scorecard-backend snapshot (D-068: Nick chose the Qwen run), else the oracle."""
    for p in paths:
        try:
            if snap.load(p).header.scorecard:
                return p
        except ValueError:
            continue
    return paths[0]


@st.cache_resource(show_spinner="Loading snapshot…")
def load_snapshot(path: str) -> snap.Snapshot:
    return snap.load(Path(path))


@st.cache_resource(show_spinner=False)
def case_input(case_id: str) -> CaseInput:
    return load_case(CASES / case_id)


def audit(snapshot: snap.Snapshot) -> AuditLog:
    """The app's audit log for this snapshot, seeded with its recommendations once."""
    STATE.mkdir(parents=True, exist_ok=True)
    log = AuditLog(STATE / f"{snapshot.header.name}.sqlite")
    if not log.db.execute("SELECT 1 FROM runs LIMIT 1").fetchone():
        for c in snapshot.cases.values():
            log.record(
                c.rec,
                policy_sha256=c.policy_sha256,
                prompt_version=c.prompt_version,
                backend=snapshot.header.backend,
                official=snapshot.header.scorecard,
            )
    return log


@dataclass(frozen=True)
class CaseRun:
    run_id: int
    rec: Recommendation
    backend: str


def latest_runs(log: AuditLog) -> dict[str, CaseRun]:
    rows = log.db.execute(
        "SELECT run_id, case_id, backend, recommendation_json FROM runs ORDER BY run_id"
    ).fetchall()
    return {r[1]: CaseRun(int(r[0]), Recommendation.model_validate_json(r[3]), r[2]) for r in rows}


def case_status(log: AuditLog, run_id: int) -> str:
    if log.actions(run_id):
        return "Done"
    if log.finding_reviews(run_id):
        return "In review"
    return "New"


# --- Sidebar -----------------------------------------------------------------------------------


@dataclass(frozen=True)
class Ctx:
    snapshot: snap.Snapshot
    log: AuditLog
    runs: dict[str, CaseRun]
    clock: datetime
    reviewer: str

    def arrivals(self) -> dict[str, datetime]:
        received = {cid: case_input(cid).request.received_at for cid in self.runs}
        return rd.rebased_arrivals(received, self.clock)


def live_backend() -> str | None:
    """A backend the app may call for a live re-run, or None (the hosted demo, D-068)."""
    backend = os.environ.get("PRIORAUTH_BACKEND", "").strip().lower()
    if not backend or backend in ("fake",):
        return None
    if backend == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    return backend


def sidebar() -> Ctx:
    paths = snap.available()
    if not paths:
        st.error("No snapshot in app/snapshots/. Run `python -m priorauth snapshot oracle`.")
        st.stop()
    names = [p.name for p in paths]
    if "snapshot" not in st.session_state:
        st.session_state.snapshot = default_snapshot(paths).name
    with st.sidebar:
        choice = st.selectbox(
            "Results shown",
            names,
            key="snapshot",
            format_func=lambda n: load_snapshot(str(paths[names.index(n)])).header.label,
        )
        snapshot = load_snapshot(str(paths[names.index(choice)]))
        h = snapshot.header
        st.caption(
            f"Snapshot `{h.name}` · prompt {h.prompt_version} · commit {h.commit}"
            + ("" if h.scorecard else " · not a scorecard result")
        )
        if h.backend == "oracle":
            st.info(
                "Ground-truth replay: the labels run through the real pipeline. Not model output."
            )
        now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
        if "clock_date" not in st.session_state:
            st.session_state.clock_date = now.date()
            st.session_state.clock_time = now.time()
        st.markdown("**Demo clock** (UTC)")
        d = st.date_input("Date", key="clock_date", label_visibility="collapsed")
        t = st.time_input("Time", key="clock_time", label_visibility="collapsed", step=3600)
        st.caption("Arrival times are rebased to this clock for the SLA view only (D-069).")
        reviewer = st.text_input("Reviewer", value="Priya N., RN", key="reviewer")
    clock = datetime.combine(d, t if isinstance(t, time) else now.time(), tzinfo=UTC)
    log = audit(snapshot)
    return Ctx(snapshot, log, latest_runs(log), clock, reviewer.strip() or "Reviewer")


def open_case(case_id: str) -> None:
    st.session_state.case_id = case_id
    st.switch_page("views/case.py")
