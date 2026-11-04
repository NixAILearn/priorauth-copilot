"""D-063: a header-line quote for dates, code-decided checks, per-kind statuses, missing docs."""

import copy

from oracle import CASES, oracle_output

from priorauth.backends import FakeClient
from priorauth.evaluator import evaluate
from priorauth.extractor import PER_FIELD_CAP, keyed_schema, kind_of, verify
from priorauth.intake import load_case
from priorauth.pipeline import review_case
from priorauth.schemas import ExtractionOutput, Route


def _run(case_id, edit=None):
    out = copy.deepcopy(oracle_output(case_id))
    if edit:
        edit(out)
    case = load_case(CASES / case_id)
    v = verify(case, ExtractionOutput.model_validate(out))
    return case, v, evaluate(case, v)


def _baseline(out):
    return next(x for x in out["values"] if x["field"] == "baseline_date")


def test_a_date_on_a_header_line_is_accepted_with_a_second_exact_quote():
    def edit(out):
        b = _baseline(out)
        b["quote"] = "Baseline measurement for standard care"  # no date in it
        b["date_quote"] = "Date of visit: 09/08/2026"

    _, v, _ = _run("CASE-034-07", edit)
    (o,) = v.obs[("baseline_date", "U1")]
    assert [e.quote for e in o.evidence()] == [
        "Baseline measurement for standard care",
        "Date of visit: 09/08/2026",
    ]


def test_the_second_date_quote_must_be_exact_same_document_and_show_the_date():
    for dq, doc in (
        ("Date of visit: 09/08/2026", "D05"),  # another document
        ("Date of visit: 09/09/2026", "D04"),  # not in the document
        ("Course: Initial visit", "D04"),  # exact, but no date
        (None, "D04"),
    ):

        def edit(out, dq=dq, doc=doc):
            b = _baseline(out)
            b["quote"], b["doc_id"], b["date_quote"] = (
                "Baseline measurement for standard care",
                doc,
                dq,
            )
            _drop_measurement_dates(out, "D04")  # keep the D-064 fallback out of this test

        _, v, _ = _run("CASE-034-07", edit)
        assert ("baseline_date", "U1") not in v.obs, (dq, doc)


def _drop_measurement_dates(out, doc):
    out["values"] = [
        x for x in out["values"] if not (x["field"] == "measurement_date" and x["doc_id"] == doc)
    ]


def _undated_baseline(out):
    b = _baseline(out)
    b["quote"], b["date_quote"] = "Baseline measurement for standard care", None


def test_an_undated_baseline_takes_the_same_documents_measurement_date():  # D-064
    _, v, _ = _run("CASE-034-07", _undated_baseline)
    (o,) = v.obs[("baseline_date", "U1")]
    assert str(o.value) == "2026-09-08" and len(o.evidence()) == 2
    assert "09/08/2026" in o.evidence()[1].quote or "2026-09-08" in o.evidence()[1].quote


def test_an_undated_baseline_is_rejected_without_one_matching_measurement_date():  # D-064
    def no_dates(out):
        _undated_baseline(out)
        _drop_measurement_dates(out, "D04")

    _, v, _ = _run("CASE-034-07", no_dates)
    assert ("baseline_date", "U1") not in v.obs

    def other_date(out):
        _undated_baseline(out)
        _baseline(out)["value"] = "2026-09-15"  # not the date D04 records

    _, v, _ = _run("CASE-034-07", other_date)
    assert ("baseline_date", "U1") not in v.obs


def test_length_and_width_pair_by_document_and_date_when_labels_differ():  # D-064
    def relabel(out):
        for x in out["values"]:
            if x["field"] in ("wound_length", "wound_width"):
                x["record"] = f"{x['doc_id']}-{x['field']}-{x['observed_on']}"

    _, _, ev = _run("CASE-034-07", relabel)
    _, _, base = _run("CASE-034-07")
    for node in ("034-C5d", "034-C7"):
        assert ev.get(node, "U1").status == base.get(node, "U1").status, node


def test_exclusions_and_contraindications_offer_only_found_or_not_found():
    case = load_case(CASES / "CASE-034-07")
    facts = keyed_schema(case)["properties"]["facts"]["properties"]
    kinds = kind_of(case.spec)
    for node_id, s in facts.items():
        item = s.get("items", s)
        want = (
            ["met", "not_met", "insufficient"]
            if kinds[node_id] == "criterion"
            else ["found", "not_found"]
        )
        assert item["properties"]["status"]["enum"] == want, node_id


def test_cap_leaves_room_for_more_visits():
    assert PER_FIELD_CAP == 8


def _method(out, when, method, doc):
    out["values"].append(
        {
            "field": "measurement_method",
            "unit_id": "U1",
            "value": method,
            "unit": None,
            "observed_on": when,
            "period_start": None,
            "period_end": None,
            "record": f"{doc}-method",
            "doc_id": doc,
            "quote": "Measurement method | Ruler, length x width",
        }
    )


def _claim_method_change(out):
    out["flag_rules"].append(
        {
            "rule_id": "034-C7-F1",
            "unit_id": "U1",
            "citations": [{"doc_id": "D04", "quote": "Measurement method | Ruler, length x width"}],
            "rationale": "method changed",
        }
    )


def test_same_verified_method_overrides_a_model_method_change_claim():
    def edit(out):
        _method(out, "2026-09-08", "ruler", "D04")
        cur = max(x["value"] for x in out["values"] if x["field"] == "measurement_date")
        _method(out, cur, "ruler", "D04")
        _claim_method_change(out)

    _, _, ev = _run("CASE-034-07", edit)
    assert not any(f.rule_id == "034-C7-F1" for f in ev.flags)


def test_without_verified_methods_the_model_claim_stands():
    _, _, ev = _run("CASE-034-07", _claim_method_change)
    assert any(f.rule_id == "034-C7-F1" for f in ev.flags)


def test_knee_side_is_decided_in_code_from_verified_sides():
    def uncited_not_met(out):
        for f in out["facts"]:
            if f["node_id"] == "047-C2":
                f.update(status="not_met", citations=[])

    _, _, ev = _run("CASE-047-12", uncited_not_met)
    c2 = ev.get("047-C2", None)
    assert c2.status == "met" and c2.source == "code" and c2.citations
    assert not any("047-C2" in f.detail for f in ev.flags if f.kind == "low_confidence")

    def says_met(out):
        for f in out["facts"]:
            if f["node_id"] == "047-C2":
                f["status"] = "met"

    _, _, ev = _run("CASE-047-17", says_met)  # D03 names the left knee
    assert ev.get("047-C2", None).status == "not_met"


def test_missing_documents_stay_request_info_only():  # D-063 (D) withdrawn
    import json

    out = copy.deepcopy(oracle_output("CASE-034-07"))
    _claim_method_change(out)  # a verified reviewer flag forces clinician review
    rec = review_case(CASES / "CASE-034-07", FakeClient([json.dumps(out)], hard_model=None))
    assert rec.route == Route.CLINICIAN_REVIEW and rec.missing == []


def _site_claim(quote):
    def edit(out):
        out["flag_rules"].append(
            {
                "rule_id": "034-C4-F1",
                "unit_id": "U1",
                "citations": [{"doc_id": "D04", "quote": quote}],
                "rationale": "sides match",
            }
        )

    return edit


def test_a_site_mismatch_claim_whose_quote_matches_the_request_is_dropped():  # D-064
    _, _, ev = _run("CASE-034-07", _site_claim("Location | right plantar first metatarsal head"))
    assert not any(f.rule_id == "034-C4-F1" for f in ev.flags)


def test_a_real_site_mismatch_still_flags():  # D-064
    _, _, ev = _run("CASE-034-18")  # request says left, notes say right
    assert any(f.rule_id == "034-C4-F1" for f in ev.flags)
    _, _, ev = _run("CASE-034-07", _site_claim("Etiology | Diabetic neuropathic ulcer"))
    assert any(f.rule_id == "034-C4-F1" for f in ev.flags)  # quote shows no side: kept
