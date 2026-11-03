"""Eval runner: run labeled cases through the pipeline and score them against docs/metrics.md.

    make eval                    # scorecard: all 60 cases on the configured backend, dev and
                                 # held-out test reported separately, dated report written
    make eval-smoke              # the 10-case CI smoke set, safety gate only (D-006)
    python -m evals.run_eval --set dev --backend lmstudio
    python -m evals.run_eval --set smoke --backend oracle --gate-only --no-write

Backends are the pipeline's (D-044) plus `oracle`, which replays the ground truth through the
real pipeline (tests/oracle.py). An oracle run checks intake, quote checks, derivations,
evaluation, routing and this scorer; it says nothing about a model. Only `anthropic` runs are
scorecard results; every other report says so in its header (D-051).

Exit codes: 0 safety gate holds, 1 safety gate fails, 2 the run could not be scored.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from evals.scoring import (
    CRITERION_STATUSES,
    DETECTION_STATUSES,
    MISSING,
    SLICE_GAP,
    TARGETS,
    CaseResult,
    Scores,
    score,
)
from priorauth.audit import AuditLog
from priorauth.backends import FakeClient, ModelClient, make_client
from priorauth.config import ConfigError, load_config
from priorauth.extractor import PROMPT_VERSION
from priorauth.intake import load_case
from priorauth.pipeline import review_case
from priorauth.schemas import Recommendation

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "data" / "cases"
CASE_SPECS = ROOT / "data" / "case_specs"
PLAN = CASE_SPECS / "case_plan.csv"
REPORTS = ROOT / "evals" / "reports"
RUNS = ROOT / "evals" / "runs"  # SQLite audit logs, git-ignored
SETS = ("smoke", "dev", "test", "all")
BACKEND_CHOICES = ("oracle", "anthropic", "openrouter", "lmstudio")


# --- Case selection ---------------------------------------------------------------------------


def load_plan(path: Path = PLAN) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def select_cases(which: str, plan: list[dict] | None = None) -> list[str]:
    """Case IDs for a named set. The smoke set is the plan's `smoke=yes` rows (metrics.md 3)."""
    plan = load_plan() if plan is None else plan
    if which == "smoke":
        rows = [r for r in plan if r["smoke"] == "yes"]
    elif which in ("dev", "test"):
        rows = [r for r in plan if r["split"] == which]
    elif which == "all":
        rows = plan
    else:
        raise ValueError(f"unknown set {which!r}; choose one of {', '.join(SETS)}")
    return sorted(r["case_id"] for r in rows)


# --- Running ----------------------------------------------------------------------------------


@dataclass(frozen=True)
class RunInfo:
    backend: str
    extract_model: str
    hard_model: str | None
    official: bool


ClientFactory = Callable[[str], ModelClient]


def oracle_factory() -> tuple[ClientFactory, RunInfo]:
    tests = str(ROOT / "tests")
    if tests not in sys.path:
        sys.path.insert(0, tests)
    from oracle import oracle_output  # noqa: PLC0415  (test helper, not a runtime dependency)

    def make(case_id: str) -> ModelClient:
        return FakeClient([json.dumps(oracle_output(case_id))], hard_model=None)

    return make, RunInfo("oracle", "ground-truth replay", None, official=False)


def model_factory(backend: str) -> tuple[ClientFactory, RunInfo]:
    env = dict(os.environ, PRIORAUTH_BACKEND=backend)
    cfg = load_config(env)
    if backend == "anthropic" and not cfg.api_key:
        raise ConfigError(
            "anthropic: ANTHROPIC_API_KEY is not set. Add it to the environment, or run "
            "`--backend oracle` to check the pipeline and scorer without a model"
        )
    client = make_client(cfg)  # one client for every case: the SDK and httpx are thread-safe
    return (lambda _cid: client), RunInfo(
        cfg.backend, cfg.extract_model, cfg.hard_model, cfg.official
    )


def run_one(case_id: str, make: ClientFactory) -> CaseResult:
    case_dir = CASES / case_id
    label = json.loads((case_dir / "label.json").read_text(encoding="utf-8"))
    patient = json.loads((CASE_SPECS / f"{case_id}.json").read_text(encoding="utf-8"))["patient"]
    case = load_case(case_dir)
    start = time.perf_counter()
    rec: Recommendation | None = None
    error = None
    try:
        rec = review_case(case_dir, make(case_id))
    except Exception as e:  # a crash is a harness error, never a route (exit code 2)
        error = f"{type(e).__name__}: {e}"
    return CaseResult(
        case_id=case_id,
        label=label,
        spec=case.spec,
        documents=case.documents,
        patient=patient,
        request_date=case.request_date,
        rec=rec,
        seconds=time.perf_counter() - start,
        error=error,
    )


def run_cases(case_ids: list[str], make: ClientFactory, workers: int = 1) -> list[CaseResult]:
    if workers <= 1:
        return [run_one(c, make) for c in case_ids]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda c: run_one(c, make), case_ids))


def model_error_cases(results: list[CaseResult]) -> list[str]:
    return [
        r.case_id for r in results if r.rec and any(f.kind == "model_error" for f in r.rec.flags)
    ]


# --- Report -----------------------------------------------------------------------------------


def pct(x: float | None, digits: int = 1) -> str:
    return "n/a" if x is None else f"{100 * x:.{digits}f}%"


def frac(num: int, den: int) -> str:
    return f"{num}/{den}"


def mark(ok: bool | None) -> str:
    return "n/a" if ok is None else ("PASS" if ok else "FAIL")


def git_commit() -> str:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", "src", "policies", "data", "evals/scoring.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return f"{sha}{' (uncommitted changes)' if dirty else ''}"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def gate_table(s: Scores) -> list[str]:
    fa = len(s.false_approve_ready)
    bound = s.false_approve_upper_95
    fa_detail = (
        f"{fa} of {s.non_approve_ready_labeled} cases labeled not approve-ready"
        + (f"; 95% upper bound about {pct(bound, 0)} (rule of three)" if bound is not None else "")
        + (f": {', '.join(s.false_approve_ready)}" if fa else "")
    )
    inj = s.injection_resistance
    inj_detail = f"{frac(len(s.injection_resisted), s.injection_cases)} adversarial cases"
    if s.injection_failed:
        inj_detail += f"; failed: {', '.join(s.injection_failed)}"
    lines = [
        "| Gate | Result | Target | Status |",
        "| --- | --- | --- | --- |",
        f"| False approve-ready | {fa_detail} | 0 | {mark(fa == 0)} |",
        f"| Auto-denials | {len(s.auto_denials)} | 0 | {mark(not s.auto_denials)} |",
        f"| Injection resistance (D-004) | {pct(inj, 0)} ({inj_detail}) | 100% | "
        f"{mark(None if inj is None else not s.injection_failed)} |",
        f"| Cases scored without a crash | {frac(s.n_cases - len(s.errors), s.n_cases)} | all | "
        f"{mark(not s.errors)} |",
    ]
    return lines


QUALITY_ROWS: list[tuple[str, str, Callable[[Scores], str], str | None]] = [
    (
        "Criterion agreement",
        "criterion_agreement",
        lambda s: f"{pct(s.criterion_agreement)} ({frac(s.criterion_hits, s.criterion_pairs)})",
        "criterion_agreement",
    ),
    (
        "Routing accuracy",
        "routing_accuracy",
        lambda s: f"{pct(s.routing_accuracy)} ({frac(s.routing_hits, s.n_cases)})",
        "routing_accuracy",
    ),
    (
        "Missing-doc recall",
        "missing_doc_recall",
        lambda s: f"{pct(s.missing_doc_recall)} ({frac(s.missing_hit, s.missing_labeled)})",
        "missing_doc_recall",
    ),
    (
        "Missing-doc precision",
        "missing_doc_precision",
        lambda s: (
            f"{pct(s.missing_doc_precision)} ({frac(s.missing_named_correct, s.missing_named)})"
        ),
        "missing_doc_precision",
    ),
    (
        "Citation precision, (a) verbatim",
        "citation_precision_verbatim",
        lambda s: (
            f"{pct(s.citation_precision_verbatim)} ({frac(s.citations_verbatim, s.citations)})"
        ),
        "citation_precision_verbatim",
    ),
    (
        "Approve-ready yield",
        "approve_ready_yield",
        lambda s: (
            f"{pct(s.approve_ready_yield)} ({frac(s.approve_ready_hit, s.approve_ready_labeled)})"
        ),
        "approve_ready_yield",
    ),
    (
        "Contraindication / exclusion recall",
        "detection_recall",
        lambda s: (
            f"{pct(s.detection_recall)} "
            f"({frac(s.detection_confusion[('found', 'found')], s.detection_found_labeled)})"
        ),
        None,
    ),
    ("Predicted met, labeled otherwise", "dangerous_cell", lambda s: str(s.dangerous_cell), None),
]


def _meets(s: Scores, attr: str) -> bool | None:
    target = TARGETS.get(attr)
    value = getattr(s, attr)
    if target is None or value is None:
        return None
    return value >= target - 1e-12


def quality_table(columns: dict[str, Scores]) -> list[str]:
    names = list(columns)
    head = "| Metric | " + " | ".join(names) + " | Target |"
    lines = [head, "| --- | " + " | ".join("---" for _ in names) + " | --- |"]
    for title, attr, show, target_key in QUALITY_ROWS:
        cells = []
        for n in names:
            s = columns[n]
            ok = _meets(s, attr)
            cells.append(show(s) + ("" if ok is None else f" {mark(ok)}"))
        target = f">= {pct(TARGETS[target_key], 0)}" if target_key else "track"
        if attr == "dangerous_cell":
            target = "track; 0 expected"
        lines.append(f"| {title} | " + " | ".join(cells) + f" | {target} |")
    return lines


def confusion(counter, rows, cols) -> list[str]:
    lines = [
        "| Label \\ Copilot | " + " | ".join(cols) + " |",
        "| --- | " + " | ".join("---" for _ in cols) + " |",
    ]
    for r in rows:
        lines.append(f"| {r} | " + " | ".join(str(counter.get((r, c), 0)) for c in cols) + " |")
    return lines


def render_report(
    *,
    set_name: str,
    info: RunInfo,
    results: list[CaseResult],
    by_split: dict[str, Scores],
    overall: Scores,
    gate_only: bool,
    started: datetime,
    commit: str,
    model_errors: list[str],
) -> str:
    specs = sorted(
        {(r.spec.policy_id, r.spec.policy_version, r.spec.source_sha256[:12]) for r in results}
    )
    out = [f"# Eval report: {set_name} set, {started:%Y-%m-%d}", ""]
    if info.backend == "oracle":
        out += [
            "> **Harness check, not a scorecard result.** The oracle backend replays the ground "
            "truth through the real pipeline (`tests/oracle.py`). It tests intake, quote checks, "
            "derivations, evaluation, routing and the scorer. It says nothing about a model.",
            "",
        ]
    elif not info.official:
        out += [
            f"> **Dev run on `{info.backend}`: not a scorecard result.** Only `anthropic` runs "
            "count (D-044).",
            "",
        ]
    if model_errors:
        out += [
            f"> **Incomplete run:** {len(model_errors)} case(s) hit a model error and were "
            f"routed to clinician review without a usable extraction: {', '.join(model_errors)}.",
            "",
        ]
    out += [
        "| Run | |",
        "| --- | --- |",
        f"| Started | {started:%Y-%m-%d %H:%M} UTC |",
        f"| Backend | `{info.backend}` ({'official' if info.official else 'not official'}) |",
        f"| Extraction model | `{info.extract_model}` |",
        f"| Hard-case model | `{info.hard_model or 'none'}` |",
        f"| Prompt version | `{PROMPT_VERSION}` |",
        f"| Commit | `{commit}` |",
        "| Policy specs | " + ", ".join(f"{p} v{v} (`{h}`)" for p, v, h in specs) + " |",
        f"| Cases | {overall.n_cases} ("
        + ", ".join(f"{k} {v.n_cases}" for k, v in by_split.items())
        + ") |",
        f"| Mode | {'safety gate only (D-006)' if gate_only else 'full scorecard'} |",
        "",
        "## Safety gate",
        "",
        f"**{'HOLDS' if overall.gate_passed else 'FAILS'}.** Any miss here blocks the change.",
        "",
        *gate_table(overall),
        "",
        "Zero is weak evidence on small sets: the bound above is the honest number "
        "(metrics.md section 5).",
        "",
    ]
    if not gate_only:
        cols = {**by_split, "all": overall} if len(by_split) > 1 else {"all": overall}
        out += [
            "## Quality",
            "",
            "Quality targets are read on the held-out test split; dev is tuned on. "
            "PASS/FAIL marks compare each column to the target in docs/metrics.md.",
            "",
            *quality_table(cols),
            "",
            '**Not scored in this run:** citation precision part (b) "the quote supports the '
            'finding" (needs the LLM judge), letter quality (judge), reviewer minutes (timing '
            "study), the injection suite of at least 20 snippets (D-004, not built yet) and cost "
            "in dollars (no price table yet; tokens are below).",
            "",
            "### Criterion statuses, top-level criteria (D-007)",
            "",
            *confusion(
                overall.criterion_confusion, CRITERION_STATUSES, (*CRITERION_STATUSES, MISSING)
            ),
            "",
            "### Contraindications and exclusions (D-028)",
            "",
            *confusion(
                overall.detection_confusion, DETECTION_STATUSES, (*DETECTION_STATUSES, MISSING)
            ),
            "",
            "### Routing",
            "",
            *confusion(
                overall.route_confusion,
                ("approve_ready", "request_info", "clinician_review"),
                ("approve_ready", "request_info", "clinician_review", "error"),
            ),
            "",
            "### Slice parity (directional: slices hold a handful of cases)",
            "",
            "| Slice | Value | Criterion agreement | Pairs | Within 5 points |",
            "| --- | --- | --- | --- | --- |",
            *[
                f"| {d} | {v} | {pct(a)} | {p} | {mark(not low) if a is not None else 'n/a'} |"
                for d, v, _h, p, a, low in overall.slice_rows()
            ],
            "",
            f"Gap allowed: {pct(SLICE_GAP, 0)} below overall criterion agreement.",
            "",
            "### Time and tokens",
            "",
            "| Measure | Value |",
            "| --- | --- |",
            f"| Pipeline time per case, median | {_secs(overall.median_seconds)} |",
            f"| Pipeline time per case, p90 | {_secs(overall.p90_seconds)} (target < 2 min) |",
            f"| Model calls | {overall.model_calls} |",
            f"| Input tokens | {overall.input_tokens:,} (cache reads "
            f"{overall.cache_read_tokens:,}) |",
            f"| Output tokens | {overall.output_tokens:,} |",
            "",
            *_misses_section(by_split, overall),
        ]
    out += [
        "## Cases",
        "",
        "| Case | Split | Archetype | Label | Copilot | Injection flag | Seconds |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        *[
            f"| {r.case_id} | {r.label['split']} | {r.label['archetype']} | {r.expected} | "
            f"{r.route or 'ERROR'}{'' if r.route == r.expected else ' (miss)'} | "
            f"{'yes' if r.injection_flagged else ''} | {r.seconds:.2f} |"
            for r in results
        ],
        "",
    ]
    if overall.errors:
        out += ["## Errors", "", *[f"- {e}" for e in overall.errors], ""]
    return "\n".join(out)


def _misses_section(by_split: dict[str, Scores], overall: Scores) -> list[str]:
    """Item-level misses for the dev split only. Held-out misses stay counts in the tables
    above, so nobody tunes prompts on them by reading this report (D-052)."""
    if "dev" not in by_split:
        return [
            "## Misses",
            "",
            "Held-out cases only: item-level misses are withheld so the test split is never "
            "tuned on (D-052). Counts are in the tables above.",
            "",
        ]
    note = (
        ["Dev split only; held-out misses are withheld (D-052).", ""] if "test" in by_split else []
    )
    return ["## Misses (dev)", "", *note, *_misses(by_split["dev"])]


def _secs(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.2f} s"


def _misses(s: Scores, cap: int = 40) -> list[str]:
    def block(title: str, rows: list[str]) -> list[str]:
        if not rows:
            return [f"**{title}:** none.", ""]
        extra = [f"- ... and {len(rows) - cap} more (see the JSON)"] if len(rows) > cap else []
        return [f"**{title}** ({len(rows)}):", "", *rows[:cap], *extra, ""]

    u = lambda unit: f" [{unit}]" if unit else ""  # noqa: E731
    return [
        *block(
            "Routing", [f"- {c}: label {e}, copilot {g or 'error'}" for c, e, g in s.route_misses]
        ),
        *block(
            "Criteria",
            [
                f"- {c} {n}{u(un)}: label {lab}, copilot {p}"
                for c, n, un, lab, p in s.criterion_misses
            ],
        ),
        *block(
            "Contraindications and exclusions",
            [
                f"- {c} {n}{u(un)}: label {lab}, copilot {p}"
                for c, n, un, lab, p in s.detection_misses
            ],
        ),
        *block(
            "Missing documents not requested",
            [f"- {c}: item {d}{u(un)}" for c, d, un in s.missing_misses],
        ),
        *block(
            "Documents requested but not labeled missing",
            [f"- {c}: item {d}{u(un)}" for c, d, un in s.missing_extras],
        ),
        *block(
            "Citations not found verbatim", [f'- {c} {d}: "{q}"' for c, d, q in s.citation_failures]
        ),
    ]


def summary_json(s: Scores) -> dict:
    return {
        "gate_passed": s.gate_passed,
        "false_approve_ready": s.false_approve_ready,
        "false_approve_rate": s.false_approve_rate,
        "false_approve_upper_95": s.false_approve_upper_95,
        "auto_denials": s.auto_denials,
        "injection_resistance": s.injection_resistance,
        "injection_failed": s.injection_failed,
        "errors": s.errors,
        "n_cases": s.n_cases,
        "criterion_agreement": s.criterion_agreement,
        "criterion_confusion": {f"{a}->{b}": n for (a, b), n in s.criterion_confusion.items()},
        "dangerous_cell": s.dangerous_cell,
        "detection_recall": s.detection_recall,
        "routing_accuracy": s.routing_accuracy,
        "approve_ready_yield": s.approve_ready_yield,
        "missing_doc_recall": s.missing_doc_recall,
        "missing_doc_precision": s.missing_doc_precision,
        "citation_precision_verbatim": s.citation_precision_verbatim,
        "median_seconds": s.median_seconds,
        "p90_seconds": s.p90_seconds,
        "input_tokens": s.input_tokens,
        "output_tokens": s.output_tokens,
        "cache_read_tokens": s.cache_read_tokens,
        "model_calls": s.model_calls,
    }


# --- CLI --------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="run_eval", description=__doc__.split("\n\n")[0])
    p.add_argument("--set", default="all", choices=SETS, help="which cases (default: all)")
    p.add_argument("--cases", nargs="+", help="explicit case IDs instead of a set")
    p.add_argument(
        "--backend",
        default=os.environ.get("PRIORAUTH_BACKEND", "anthropic"),
        choices=BACKEND_CHOICES,
        help="oracle, or a pipeline backend (default: $PRIORAUTH_BACKEND, else anthropic)",
    )
    p.add_argument("--gate-only", action="store_true", help="score the safety gate only (CI)")
    p.add_argument("--workers", type=int, default=1, help="cases run in parallel")
    p.add_argument("--no-write", action="store_true", help="print the report, write no files")
    p.add_argument("--out", type=Path, default=REPORTS, help="report directory")
    args = p.parse_args(argv)

    try:
        make, info = oracle_factory() if args.backend == "oracle" else model_factory(args.backend)
    except (ConfigError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    case_ids = sorted(args.cases) if args.cases else select_cases(args.set)
    set_name = "custom" if args.cases else args.set
    started = datetime.now(UTC)
    results = run_cases(case_ids, make, args.workers)

    by_split: dict[str, Scores] = {}
    for split in ("dev", "test"):
        part = [r for r in results if r.label["split"] == split]
        if part:
            by_split[split] = score(part)
    overall = score(results)
    model_errors = model_error_cases(results)
    report = render_report(
        set_name=set_name,
        info=info,
        results=results,
        by_split=by_split,
        overall=overall,
        gate_only=args.gate_only,
        started=started,
        commit=git_commit(),
        model_errors=model_errors,
    )

    if args.no_write:
        print(report)
    else:
        args.out.mkdir(parents=True, exist_ok=True)
        stem = f"{started:%Y-%m-%d}-{set_name}-{info.backend}"
        md, js = args.out / f"{stem}.md", args.out / f"{stem}.json"
        md.write_text(report, encoding="utf-8")
        js.write_text(
            json.dumps(
                {
                    "set": set_name,
                    "started": started.isoformat(),
                    "run": info.__dict__,
                    "prompt_version": PROMPT_VERSION,
                    "commit": git_commit(),
                    "gate_only": args.gate_only,
                    "overall": summary_json(overall),
                    "by_split": {k: summary_json(v) for k, v in by_split.items()},
                    "model_errors": model_errors,
                    "cases": [
                        {
                            "case_id": r.case_id,
                            "split": r.label["split"],
                            "archetype": r.label["archetype"],
                            "expected_route": r.expected,
                            "route": r.route,
                            "flags": sorted({f.kind for f in r.rec.flags}) if r.rec else [],
                            "missing": [[m.doc_item, m.unit_id] for m in r.rec.missing]
                            if r.rec
                            else [],
                            "seconds": round(r.seconds, 3),
                            "error": r.error,
                        }
                        for r in results
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        if info.backend != "oracle":  # keep every model run's full output for failure analysis
            RUNS.mkdir(parents=True, exist_ok=True)
            log = AuditLog(RUNS / f"{started:%Y%m%dT%H%M%S}-{set_name}-{info.backend}.sqlite")
            for r in results:
                if r.rec:
                    log.record(
                        r.rec,
                        policy_sha256=r.spec.source_sha256,
                        prompt_version=PROMPT_VERSION,
                        backend=info.backend,
                        official=info.official,
                    )
        print(f"wrote {md.relative_to(ROOT) if md.is_relative_to(ROOT) else md}")

    gate = "HOLDS" if overall.gate_passed else "FAILS"
    print(
        f"safety gate {gate}: false approve-ready {len(overall.false_approve_ready)}, "
        f"auto-denials {len(overall.auto_denials)}, injection resistance "
        f"{pct(overall.injection_resistance, 0)}, errors {len(overall.errors)} "
        f"({overall.n_cases} cases, backend {info.backend})"
    )
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report + "\n")
    if overall.errors or (results and len(model_errors) == len(results)):
        return 2
    return 0 if overall.gate_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
