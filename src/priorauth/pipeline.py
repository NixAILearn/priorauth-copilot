"""One case end to end: intake -> extract -> verify -> evaluate -> route -> audit."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from priorauth.audit import AuditLog
from priorauth.backends import ModelClient
from priorauth.evaluator import evaluate
from priorauth.extractor import PROMPT_VERSION, extract, verify
from priorauth.intake import load_case
from priorauth.router import missing_documents, route_case
from priorauth.schemas import Flag, Recommendation, Route


def review_case(
    case_dir: str | Path,
    client: ModelClient,
    audit: AuditLog | None = None,
    *,
    official: bool = False,
) -> Recommendation:
    case = load_case(case_dir)
    raw = extract(client, case)
    flags: list[Flag] = list(case.flags)
    if raw.output is None:
        # Nothing the model said can be used, so nothing can be checked: a person reviews.
        flags.append(
            Flag(
                kind="model_error",
                route=Route.CLINICIAN_REVIEW,
                detail=f"extraction failed after retry: {raw.error}",
            )
        )
    verified = verify(case, raw.output)
    ev = evaluate(case, verified)
    route, reasons = route_case(case.spec, case.unit_ids, ev, flags)
    missing = missing_documents(case.spec, case.unit_ids, ev) if route == Route.REQUEST_INFO else []
    rec = Recommendation(
        case_id=case.case_id,
        request_id=case.request.request_id,
        policy_id=case.spec.policy_id,
        policy_version=case.spec.policy_version,
        route=route,
        reasons=reasons,
        findings=ev.findings,
        flags=[*flags, *ev.flags],
        missing=missing,
        model_calls=raw.calls,
        created_at=datetime.now(UTC),
    )
    if audit is not None:
        audit.record(
            rec,
            policy_sha256=case.spec.source_sha256,
            prompt_version=PROMPT_VERSION,
            backend=client.backend,
            official=official,
        )
    return rec
