"""All 60 committed cases through the real pipeline with a perfect extractor (D-050).

The fake model returns exactly the ground truth, so any miss here is a bug in intake, quote
checks, derivations, evaluation or routing, not in a model.
"""

import json

import pytest
from oracle import CASES, oracle_output

from priorauth.audit import AuditLog
from priorauth.backends import FakeClient
from priorauth.pipeline import review_case

CASE_IDS = sorted(p.name for p in CASES.glob("CASE-*"))
# Known gap (D-050): a note saying a test was not performed has no extractor slot yet.
KNOWN_LEAF_GAPS = {("CASE-021-10", "021-C6a.2-i")}


def _run(case_id, audit=None):
    client = FakeClient([json.dumps(oracle_output(case_id))], hard_model=None)
    return review_case(CASES / case_id, client, audit)


def test_there_are_60_cases():
    assert len(CASE_IDS) == 60


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_route_and_statuses_match_label(case_id):
    label = json.loads((CASES / case_id / "label.json").read_text(encoding="utf-8"))
    rec = _run(case_id)
    assert rec.route.value == label["expected_route"], rec.reasons
    got = {(f.node_id, f.unit_id): f.status for f in rec.findings}
    for x in label["findings"]:
        if (case_id, x["node_id"]) in KNOWN_LEAF_GAPS:
            continue
        assert got.get((x["node_id"], x["unit_id"])) == x["status"], x["node_id"]
    if label["archetype"] == "clean":
        assert rec.flags == []


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_letter_names_every_labeled_gap(case_id):
    label = json.loads((CASES / case_id / "label.json").read_text(encoding="utf-8"))
    if label["expected_route"] != "request_info":
        return
    expected = {(m["doc_item"], x["unit_id"]) for x in label["findings"] for m in x["missing"]}
    got = {(m.doc_item, m.unit_id) for m in _run(case_id).missing}
    assert got == expected


def test_audit_records_each_run():
    log = AuditLog()
    _run("CASE-021-01", log)
    _run("CASE-034-20", log)
    rows = log.runs()
    assert [r["route"] for r in rows] == ["approve_ready", "clinician_review"]
    n_flags = log.db.execute("SELECT count(*) FROM flags WHERE kind='injection'").fetchone()[0]
    assert n_flags == 1
