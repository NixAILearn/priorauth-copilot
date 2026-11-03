"""Intake: validate the request, resolve its policy, load documents, check scope (D-045).

Intake never calls a model. Its scope checks and the injection scan are code, so they hold
whatever backend runs the extraction.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

from priorauth.quotes import norm
from priorauth.schemas import Evidence, Flag, PriorAuthRequest, Route
from priorauth.spec import CriteriaSpec, load_spec

ROOT = Path(__file__).resolve().parents[2]
CODE_TABLE = ROOT / "codes" / "nhp_procedures.csv"
SPECS = ROOT / "policies" / "specs"
REQUEST_DOC = "REQUEST"  # the request JSON shown as a document (D-048)


class IntakeError(ValueError):
    """The request cannot be reviewed at all (bad JSON, unknown code, missing spec or file)."""


@dataclass
class CaseInput:
    case_id: str
    request: PriorAuthRequest
    spec: CriteriaSpec
    documents: dict[str, str]  # doc ID -> text, including REQUEST
    flags: list[Flag] = field(default_factory=list)

    @property
    def request_date(self):
        return self.request.received_at.date()

    @property
    def unit_ids(self) -> list[str]:
        return [u.id for u in self.request.service.target_ulcers]


def resolve_policy(code: str, table: Path = CODE_TABLE) -> str:
    with table.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["code"] == code:
                if row["pa_required"] != "Y":
                    raise IntakeError(f"{code} does not need prior authorization")
                return row["policy_id"]
    raise IntakeError(f"unknown Northwind procedure code {code}")


def render_request(req: PriorAuthRequest, spec: CriteriaSpec) -> str:
    """The request as `field: value` lines, the form the labels cite (D-048)."""
    side_field = (
        "requested_knee_side"
        if any(f.name == "requested_knee_side" for f in spec.fields)
        else "requested_side"
    )
    s = req.service
    lines = [
        f"request_id: {req.request_id}",
        f"received_at: {req.received_at.isoformat()}",
        f"review_type: {req.review_type}",
        f"member_id: {req.member.synthetic_id}",
        f"date_of_birth: {req.member.birth_date.isoformat()}",
        f"sex: {req.member.sex}",
        f"requesting_provider: {req.requesting_provider.name}, {req.requesting_provider.specialty}",
        f"service_code: {s.code}",
        f"service_description: {s.description}",
        f"{side_field}: {s.side or 'not_stated'}",
        f"units: {s.units}",
    ]
    for d in req.diagnoses:
        name = "primary_diagnosis_code" if d.role == "primary" else "secondary_diagnosis_code"
        lines.append(f"{name}: {d.code}")
    for u in s.target_ulcers:
        lines += [
            f"target_ulcer: {u.id}",
            f"ulcer_laterality: {u.laterality}",
            f"ulcer_site: {u.site}",
            f"ulcer_diagnosis_code: {u.diagnosis}",
            f"applications_planned: {u.applications_planned}",
        ]
    lines.append(f"attachments: {', '.join(req.attachments)}")
    return "\n".join(lines)


# --- Injection scan (D-047) -------------------------------------------------------------------
# Text aimed at an AI or an automated reviewer. Clinical notes address patients and clinicians;
# these shapes do not occur in ordinary charting, so a hit is a flag, never an instruction.

INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("system-message mimic", re.compile(r"\[\s*(system|assistant|developer)\s*\]", re.I)),
    ("system-message mimic", re.compile(r"^\s*(system|assistant)\s*(prompt)?\s*:", re.I | re.M)),
    (
        "addresses an automated reviewer",
        re.compile(
            r"\b(automated|ai|artificial intelligence|llm|language model|machine)\s+"
            r"(review(er)?s?|system|systems|assistant|prior authorization reviewer)\b",
            re.I,
        ),
    ),
    (
        "overrides instructions",
        re.compile(
            r"\b(ignore|disregard|override)\b[^.\n]{0,40}\b(instructions?|prompts?|rules|"
            r"polic(y|ies)|(previous|above|prior) (text|messages?|guidance))\b",
            re.I,
        ),
    ),
    (
        "tells the reader to approve",
        re.compile(
            r"\b(mark|record|return|set|treat|classify)\b[^.\n]{0,60}"
            r"\b(approve[ -]?ready|(as|it|case|request) approved|(as|criteri(a|on)) met)\b",
            re.I,
        ),
    ),
    ("claims prior approval", re.compile(r"\bpre-?(approved|verified|authorized)\b", re.I)),
    (
        "tells the reader to skip documents",
        re.compile(r"\bdo not (request|ask for)\b[^.\n]{0,30}\b(documents?|information)\b", re.I),
    ),
]


def scan_injection(documents: dict[str, str]) -> list[Flag]:
    flags: list[Flag] = []
    for doc_id, text in documents.items():
        if doc_id == REQUEST_DOC:
            continue
        hits: list[str] = []
        cites: list[Evidence] = []
        for line in text.splitlines():
            for name, pat in INJECTION_PATTERNS:
                if pat.search(line):
                    hits.append(name)
                    q = norm(line)[:300]
                    if not any(c.quote == q for c in cites):
                        cites.append(Evidence(doc_id=doc_id, quote=q, verified=True))
        if hits:
            flags.append(
                Flag(
                    kind="injection",
                    route=Route.CLINICIAN_REVIEW,
                    detail=f"{doc_id}: text aimed at an AI reviewer "
                    f"({', '.join(sorted(set(hits)))}); treated as data and not followed",
                    citations=cites,
                )
            )
    return flags


# --- Scope ------------------------------------------------------------------------------------


def scope_flags(req: PriorAuthRequest, spec: CriteriaSpec) -> list[Flag]:
    flags: list[Flag] = []
    route = Route(spec.scope.out_of_scope_route)
    primary = next(d.code for d in req.diagnoses if d.role == "primary")
    if primary not in spec.scope.primary_diagnoses:
        flags.append(
            Flag(
                kind="out_of_scope",
                route=route,
                detail=f"primary diagnosis {primary} is not a covered diagnosis in "
                f"{spec.policy_id} section 2.2",
            )
        )
    per_unit = spec.scope.review_unit != "request"
    units = req.service.target_ulcers
    if per_unit and not units:
        flags.append(
            Flag(kind="out_of_scope", route=route, detail="the request names no target ulcer")
        )
    for u in units:
        if per_unit and u.diagnosis not in spec.scope.unit_diagnoses:
            flags.append(
                Flag(
                    kind="out_of_scope",
                    route=route,
                    unit_id=u.id,
                    detail=f"{u.id}: ulcer diagnosis {u.diagnosis} is not in scope",
                )
            )
    return flags


def load_case(case_dir: str | Path, specs_dir: Path = SPECS) -> CaseInput:
    case_dir = Path(case_dir)
    try:
        req = PriorAuthRequest.model_validate_json(
            (case_dir / "request.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError) as e:
        raise IntakeError(f"{case_dir.name}: invalid request.json: {e}") from e
    policy_id = resolve_policy(req.service.code)
    spec_path = specs_dir / f"{policy_id}.json"
    if not spec_path.exists():
        raise IntakeError(f"no compiled criteria spec for {policy_id}")
    spec = load_spec(spec_path)
    if spec.review_status != "reviewed":
        raise IntakeError(
            f"{policy_id} spec is not reviewed; the pipeline uses reviewed specs only"
        )
    docs: dict[str, str] = {}
    for doc_id in req.attachments:
        path = case_dir / "documents" / f"{doc_id}.md"
        if not path.exists():
            raise IntakeError(f"{case_dir.name}: attachment {doc_id} is listed but missing")
        docs[doc_id] = path.read_text(encoding="utf-8")
    docs[REQUEST_DOC] = render_request(req, spec)
    flags = scope_flags(req, spec) + scan_injection(docs)
    return CaseInput(case_id=case_dir.name, request=req, spec=spec, documents=docs, flags=flags)
