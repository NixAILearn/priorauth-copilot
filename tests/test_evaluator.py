"""Evaluator rules on one real case with edited evidence (D-029, D-046, D-047)."""

import copy
import json

from oracle import CASES, oracle_output

from priorauth.evaluator import evaluate
from priorauth.extractor import verify
from priorauth.intake import load_case
from priorauth.schemas import ExtractionOutput

CASE = "CASE-021-01"  # clean HGNS case, request date 2026-10-15


def run(edit=None):
    out = oracle_output(CASE)
    if edit:
        out = copy.deepcopy(out)
        edit(out)
    case = load_case(CASES / CASE)
    ev = evaluate(case, verify(case, ExtractionOutput.model_validate(out)))
    return ev, {(f.node_id, f.unit_id): f for f in ev.findings}


def test_clean_case_meets_every_criterion():
    ev, f = run()
    assert all(f[(n, None)].status == "met" for n in ("021-C1", "021-C2", "021-C3", "021-C6"))
    assert ev.flags == []


def test_a_failing_value_inside_the_window_is_not_met():
    def edit(out):
        for v in out["values"]:
            if v["field"] == "ahi":
                v["value"], v["quote"] = "68", v["quote"]

    # 68 is not in the quote, so the value is rejected rather than trusted
    _, f = run(edit)
    assert f[("021-C3b", None)].status == "insufficient"


def test_evidence_only_outside_the_window_is_insufficient():
    def edit(out):
        for v in out["values"]:
            if v["field"] == "bmi_recorded":
                v["observed_on"] = "2025-01-10"

    _, f = run(edit)
    assert f[("021-C2", None)].status == "insufficient"
    assert "outside" in f[("021-C2", None)].note


def test_disagreeing_values_on_the_latest_date_raise_a_conflict():
    def edit(out):
        bmis = [v for v in out["values"] if v["field"] == "bmi_recorded"]
        twin = dict(
            bmis[0], record="other", value="31.6", quote=bmis[1]["quote"], doc_id=bmis[1]["doc_id"]
        )
        out["values"].append(twin)

    ev, _ = run(edit)
    assert [fl.kind for fl in ev.flags] == ["conflict"]


def test_contraindications_are_never_insufficient():
    ev, _ = run(lambda out: out.update(facts=[]))
    statuses = {f.status for f in ev.findings if "-CI" in f.node_id or "-EX" in f.node_id}
    assert statuses <= {"found", "not_found"}


def test_every_finding_carries_its_section():
    ev, _ = run()
    assert all(f.section for f in ev.findings)
    assert json.dumps([f.model_dump(mode="json") for f in ev.findings])
