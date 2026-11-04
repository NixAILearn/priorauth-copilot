"""Letter drafts (D-071): specific items, no adverse determination letter."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pytest

from priorauth import letters
from priorauth.intake import load_case
from priorauth.schemas import Route
from priorauth.snapshot import SNAPSHOTS, load

CASES = Path(__file__).resolve().parents[1] / "data" / "cases"
TODAY = date(2026, 11, 4)
DENIAL = re.compile(r"\b(denied|denial|denies|adverse determination is)\b", re.I)


@pytest.fixture(scope="module")
def oracle():
    return load(SNAPSHOTS / "oracle.jsonl")


def _case(cid):
    c = load_case(CASES / cid)
    return c.request, c.spec


def test_request_info_letter_names_every_missing_item(oracle):
    n = 0
    for cid, c in oracle.cases.items():
        if c.rec.route != Route.REQUEST_INFO:
            continue
        req, spec = _case(cid)
        text = letters.request_info_letter(c.rec, req, spec, TODAY)
        for m in c.rec.missing:
            assert f"Policy section: {m.section}" in text
            assert m.name in text and m.must_show in text
        assert "This is not a decision on the request" in text
        assert not DENIAL.search(text)
        n += 1
    assert n >= 10


def test_request_info_letter_needs_missing_items(oracle):
    rec = oracle.cases["CASE-021-01"].rec
    req, spec = _case("CASE-021-01")
    with pytest.raises(ValueError):
        letters.request_info_letter(rec, req, spec, TODAY)


def test_brief_lists_every_uncleared_criterion_and_flag(oracle):
    for cid, c in oracle.cases.items():
        if c.rec.route != Route.CLINICIAN_REVIEW:
            continue
        req, spec = _case(cid)
        text = letters.md_brief(c.rec, req, spec, TODAY)
        tops = {n.id for n in (*spec.criteria, *spec.contraindications, *spec.exclusions)}
        for f in c.rec.findings:
            if f.node_id in tops and f.status in ("not_met", "insufficient", "found"):
                assert f"- {f.section}" in text, (cid, f.section)
        for fl in c.rec.flags:
            assert fl.detail in text
        assert not DENIAL.search(text), cid


def test_approval_notice_lists_met_criteria(oracle):
    rec = oracle.cases["CASE-021-01"].rec
    req, spec = _case("CASE-021-01")
    text = letters.approval_notice(rec, req, spec, "Priya N., RN", TODAY)
    for n in spec.criteria:
        assert f"- {n.section}: {n.summary}" in text
    assert "Priya N., RN" in text


def test_draft_matches_route(oracle):
    for cid, c in oracle.cases.items():
        req, spec = _case(cid)
        d = letters.draft_for(c.rec, req, spec, TODAY)
        if c.rec.route == Route.APPROVE_READY:
            assert d is None
        elif c.rec.route == Route.CLINICIAN_REVIEW:
            assert d[0] == "Medical director brief"


def test_no_adverse_letter_function_exists():
    names = [n.lower() for n in dir(letters)]
    assert not [n for n in names if "deny" in n or "denial" in n or "adverse" in n]
