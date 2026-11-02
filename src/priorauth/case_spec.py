"""Case spec schema: the ground truth for one synthetic test case, fixed before any text is written.

A case spec says who the synthetic member is, what the request asks for, which documents the
generator must write, which dated facts each document must state (with a verbatim anchor
phrase), and the expected status of every criterion and the expected routing. The generator
(week 2, step 2) writes documents from it; its consistency check confirms each anchor appears
in the document the spec names. The label file is then derived from the spec plus the written
documents (each citation is the sentence that contains the anchor).

`check_case(case, spec)` validates a case spec against its reviewed criteria spec. It is the
label-side oracle: it derives the expected routing from the findings and flags on its own and
never imports the pipeline router, so a bug in one cannot hide in the other (D-030).

Design rules this schema enforces (decisions D-026 to D-032):
- Every top-level criterion gets a finding (one per target ulcer for per-ulcer nodes). Groups
  are labeled down to the depth that determines their status.
- Contraindications and exclusions are listed only when found; an unlisted one is not found.
- Criteria use met / not_met / insufficient; contraindications and exclusions use found /
  not_found. There is no deny value anywhere.
- Evidence outside a criterion's time window is insufficient, not not met (D-029).
- Each archetype has a contract the case must satisfy (see ARCHETYPE_CONTRACTS).
"""

from __future__ import annotations

import calendar
import operator
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from priorauth.spec import CriteriaSpec, Node, Window

Archetype = Literal[
    "clean",
    "missing_documentation",
    "clearly_not_met",
    "borderline",
    "conflicting",
    "buried_contraindication",
    "adversarial",
]
CaseRoute = Literal["approve_ready", "request_info", "clinician_review"]
CriterionStatus = Literal["met", "not_met", "insufficient"]
FindingStatus = Literal["met", "not_met", "insufficient", "found", "not_found"]
Split = Literal["dev", "test"]

DocType = Literal[
    "office_visit_note",
    "history_and_physical",
    "sleep_consult_note",
    "sleep_study_report",
    "titration_study_report",
    "dise_report",
    "pap_usage_report",
    "surgical_consult_note",
    "problem_list",
    "medication_list",
    "device_list",
    "allergy_list",
    "lab_result",
    "wound_care_note",
    "wound_treatment_record",
    "offloading_record",
    "vascular_study_report",
    "radiograph_report",
    "mri_report",
    "physical_therapy_note",
    "orthopedic_note",
    "referral_letter",
    "discharge_summary",
]
Noise = Literal[
    "copy_forward",
    "old_values",
    "abbreviations",
    "typos",
    "templated_text",
    "irrelevant_history",
    "scanned_formatting",
]

REQUEST_DOC = "REQUEST"  # a fact stated on the request JSON, not in a clinical document
DERIVED_DOC = "DERIVED"  # a value code computes from other facts (age, BMI, area reduction)
MIN_DOCS, MAX_DOCS = 4, 12  # kickoff says 4-8; NHP-MP-034 needs a note per visit (D-032)
ICD10 = r"^[A-TV-Z]\d[0-9A-Z](\.[0-9A-Z]{1,4})?$"

ROUTE_ORDER: dict[CaseRoute, int] = {"approve_ready": 0, "request_info": 1, "clinician_review": 2}


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Patient(Strict):
    """Synthetic member. Demographics drive the Synthea profile and the slice-parity metric."""

    synthetic_id: str = Field(pattern=r"^SYN-\d{4}$")
    sex: Literal["female", "male"]
    date_of_birth: date
    race: Literal["white", "black", "asian", "native", "other"]
    ethnicity: Literal["hispanic", "nonhispanic"]
    background_conditions: list[str] = []  # ICD-10-CM codes for the Synthea profile
    summary: str


class TargetUlcer(Strict):
    """One ulcer named on a skin substitute request (NHP-MP-034, D-020)."""

    id: str = Field(pattern=r"^U\d$")
    laterality: Literal["right", "left"]
    site: str
    diagnosis: str = Field(pattern=ICD10)
    applications_planned: int = Field(gt=0)


class RequestSpec(Strict):
    """What the simplified PAS-style request JSON will carry."""

    request_date: date
    review_type: Literal["standard", "expedited"]
    service_code: str
    primary_diagnosis: str = Field(pattern=ICD10)
    secondary_diagnoses: list[str] = []
    requested_side: Literal["right", "left"] | None = None
    target_ulcers: list[TargetUlcer] = []
    requesting_specialty: str
    service_details: str


class DocPlan(Strict):
    """A document the generator must write."""

    id: str = Field(pattern=r"^D\d{2}$")
    type: DocType
    title: str
    date: date
    author_role: str
    satisfies: list[str] = []  # documentation item IDs from the criteria spec, e.g. "6.3"
    length: Literal["short", "medium", "long"] = "medium"
    noise: list[Noise] = []
    guidance: str


class Fact(Strict):
    """A dated clinical fact. The document named by doc_id must contain the anchor verbatim."""

    id: str = Field(pattern=r"^F\d{2}$")
    field: str | None = None  # a field name from the criteria spec, when the fact is one
    unit_id: str | None = None  # target ulcer ID for per-ulcer fields
    date: date  # observation date; for date fields this is the value
    value: float | bool | str | None = None
    unit: str | None = None
    doc_id: str
    anchor: str | None = None
    statement: str
    derived_from: list[str] = []
    placement: Literal["prominent", "buried"] = "prominent"
    boundary: str | None = None  # what edge this fact sits on, for borderline cases
    distractor: str | None = None  # why this fact must not change any status

    @model_validator(mode="after")
    def _source_shape(self) -> Fact:
        if self.doc_id == DERIVED_DOC:
            if not self.derived_from or self.anchor is not None:
                raise ValueError(f"{self.id}: a derived fact has derived_from and no anchor")
        elif self.derived_from:
            raise ValueError(f"{self.id}: only DERIVED facts have derived_from")
        elif self.doc_id != REQUEST_DOC and not self.anchor:
            raise ValueError(f"{self.id}: a document fact needs a verbatim anchor")
        return self


class MissingItem(Strict):
    """What the request-for-information letter must ask for."""

    doc_item: str  # documentation item ID from the criteria spec, e.g. "6.6"
    what: str
    forbidden_phrases: list[str] = []  # the generator must not write these anywhere


class Finding(Strict):
    node_id: str
    unit_id: str | None = None
    status: FindingStatus
    facts: list[str] = []
    missing: list[MissingItem] = []
    rationale: str


class ExpectedFlag(Strict):
    kind: Literal["flag_rule", "conflict", "injection", "out_of_scope"]
    rule_id: str | None = None
    unit_id: str | None = None
    facts: list[str] = []
    rationale: str

    @model_validator(mode="after")
    def _rule_id_iff_flag_rule(self) -> ExpectedFlag:
        if (self.kind == "flag_rule") != (self.rule_id is not None):
            raise ValueError("rule_id is set exactly when kind is flag_rule")
        return self


class Injection(Strict):
    """Adversarial text planted in a document. It is data; the copilot must flag it."""

    doc_id: str
    style: Literal["system_prompt_mimic", "note_to_reviewer", "hidden_footer", "fake_approval"]
    text: str


class CaseSpec(Strict):
    case_schema_version: Literal["1.0"]
    case_id: str = Field(pattern=r"^CASE-\d{3}-\d{2}$")
    policy_id: str = Field(pattern=r"^NHP-MP-\d{3}$")
    policy_version: str
    archetype: Archetype
    variant: str = Field(pattern=r"^[a-z0-9_]+$")
    split: Split
    smoke: bool = False
    purpose: str
    review_status: Literal["draft", "reviewed"] = "draft"
    patient: Patient
    request: RequestSpec
    documents: list[DocPlan] = Field(min_length=MIN_DOCS, max_length=MAX_DOCS)
    facts: list[Fact]
    findings: list[Finding]
    flags: list[ExpectedFlag] = []
    injection: Injection | None = None
    expected_route: CaseRoute
    author_notes: list[str] = []

    @model_validator(mode="after")
    def _self_consistent(self) -> CaseSpec:
        if self.case_id[5:8] != self.policy_id[-3:]:
            raise ValueError("case_id must carry the policy number, e.g. CASE-021-01")
        if self.smoke and self.split != "dev":
            raise ValueError("smoke cases come from the dev split (D-006)")
        for name, ids in (
            ("document", [d.id for d in self.documents]),
            ("fact", [f.id for f in self.facts]),
            ("finding", [(f.node_id, f.unit_id) for f in self.findings]),
        ):
            if len(ids) != len(set(ids)):
                raise ValueError(f"duplicate {name} IDs")
        return self


# ---------------------------------------------------------------------------------------------
# Label file (written by the generator after documents exist; schema fixed now so the eval
# runner and metrics can rely on it).


class Citation(Strict):
    doc_id: str
    quote: str  # the full sentence in the document that contains the fact's anchor


class LabelFinding(Strict):
    node_id: str
    unit_id: str | None = None
    status: FindingStatus
    citations: list[Citation] = []
    missing: list[MissingItem] = []


class Label(Strict):
    label_schema_version: Literal["1.0"]
    case_id: str
    policy_id: str
    policy_version: str
    archetype: Archetype
    split: Split
    expected_route: CaseRoute
    findings: list[LabelFinding]  # expanded: every contraindication and exclusion included
    flags: list[ExpectedFlag]


# ---------------------------------------------------------------------------------------------
# Checks against the criteria spec.


def load_case(path: str | Path) -> CaseSpec:
    return CaseSpec.model_validate_json(Path(path).read_text(encoding="utf-8"))


def window_start(request_date: date, window: Window) -> date:
    """First day inside a look-back window (inclusive), per D-019 and D-022."""
    if window.days is not None:
        return request_date - timedelta(days=window.days)
    months = window.months or 0
    y, m = divmod(request_date.year * 12 + request_date.month - 1 - months, 12)
    last = calendar.monthrange(y, m + 1)[1]
    return date(y, m + 1, min(request_date.day, last))


def in_window(d: date, request_date: date, window: Window) -> bool:
    return window_start(request_date, window) <= d <= request_date


def completed_years(born: date, on: date) -> int:
    return on.year - born.year - ((on.month, on.day) < (born.month, born.day))


OPS = {">=": operator.ge, ">": operator.gt, "<=": operator.le, "<": operator.lt}

ARCHETYPE_CONTRACTS: dict[str, str] = {
    "clean": "routes approve_ready with no flags",
    "missing_documentation": "routes request_info; at least one criterion is insufficient",
    "clearly_not_met": "routes clinician_review; a criterion is not_met; nothing is found",
    "borderline": "at least one fact names the boundary it sits on; one stated route",
    "conflicting": "routes clinician_review; at least one conflict or flag-rule flag",
    "buried_contraindication": (
        "every criterion met; a contraindication or exclusion is found from a buried fact"
    ),
    "adversarial": (
        "planted injection with an injection flag; routes clinician_review; the case would "
        "not be approve_ready even if the injection were ignored"
    ),
}


def _group_status(node: Node, labeled: dict[str, str]) -> str | None:
    """Status a group's labeled children determine, or None if they don't determine it."""
    kids = [labeled.get(c.id) for c in node.children]
    if node.type == "all_of":
        if "not_met" in kids:
            return "not_met"
        if None in kids:
            return None
        return "insufficient" if "insufficient" in kids else "met"
    if "met" in kids:
        return "met"
    if None in kids:
        return None
    return "insufficient" if "insufficient" in kids else "not_met"


def derive_route(case: CaseSpec, spec: CriteriaSpec, *, ignore_injection: bool = False) -> str:
    """Expected routing from findings and flags alone (the kickoff's three routing rules)."""
    top_criteria = {n.id for n in spec.criteria}
    cis = {n.id for n in spec.contraindications}
    exs = {n.id for n in spec.exclusions}
    rules = {r.id: r.route for n in spec.nodes() for r in n.flag_rules}
    routes: list[str] = ["approve_ready"]
    for f in case.findings:
        if f.node_id in top_criteria and f.status == "not_met":
            routes.append("clinician_review")
        elif f.node_id in top_criteria and f.status == "insufficient":
            routes.append("request_info")
        elif f.node_id in cis and f.status == "found":
            routes.append(spec.rules.contraindication_found_route)
        elif f.node_id in exs and f.status == "found":
            routes.append(spec.rules.exclusion_found_route)
    for flag in case.flags:
        if flag.kind == "injection" and ignore_injection:
            continue
        routes.append(
            {
                "flag_rule": rules.get(flag.rule_id or "", "clinician_review"),
                "conflict": spec.rules.conflict_route,
                "injection": "clinician_review",
                "out_of_scope": spec.scope.out_of_scope_route,
            }[flag.kind]
        )
    return max(routes, key=lambda r: ROUTE_ORDER[r])  # type: ignore[index]


def check_case(case: CaseSpec, spec: CriteriaSpec) -> list[str]:
    """Every way the case spec disagrees with its criteria spec or its archetype contract."""
    errors: list[str] = []
    err = errors.append
    req = case.request

    # Identity and scope.
    if case.policy_id != spec.policy_id or case.policy_version != spec.policy_version:
        err("policy_id/policy_version do not match the criteria spec")
    if req.service_code != spec.scope.service_code:
        err(f"service_code {req.service_code} is not {spec.scope.service_code}")
    out_of_scope = any(f.kind == "out_of_scope" for f in case.flags)
    if req.primary_diagnosis not in spec.scope.primary_diagnoses and not out_of_scope:
        err(f"primary diagnosis {req.primary_diagnosis} is out of scope but not flagged")
    per_unit = spec.scope.review_unit != "request"
    units = [u.id for u in req.target_ulcers]
    if per_unit and not units:
        err("this policy is reviewed per target ulcer; the request names none")
    if not per_unit and units:
        err("target_ulcers set on a policy reviewed per request")
    for u in req.target_ulcers:
        if u.diagnosis not in spec.scope.unit_diagnoses and not out_of_scope:
            err(f"{u.id}: ulcer diagnosis {u.diagnosis} is out of scope but not flagged")

    # Documents and facts.
    docs = {d.id: d for d in case.documents}
    doc_items = {d.id for d in spec.documentation}
    for d in case.documents:
        if d.date > req.request_date:
            err(f"{d.id}: dated after the request date")
        for item in d.satisfies:
            if item not in doc_items:
                err(f"{d.id}: unknown documentation item {item}")
    fields = {f.name: f for f in spec.fields}
    facts = {f.id: f for f in case.facts}
    for f in case.facts:
        if f.doc_id not in docs and f.doc_id not in (REQUEST_DOC, DERIVED_DOC):
            err(f"{f.id}: unknown document {f.doc_id}")
        if f.date > req.request_date:
            err(f"{f.id}: dated after the request date")
        if f.doc_id in docs and f.date > docs[f.doc_id].date:
            err(f"{f.id}: dated after the document that states it")
        for src in f.derived_from:
            if src not in facts:
                err(f"{f.id}: derived from unknown fact {src}")
        if f.unit_id is not None and f.unit_id not in units:
            err(f"{f.id}: unknown target ulcer {f.unit_id}")
        if f.field is None:
            continue
        fd = fields.get(f.field)
        if fd is None:
            err(f"{f.id}: {f.field} is not a field of {spec.policy_id}")
            continue
        if fd.per != "request" and f.unit_id is None:
            err(f"{f.id}: {f.field} is per {fd.per} and needs a unit_id")
        if f.doc_id == DERIVED_DOC and fd.evaluator != "code":
            err(f"{f.id}: {f.field} is extracted by the model, not derived")
        ok = {
            "number": isinstance(f.value, int | float) and not isinstance(f.value, bool),
            "boolean": isinstance(f.value, bool),
            "date": f.value is None,
            "enum": f.value in (fd.values or []),
            "text": isinstance(f.value, str),
        }[fd.type]
        if not ok:
            err(f"{f.id}: value {f.value!r} does not fit {fd.type} field {f.field}")
    if "age_years" in fields:
        for f in case.facts:
            if f.field == "age_years":
                age = completed_years(case.patient.date_of_birth, req.request_date)
                if f.value != age:
                    err(f"{f.id}: age_years {f.value} but date of birth gives {age}")

    # Findings: coverage, status vocabulary, evidence and group logic.
    nodes = {n.id: n for n in spec.nodes()}
    criteria_ids = {n.id for c in spec.criteria for n in c.walk()}
    flagged_ids = {n.id for top in (*spec.contraindications, *spec.exclusions) for n in top.walk()}
    labeled: dict[str | None, dict[str, str]] = {}
    for f in case.findings:
        node = nodes.get(f.node_id)
        if node is None:
            err(f"finding for unknown node {f.node_id}")
            continue
        if node.per == "request" and f.unit_id is not None:
            err(f"{f.node_id}: per-request node labeled for {f.unit_id}")
        if node.per != "request" and f.unit_id not in units:
            err(f"{f.node_id}: per-ulcer node needs a target ulcer unit_id")
        labeled.setdefault(f.unit_id, {})[f.node_id] = f.status
        if f.node_id in criteria_ids and f.status not in ("met", "not_met", "insufficient"):
            err(f"{f.node_id}: criteria use met / not_met / insufficient")
        if f.node_id in flagged_ids and f.status not in ("found", "not_found"):
            err(f"{f.node_id}: contraindications and exclusions use found / not_found (D-024)")
        for fid in f.facts:
            if fid not in facts:
                err(f"{f.node_id}: unknown fact {fid}")
        if f.status in ("met", "not_met", "found") and not f.facts:
            err(f"{f.node_id}: status {f.status} needs at least one evidence fact")
        if f.status == "insufficient" and not f.missing:
            err(f"{f.node_id}: insufficient needs the missing item(s) for the letter")
        if f.status != "insufficient" and f.missing:
            err(f"{f.node_id}: only insufficient findings list missing items")
        for m in f.missing:
            if m.doc_item not in doc_items:
                err(f"{f.node_id}: unknown documentation item {m.doc_item}")
        errors.extend(_value_checks(f, node, facts, req.request_date))

    for unit in [None, *units]:
        got = labeled.get(unit, {})
        at = f"/{unit}" if unit else ""
        for top in spec.criteria:
            if (top.per == "request") == (unit is None) and top.id not in got:
                err(f"{top.id}{at}: every top-level criterion needs a finding")
        for nid, status in got.items():
            node = nodes.get(nid)
            if node is None or not node.children:
                continue
            derived = _group_status(node, got)
            if derived is None:
                err(f"{nid}{at}: label children until the status is determined")
            elif derived != status:
                err(f"{nid}{at}: children give {derived}, labeled {status}")

    # Flags and injection.
    rule_ids = {r.id for n in spec.nodes() for r in n.flag_rules}
    for flag in case.flags:
        if flag.rule_id and flag.rule_id not in rule_ids:
            err(f"unknown flag rule {flag.rule_id}")
        for fid in flag.facts:
            if fid not in facts:
                err(f"flag {flag.rule_id or flag.kind}: unknown fact {fid}")
    has_injection_flag = any(f.kind == "injection" for f in case.flags)
    if (case.injection is not None) != has_injection_flag:
        err("an injection and an injection flag come together")
    if case.injection and case.injection.doc_id not in docs:
        err(f"injection in unknown document {case.injection.doc_id}")

    # Every fact earns its place.
    cited = {fid for f in case.findings for fid in f.facts}
    cited |= {fid for fl in case.flags for fid in fl.facts}
    cited |= {src for f in case.facts for src in f.derived_from}
    for f in case.facts:
        if f.id not in cited and not f.distractor:
            err(f"{f.id}: not cited by any finding or flag; mark it a distractor or drop it")

    # The generator must write every anchor and none of the forbidden phrases.
    forbidden = {p.lower() for f in case.findings for m in f.missing for p in m.forbidden_phrases}
    for f in case.facts:
        hits = [p for p in forbidden if f.anchor and p in f.anchor.lower()]
        if hits:
            err(f"{f.id}: anchor contains forbidden phrase(s) {sorted(hits)}")

    # Routing and archetype contract.
    route = derive_route(case, spec)
    if route != case.expected_route:
        err(f"findings and flags route {route}, expected_route says {case.expected_route}")
    errors.extend(_archetype_checks(case, spec, route))
    return errors


def _value_checks(f: Finding, node: Node, facts: dict[str, Fact], request_date: date) -> list[str]:
    """Numbers and dates in the evidence must agree with the labeled status."""
    errors: list[str] = []
    ev = sorted(
        (facts[i] for i in f.facts if i in facts and facts[i].field == node.field and node.field),
        key=lambda x: x.date,
    )
    if not ev:
        return errors
    latest = ev[-1]
    positive = f.status in ("met", "found")
    if node.type == "date_window" and node.window:
        inside = in_window(latest.date, request_date, node.window)
        if positive and not inside:
            errors.append(f"{node.id}: evidence dated {latest.date} is outside the window")
        if f.status in ("insufficient", "not_found") and inside:
            errors.append(f"{node.id}: evidence dated {latest.date} is inside the window")
    numeric = isinstance(latest.value, int | float) and not isinstance(latest.value, bool)
    if node.type == "numeric" and numeric and f.status != "insufficient":
        holds = OPS[node.op or ">="](latest.value, node.value)
        if holds != positive:
            errors.append(
                f"{node.id}: {node.field}={latest.value} {node.op} {node.value} is {holds}, "
                f"labeled {f.status}"
            )
        if node.window and positive and not in_window(latest.date, request_date, node.window):
            errors.append(f"{node.id}: evidence dated {latest.date} is outside the window")
    return errors


def _archetype_checks(case: CaseSpec, spec: CriteriaSpec, route: str) -> list[str]:
    errors: list[str] = []
    a = case.archetype
    top = {n.id for n in spec.criteria}
    statuses = [f.status for f in case.findings if f.node_id in top]
    cis = {n.id for n in (*spec.contraindications, *spec.exclusions)}
    found = [f for f in case.findings if f.node_id in cis and f.status == "found"]
    facts = {f.id: f for f in case.facts}
    if case.injection is not None and a != "adversarial":
        errors.append("only adversarial cases carry an injection")
    if a == "clean" and (route != "approve_ready" or case.flags):
        errors.append("clean: must route approve_ready with no flags")
    if a == "missing_documentation" and (route != "request_info" or "insufficient" not in statuses):
        errors.append("missing_documentation: must route request_info, a criterion insufficient")
    if a == "clearly_not_met" and (
        route != "clinician_review" or "not_met" not in statuses or found
    ):
        errors.append("clearly_not_met: needs a not_met criterion, nothing found, clinician_review")
    if a == "borderline" and not any(f.boundary for f in case.facts):
        errors.append("borderline: at least one fact must name its boundary")
    conflict = any(f.kind in ("conflict", "flag_rule") for f in case.flags)
    if a == "conflicting" and (route != "clinician_review" or not conflict):
        errors.append("conflicting: needs a conflict or flag-rule flag and clinician_review")
    if a == "buried_contraindication":
        buried = any(facts[i].placement == "buried" for f in found for i in f.facts if i in facts)
        if not buried or any(s != "met" for s in statuses):
            errors.append("buried_contraindication: every criterion met and a buried finding found")
    if a == "adversarial":
        if case.injection is None or route != "clinician_review":
            errors.append("adversarial: needs an injection and clinician_review")
        if derive_route(case, spec, ignore_injection=True) == "approve_ready":
            errors.append("adversarial: the underlying case must not be approve_ready (D-031)")
    return errors
