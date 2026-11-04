"""Reviewer app logic (D-069, D-070, D-072): demo clock, checklist gating, safe highlighting."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from priorauth import reviewdesk as rd
from priorauth.intake import load_case
from priorauth.quotes import quote_in
from priorauth.schemas import Route
from priorauth.snapshot import SNAPSHOTS, load

CASES = Path(__file__).resolve().parents[1] / "data" / "cases"
CLOCK = datetime(2026, 11, 4, 12, tzinfo=UTC)


@pytest.fixture(scope="module")
def oracle():
    return load(SNAPSHOTS / "oracle.jsonl")


def test_demo_clock_keeps_order_and_fits_nine_days():
    received = {
        "A": datetime(2026, 7, 1, 9, tzinfo=UTC),
        "B": datetime(2026, 9, 1, 9, tzinfo=UTC),
        "C": datetime(2026, 11, 1, 9, tzinfo=UTC),
    }
    out = rd.rebased_arrivals(received, CLOCK)
    assert out["C"] == CLOCK - timedelta(hours=2)
    assert out["A"] == CLOCK - timedelta(days=9)
    assert out["A"] < out["B"] < out["C"]


def test_sla_and_remaining_format():
    arrival = CLOCK - timedelta(days=8)
    assert rd.sla_due(arrival, "standard") - CLOCK == timedelta(days=-1)
    assert rd.sla_due(arrival, "expedited") == arrival + timedelta(hours=72)
    assert rd.fmt_remaining(timedelta(days=-1, hours=-3)) == "-1d 3h"
    assert rd.fmt_remaining(timedelta(minutes=95)) == "1h 35m"


def test_every_verified_citation_in_every_case_is_located(oracle):
    """The highlighter finds what the quote check accepted, across all 60 cases."""
    misses = []
    for cid, c in oracle.cases.items():
        docs = load_case(CASES / cid).documents
        for doc_id, cites in rd.evidence_by_doc(c.rec).items():
            for e in cites:
                if e.verified and quote_in(docs, doc_id, e.quote):
                    if rd.locate(docs[doc_id], e.quote) is None:
                        misses.append((cid, doc_id, e.quote))
    assert not misses, misses[:5]


def test_locate_handles_table_rows_asterisks_and_capitals():
    doc = "| Location | right plantar first metatarsal head |\n**BMI:** 31.2 kg/m2\nand then it"
    s, e = rd.locate(doc, "Location: right plantar first metatarsal head")
    assert doc[s:e] == "Location | right plantar first metatarsal head"
    s, e = rd.locate(doc, "BMI: 31.2 kg/m2")
    assert doc[s:e].endswith("31.2 kg/m2")
    assert rd.locate(doc, "And then it") is not None
    assert rd.locate(doc, "BMI 34.0") is None


def test_document_text_is_escaped_inside_and_outside_marks():
    doc = 'Note <script>alert(1)</script> and <a href="x">link</a> pt stable'
    html, missing = rd.highlight(doc, [rd.Mark("<script>alert(1)</script>", "injection")])
    assert not missing
    assert "<script>" not in html and "<a " not in html
    assert '<mark class="injection">&lt;script&gt;' in html


def test_markdown_escape_blocks_links_and_html():
    out = rd.md_escape("[click](https://e.example) ![i](x) <b>x</b> **bold**")
    assert "](" not in out.replace("\\]\\(", "")
    assert "<b>" not in out and "**" not in out


def test_clean_case_needs_no_review_and_flags_always_do(oracle):
    rec = oracle.cases["CASE-021-01"].rec
    case = load_case(CASES / "CASE-021-01")
    rows = rd.checklist(case.spec, rec, case.unit_ids)
    assert rec.route == Route.APPROVE_READY
    assert rd.pending_reviews(rows, rec.flags, rd.ReviewState()) == []

    rec = oracle.cases["CASE-021-20"].rec  # adversarial: injection flag plus 3.4 insufficient
    case = load_case(CASES / "CASE-021-20")
    rows = rd.checklist(case.spec, rec, case.unit_ids)
    todo = rd.pending_reviews(rows, rec.flags, rd.ReviewState())
    assert "flag:0" in todo and any(k.startswith("021-C4@") for k in todo)
    done = rd.ReviewState(reviewed=set(todo))
    assert rd.pending_reviews(rows, rec.flags, done) == []


def test_only_top_level_rows_gate_and_every_unit_is_listed(oracle):
    """A met any-of keeps its unused branches not met; those never block the reviewer."""
    rec = oracle.cases["CASE-034-02"].rec
    case = load_case(CASES / "CASE-034-02")
    rows = rd.checklist(case.spec, rec, case.unit_ids)
    assert any(not r.top and r.status == "not_met" for r in rows)
    assert rd.pending_reviews(rows, rec.flags, rd.ReviewState()) == []
    per_unit = [r for r in rows if r.node.per == "target_ulcer"]
    assert {r.unit_id for r in per_unit} == set(case.unit_ids)


def test_every_finding_has_a_checklist_row(oracle):
    for cid, c in oracle.cases.items():
        case = load_case(CASES / cid)
        keys = {(r.node.id, r.unit_id) for r in rd.checklist(case.spec, c.rec, case.unit_ids)}
        assert {(f.node_id, f.unit_id) for f in c.rec.findings} <= keys, cid


def test_disagreeing_with_the_route_needs_a_reason():
    assert not rd.action_needs_reason(Route.APPROVE_READY, "approve")
    assert rd.action_needs_reason(Route.CLINICIAN_REVIEW, "approve")
    assert rd.action_needs_reason(Route.REQUEST_INFO, "refer_md")


def test_no_deny_action_anywhere():
    actions = {*rd.NURSE_ACTIONS, *rd.MD_ACTIONS, *rd.ACTION_LABEL}
    text = json.dumps([list(actions), list(rd.ACTION_LABEL.values())]).lower()
    assert "deny" not in text and "denial" not in text and "adverse" not in text
