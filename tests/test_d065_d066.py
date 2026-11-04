"""D-065 "every note" facts and D-066 claims decided from verified values."""

import copy

from oracle import CASES, oracle_output

from priorauth.evaluator import evaluate
from priorauth.extractor import verify
from priorauth.intake import load_case
from priorauth.schemas import ExtractionOutput


def _run(case_id, edit=None):
    out = copy.deepcopy(oracle_output(case_id))
    if edit:
        edit(out)
    case = load_case(CASES / case_id)
    v = verify(case, ExtractionOutput.model_validate(out))
    return v, evaluate(case, v)


def _fact(out, node_id):
    return next(f for f in out["facts"] if f["node_id"] == node_id)


def test_every_note_fact_met_needs_a_verified_quote_from_each_note():  # D-065
    _, ev = _run("CASE-034-05")  # the oracle cites D04 to D09
    assert ev.get("034-C14b", "U1").status == "met"

    def latest_only(out):
        f = _fact(out, "034-C14b")
        f["citations"] = [c for c in f["citations"] if c["doc_id"] == "D09"]

    _, ev = _run("CASE-034-05", latest_only)
    f = ev.get("034-C14b", "U1")
    assert f.status == "insufficient" and "D04" in f.note and "D08" in f.note


def _rule(value):
    def edit(out):
        for v in out["values"]:
            if v["field"] == "ahi_scoring_rule":
                v["value"] = value
                v["quote"] = "Scoring followed current AASM scoring rules"

    return edit


def _f2_claim(out):
    q = "hypopneas scored using the 4% oxygen desaturation rule"
    out["flag_rules"].append(
        {
            "rule_id": "021-C3-F2",
            "unit_id": None,
            "citations": [{"doc_id": "D01", "quote": q}],
            "rationale": "x",
        }
    )


def test_ahi_rule_flag_is_decided_from_the_verified_scoring_rule():  # D-066
    _, ev = _run("CASE-021-01", _f2_claim)  # verified rule is 4%: the claim is dropped
    assert not any(f.rule_id == "021-C3-F2" for f in ev.flags)

    _, ev = _run("CASE-021-01", _rule("3_percent"))  # no claim at all: code raises it
    assert any(f.rule_id == "021-C3-F2" for f in ev.flags)


def test_ahi_rule_flag_falls_back_to_the_model_when_not_stated():  # D-066
    def edit(out):
        _rule("not_stated")(out)
        _f2_claim(out)

    _, ev = _run("CASE-021-01", edit)
    assert any(f.rule_id == "021-C3-F2" for f in ev.flags)


def _arthroscopy(quote):
    def edit(out):
        out["values"].append(
            {
                "field": "prior_arthroscopy_date",
                "unit_id": None,
                "value": "2026-08-13",
                "unit": None,
                "observed_on": "2026-08-13",
                "period_start": None,
                "period_end": None,
                "record": "x",
                "doc_id": "D01",
                "quote": quote,
                "date_quote": None,
            }
        )

    return edit


def test_an_event_date_quote_must_name_the_event():  # D-066
    case = load_case(CASES / "CASE-047-01")
    line = next(
        ln.strip()
        for ln in case.documents["D01"].splitlines()
        if "08/13/2026" in ln or "2026-08-13" in ln
    )
    assert "arthroscop" not in line.lower()
    v, ev = _run("CASE-047-01", _arthroscopy(line))
    assert ("prior_arthroscopy_date", None) not in v.obs
    assert any(r.reason == "the quote does not name the event" for r in v.rejected)
    assert ev.get("047-EX02", None).status == "not_found"
