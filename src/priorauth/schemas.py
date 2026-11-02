"""Pipeline data shapes. v0.1 holds the prior authorization request (D-038).

The request is a simplified, PAS-style JSON: enough for intake, the SLA clock and the policy
lookup. It carries Northwind procedure codes and ICD-10-CM diagnoses only; there are no CPT,
CDT or UB-04 fields.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
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
