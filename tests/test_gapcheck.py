"""Provider gap check (PRD R8, D-077): provider wording, no flag details, no denial language."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from priorauth import gapcheck
from priorauth.intake import load_case
from priorauth.schemas import Route
from priorauth.snapshot import SNAPSHOTS, load

CASES = Path(__file__).resolve().parents[1] / "data" / "cases"
DENIAL = re.compile(r"\b(deny|denied|denial|denies|reject)", re.I)
# "injection" alone is clinical (knee steroid injections); match the flag wording instead.
REVIEWER_ONLY = re.compile(
    r"possible injection|aimed at an AI|low.confidence|flag|model error", re.I
)


@pytest.fixture(scope="module")
def oracle():
    return load(SNAPSHOTS / "oracle.jsonl")


def _report(snap, cid):
    c = load_case(CASES / cid)
    return gapcheck.gap_check(snap.cases[cid].rec, c.request, c.spec)


def test_every_case_has_provider_wording_without_denial_or_flag_details(oracle):
    for cid in oracle.cases:
        r = _report(oracle, cid)
        text = " ".join([r.headline, r.outlook, r.checklist()])
        text = text.replace("does not apply", "")  # exclusion wording, not a denial
        assert not DENIAL.search(text), (cid, text)
        assert not REVIEWER_ONLY.search(text), (cid, text)


def test_request_info_lists_every_missing_item(oracle):
    n = 0
    for cid, c in oracle.cases.items():
        if c.rec.route != Route.REQUEST_INFO:
            continue
        items = {s.item for s in _report(oracle, cid).to_send}
        assert {m.doc_item for m in c.rec.missing} <= items, cid
        n += 1
    assert n >= 10


def test_offloading_gap_demo_case(oracle):
    r = _report(oracle, "CASE-034-07")
    assert r.route == Route.REQUEST_INFO
    assert any("ffloading" in s.must_show or "ffloading" in s.name for s in r.to_send)
    assert any(g.section.startswith("3.10") for g in r.gaps)


def test_clean_case_has_nothing_to_add(oracle):
    r = _report(oracle, "CASE-021-01")
    assert r.route == Route.APPROVE_READY
    assert not r.gaps and not r.to_send
    assert "Nothing to add" in r.checklist()


def test_injection_case_shows_no_flag_detail(oracle):
    r = _report(oracle, "CASE-021-20")
    assert r.route == Route.CLINICIAN_REVIEW
    assert "physician reviewer" in r.outlook
    assert not REVIEWER_ONLY.search(r.checklist())
