"""Pipeline data shapes: the prior authorization request (D-038) and the pipeline outputs (D-045).

The request is a simplified, PAS-style JSON: enough for intake, the SLA clock and the policy
lookup. It carries Northwind procedure codes and ICD-10-CM diagnoses only; there are no CPT,
CDT or UB-04 fields.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SLA = {"expedited": timedelta(hours=72), "standard": timedelta(days=7)}  # CMS-0057-F clocks


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Member(Strict):
    synthetic_id: str = Field(pattern=r"^SYN-\d{4}$")
    birth_date: date
    sex: Literal["female", "male"]


class Provider(Strict):
    name: str
    npi: str = Field(pattern=r"^9\d{9}$")  # synthetic: issued NPIs start with 1 or 2 (D-040)
    specialty: str
    organization: str


class TargetUlcerRequest(Strict):
    id: str
    laterality: Literal["right", "left"]
    site: str
    diagnosis: str
    applications_planned: int


class Service(Strict):
    code: str = Field(pattern=r"^NHP-P-\d{4}$")
    description: str
    side: Literal["right", "left"] | None = None
    target_ulcers: list[TargetUlcerRequest] = []
    units: int = 1


class Diagnosis(Strict):
    code: str
    role: Literal["primary", "secondary"]


class PriorAuthRequest(Strict):
    request_schema_version: Literal["1.0"]
    request_id: str
    received_at: datetime
    review_type: Literal["standard", "expedited"]
    sla_due_at: datetime
    member: Member
    requesting_provider: Provider
    service: Service
    diagnoses: list[Diagnosis] = Field(min_length=1)
    attachments: list[str]  # document IDs sent with the request

    @model_validator(mode="after")
    def _sla_matches_review_type(self) -> PriorAuthRequest:
        if self.sla_due_at - self.received_at != SLA[self.review_type]:
            raise ValueError("sla_due_at must be received_at plus the review type's SLA")
        if sum(d.role == "primary" for d in self.diagnoses) != 1:
            raise ValueError("exactly one primary diagnosis")
        return self


# ---------------------------------------------------------------------------------------------
# Pipeline shapes (week 3, D-045). The router can only return a Route: there is no deny value.


class Route(StrEnum):
    """The only outcomes the copilot can recommend. Every one lands in front of a person."""

    APPROVE_READY = "approve_ready"
    REQUEST_INFO = "request_info"
    CLINICIAN_REVIEW = "clinician_review"


ROUTE_SEVERITY = {Route.APPROVE_READY: 0, Route.REQUEST_INFO: 1, Route.CLINICIAN_REVIEW: 2}

Status = Literal["met", "not_met", "insufficient", "found", "not_found"]
Confidence = Literal["high", "low"]
FlagKind = Literal[
    "flag_rule", "conflict", "injection", "out_of_scope", "low_confidence", "model_error"
]


class Quote(Strict):
    """A document ID plus a quote the model says appears verbatim in it."""

    doc_id: str
    quote: str


# What the model returns (validated before any of it is used). Values are strings so one
# schema works on every backend; code parses them per the spec's field type.


class ExtractedValue(Strict):
    field: str
    unit_id: str | None
    value: str
    unit: str | None
    observed_on: str | None  # ISO date the value was observed or measured
    period_start: str | None  # usage reports and courses of care
    period_end: str | None
    record: str  # values from the same test, measurement or report share a record
    doc_id: str
    quote: str


class FactAssessment(Strict):
    node_id: str
    unit_id: str | None
    status: Status
    confidence: Confidence
    citations: list[Quote]
    rationale: str


class FlagClaim(Strict):
    rule_id: str
    unit_id: str | None
    citations: list[Quote]
    rationale: str


class InjectionClaim(Strict):
    doc_id: str
    quote: str


class ExtractionOutput(Strict):
    values: list[ExtractedValue]
    facts: list[FactAssessment]
    flag_rules: list[FlagClaim]
    injections: list[InjectionClaim]


# What the pipeline produces.


class Evidence(Strict):
    doc_id: str
    quote: str
    verified: bool


class Finding(Strict):
    node_id: str
    unit_id: str | None = None
    section: str
    status: Status
    source: Literal["code", "model", "group", "none"]
    value: str | None = None  # the value code compared, e.g. "31.2 kg/m2 on 2026-09-20"
    citations: list[Evidence] = []
    note: str = ""


class Flag(Strict):
    kind: FlagKind
    route: Route
    rule_id: str | None = None
    unit_id: str | None = None
    detail: str
    citations: list[Evidence] = []


class MissingDoc(Strict):
    """One line of the request-for-information letter."""

    node_id: str
    unit_id: str | None
    section: str
    doc_item: str
    name: str
    must_show: str


class ModelCall(Strict):
    backend: str
    model: str
    role: Literal["extract", "hard"]
    attempt: int
    ok: bool
    input_tokens: int | None = None
    output_tokens: int | None = None
    cache_read_tokens: int | None = None
    latency_s: float
    error: str | None = None


class Recommendation(Strict):
    """The copilot's output for one case. A person makes every determination."""

    case_id: str
    request_id: str
    policy_id: str
    policy_version: str
    route: Route
    reasons: list[str]
    findings: list[Finding]
    flags: list[Flag]
    missing: list[MissingDoc]
    model_calls: list[ModelCall]
    created_at: datetime
