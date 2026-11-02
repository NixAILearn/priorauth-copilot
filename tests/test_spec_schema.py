"""Negative checks for the per-unit, day-window and enum options in the spec schema (D-025)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from priorauth.spec import CriteriaSpec, Window

SPEC_034 = Path(__file__).resolve().parent.parent / "policies" / "specs" / "NHP-MP-034.json"


def raw() -> dict:
    return json.loads(SPEC_034.read_text(encoding="utf-8"))


def test_window_needs_exactly_one_unit() -> None:
    with pytest.raises(ValidationError):
        Window()
    with pytest.raises(ValidationError):
        Window(months=3, days=14)


def test_day_window_needs_matching_rule() -> None:
    d = raw()
    d["rules"]["window_counting"] = "calendar_months"
    with pytest.raises(ValidationError, match="day windows"):
        CriteriaSpec.model_validate(d)


def test_per_ulcer_node_needs_per_ulcer_scope() -> None:
    d = raw()
    d["scope"]["review_unit"] = "request"
    d["scope"]["unit_diagnoses"] = []
    for f in d["fields"]:
        f["per"] = "request"
    with pytest.raises(ValidationError, match="review_unit"):
        CriteriaSpec.model_validate(d)


def test_enum_value_must_exist_on_field() -> None:
    d = raw()
    d["criteria"][-2]["children"][0]["children"][0]["equals"] = "ischemic"
    with pytest.raises(ValidationError, match="equals"):
        CriteriaSpec.model_validate(d)
