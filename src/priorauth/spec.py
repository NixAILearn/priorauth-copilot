"""Criteria spec schema: the reviewed JSON form of a Northwind medical policy.

A spec is compiled from policies/source/NHP-MP-###.md, reviewed by a person, and
committed to policies/specs/. The pipeline evaluates requests only against specs,
never against free policy text.

Design rules this schema enforces:
- Every node quotes its policy text verbatim (checked against the source in tests).
- Numeric thresholds use only the four policy operators; code applies them.
- Routes are only "request_info" or "clinician_review". There is no deny value.
- A policy reviewed per unit (e.g. per target ulcer, D-020) marks its per-unit nodes
  and fields; the case routes on its weakest unit.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Op = Literal[">=", ">", "<=", "<"]
NodeType = Literal["numeric", "date_window", "fact", "enum", "all_of", "any_of"]
Unit = Literal["request", "target_ulcer"]
Route = Literal["request_info", "clinician_review"]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Window(Strict):
    """A look-back window, counted per the policy's window rule (D-019, D-022).

    Exactly one of months (calendar months) or days (calendar days) is set.
    """

    months: int | None = Field(default=None, gt=0)
    days: int | None = Field(default=None, gt=0)
    anchor: Literal["request_date"] = "request_date"

    @model_validator(mode="after")
    def _one_unit(self) -> Window:
        if (self.months is None) == (self.days is None):
            raise ValueError("a window sets exactly one of months or days")
        return self


class FlagRule(Strict):
    """A condition that raises a reviewer flag and forces a route, whatever the status."""

    id: str
    when: str
    route: Route


class Node(Strict):
    """One criterion, contraindication or exclusion, or a group of them."""

    id: str
    section: str
    type: NodeType
    policy_text: str
    summary: str
    field: str | None = None
    op: Op | None = None
    value: float | None = None
    equals: str | None = None
    unit: str | None = None
    window: Window | None = None
    select: Literal["most_recent"] | None = None
    per: Unit = "request"
    evidence: str | None = None
    definitions: list[str] = []
    documentation: list[str] = []
    flag_rules: list[FlagRule] = []
    exception: Node | None = None
    children: list[Node] = []

    @model_validator(mode="after")
    def _shape_matches_type(self) -> Node:
        t = self.type
        if t in ("all_of", "any_of"):
            if len(self.children) < 2:
                raise ValueError(f"{self.id}: {t} needs at least 2 children")
            if self.field or self.op:
                raise ValueError(f"{self.id}: a group has no field or operator")
        elif self.children:
            raise ValueError(f"{self.id}: only all_of/any_of nodes have children")
        if t == "numeric" and None in (self.field, self.op, self.value, self.unit):
            raise ValueError(f"{self.id}: numeric needs field, op, value and unit")
        if t == "date_window" and (self.field is None or self.window is None):
            raise ValueError(f"{self.id}: date_window needs field and window")
        if t == "enum" and (self.field is None or self.equals is None):
            raise ValueError(f"{self.id}: enum needs field and equals")
        if t != "enum" and self.equals is not None:
            raise ValueError(f"{self.id}: only enum nodes have equals")
        if t == "fact" and not self.evidence:
            raise ValueError(f"{self.id}: fact needs an evidence description")
        return self

    def walk(self) -> Iterator[Node]:
        yield self
        if self.exception:
            yield from self.exception.walk()
        for child in self.children:
            yield from child.walk()


class FieldDef(Strict):
    """A value the extractor returns (evaluator=model) or code derives (evaluator=code)."""

    name: str
    type: Literal["number", "date", "enum", "boolean", "text"]
    unit: str | None = None
    values: list[str] | None = None
    evaluator: Literal["model", "code"]
    per: Unit = "request"
    derived_from: list[str] = []
    description: str


class DocItem(Strict):
    id: str
    name: str
    must_show: str
    supports: list[str]


class Ambiguity(Strict):
    id: str
    sections: list[str]
    issue: str
    readings: list[str] = Field(min_length=2)
    recommended: str
    encoded_as: str


class Scope(Strict):
    service_code: str
    primary_diagnoses: list[str] = Field(min_length=1)
    out_of_scope_route: Route = "clinician_review"
    review_unit: Unit = "request"
    unit_diagnoses: list[str] = []
    unit_routing: Literal["weakest_unit"] = "weakest_unit"

    @model_validator(mode="after")
    def _unit_diagnoses_need_units(self) -> Scope:
        if self.unit_diagnoses and self.review_unit == "request":
            raise ValueError("unit_diagnoses need a review_unit other than request")
        return self


class Rules(Strict):
    window_counting: Literal["calendar_months", "calendar_months_or_days"]
    window_boundary_inclusive: bool
    missing_calendar_day: Literal["last_day_of_month"]
    value_selection: Literal["most_recent"]
    conflict_route: Route
    contraindication_found_route: Route
    exclusion_found_route: Route


class CriteriaSpec(Strict):
    spec_schema_version: Literal["1.0"]
    policy_id: str = Field(pattern=r"^NHP-MP-\d{3}$")
    policy_version: str
    effective_date: date
    source_file: str
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    review_status: Literal["draft", "reviewed"]
    reviewed_by: str | None = None
    reviewed_date: date | None = None
    scope: Scope
    rules: Rules
    fields: list[FieldDef]
    criteria: list[Node]
    contraindications: list[Node]
    exclusions: list[Node]
    documentation: list[DocItem]
    ambiguities: list[Ambiguity]
    source_quote_required: Literal[True]

    @model_validator(mode="after")
    def _review_fields_consistent(self) -> CriteriaSpec:
        reviewed = self.review_status == "reviewed"
        if reviewed != (self.reviewed_by is not None and self.reviewed_date is not None):
            raise ValueError("reviewed_by and reviewed_date are set exactly when reviewed")
        return self

    @model_validator(mode="after")
    def _units_and_enums_consistent(self) -> CriteriaSpec:
        fields = {f.name: f for f in self.fields}
        unit = self.scope.review_unit
        if unit == "request" and any(f.per != "request" for f in self.fields):
            raise ValueError("per-unit fields need a scope.review_unit")
        if self.rules.window_counting == "calendar_months" and any(
            n.window and n.window.days for n in self.nodes()
        ):
            raise ValueError("day windows need window_counting calendar_months_or_days")
        for n in self.nodes():
            if n.per not in ("request", unit):
                raise ValueError(f"{n.id}: per={n.per} but scope.review_unit={unit}")
            if n.type == "enum":
                f = fields.get(n.field or "")
                if f is None or f.type != "enum" or n.equals not in (f.values or []):
                    raise ValueError(f"{n.id}: equals must be a value of enum field {n.field}")
        return self

    def nodes(self) -> Iterator[Node]:
        for top in (*self.criteria, *self.contraindications, *self.exclusions):
            yield from top.walk()


def load_spec(path: str | Path) -> CriteriaSpec:
    return CriteriaSpec.model_validate_json(Path(path).read_text(encoding="utf-8"))
