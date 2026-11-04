"""The eval runner and scorer (week 4, D-051 to D-055).

The oracle run proves the harness scores a perfect pipeline as perfect. The rest forge one
failure at a time into an otherwise perfect run and check that the right metric moves, so a
scorer bug cannot hide a safety miss.
"""

import json
from collections import Counter

import pytest

from evals import run_eval
from evals.run_eval import main, oracle_factory, run_one, select_cases
from evals.scoring import age_band, score
from priorauth.backends import FakeClient, ModelError
from priorauth.schemas import Evidence, Route


@pytest.fixture(scope="module")
def oracle():
    make, _ = oracle_factory()
    return make


@pytest.fixture(scope="module")
def smoke(oracle):
    return [run_one(c, oracle) for c in select_cases("smoke")]


def test_smoke_set_is_the_metrics_mix():
    ids = select_cases("smoke")
    assert len(ids) == 10
    archetypes = Counter(
        json.loads((run_eval.CASES / c / "label.json").read_text())["archetype"] for c in ids
    )
    assert archetypes == {
        "clean": 3,
        "missing_documentation": 2,
        "clearly_not_met": 1,
        "borderline": 1,
        "conflicting": 1,
        "buried_contraindication": 1,
        "adversarial": 1,
    }
    assert all(
        json.loads((run_eval.CASES / c / "label.json").read_text())["split"] == "dev" for c in ids
    )


def test_sets_partition_the_cases():
    dev, test = set(select_cases("dev")), set(select_cases("test"))
    assert len(dev) == 40 and len(test) == 20 and not dev & test
    assert dev | test == set(select_cases("all"))


def test_oracle_smoke_is_perfect(smoke):
    s = score(smoke)
    assert s.gate_passed
    assert s.false_approve_upper_95 == pytest.approx(3 / 6)  # 4 of the 10 are labeled approve-ready
    assert s.injection_resistance == 1.0
    assert s.criterion_agreement == 1.0
    assert s.routing_accuracy == 1.0
    assert s.missing_doc_recall == 1.0 and s.missing_doc_precision == 1.0
    assert s.citation_precision_verbatim == 1.0
    assert s.dangerous_cell == 0


def _swap(results, case_id, **update):
    out = []
    for r in results:
        if r.case_id == case_id:
            r = type(r)(**{**r.__dict__, "rec": r.rec.model_copy(update=update)})
        out.append(r)
    return out


def test_false_approve_ready_fails_the_gate(smoke):
    s = score(_swap(smoke, "CASE-047-12", route=Route.APPROVE_READY))
    assert s.false_approve_ready == ["CASE-047-12"]
    assert not s.gate_passed
    assert s.false_approve_upper_95 is None  # no bound once a miss is seen


def test_a_denial_value_is_counted(smoke):
    r = next(x for x in smoke if x.case_id == "CASE-047-12")
    forged = r.rec.model_construct(**{**r.rec.__dict__, "route": "deny"})  # bypasses the enum
    s = score([type(r)(**{**r.__dict__, "rec": forged})])
    assert s.auto_denials == ["CASE-047-12"] and not s.gate_passed


def test_injection_needs_route_and_flag(smoke):
    r = next(x for x in smoke if x.case_id == "CASE-021-20")
    unflagged = [f for f in r.rec.flags if f.kind != "injection"]
    s = score(_swap(smoke, "CASE-021-20", flags=unflagged))
    assert s.injection_failed == ["CASE-021-20"]  # still clinician review, but no flag
    assert not s.gate_passed


def test_a_wrong_met_lands_in_the_dangerous_cell(smoke):
    r = next(x for x in smoke if x.case_id == "CASE-047-12")
    top = {n.id for n in r.spec.criteria}
    bad = next(f for f in r.rec.findings if f.status == "not_met" and f.node_id in top)
    findings = [f.model_copy(update={"status": "met"}) if f is bad else f for f in r.rec.findings]
    s = score(_swap(smoke, "CASE-047-12", findings=findings))
    assert s.criterion_confusion[("not_met", "met")] == 1
    assert s.dangerous_cell == 1
    assert s.criterion_hits == s.criterion_pairs - 1


def test_a_dropped_finding_is_a_miss(smoke):
    r = next(x for x in smoke if x.case_id == "CASE-021-01")
    findings = [f for f in r.rec.findings if f.node_id != "021-C2"]
    s = score(_swap(smoke, "CASE-021-01", findings=findings))
    assert s.criterion_confusion[("met", "missing")] == 1


def test_missing_doc_recall_and_precision(smoke):
    r = next(x for x in smoke if x.case_id == "CASE-021-07")
    assert r.rec.missing
    extra = r.rec.missing[0].model_copy(update={"doc_item": "6.1"})
    s = score(_swap(smoke, "CASE-021-07", missing=[extra]))
    assert s.missing_hit == s.missing_labeled - 1
    assert s.missing_named_correct == s.missing_named - 1
    assert s.missing_extras == [("CASE-021-07", "6.1", None)]


def test_a_paraphrased_citation_is_caught(smoke):
    r = next(x for x in smoke if x.case_id == "CASE-021-01")
    f0 = next(f for f in r.rec.findings if f.source != "group" and f.citations)
    fake = Evidence(
        doc_id=f0.citations[0].doc_id, quote="The patient is a great candidate.", verified=True
    )  # the scorer rechecks; it does not trust this flag
    findings = [
        f.model_copy(update={"citations": [*f.citations, fake]}) if f is f0 else f
        for f in r.rec.findings
    ]
    s = score(_swap(smoke, "CASE-021-01", findings=findings))
    assert s.citations_verbatim == s.citations - 1
    assert s.citation_failures[0][0] == "CASE-021-01"


def test_model_error_routes_to_review_and_is_reported():
    r = run_one("CASE-021-01", lambda _c: FakeClient([ModelError("down")], hard_model=None))
    assert r.route == Route.CLINICIAN_REVIEW
    assert run_eval.model_error_cases([r]) == ["CASE-021-01"]


def test_age_band():
    from datetime import date

    assert age_band(date(1958, 7, 22), date(2026, 7, 21)) == "65-74"
    assert age_band(date(1958, 7, 22), date(2023, 7, 21)) == "under 65"
    assert age_band(date(1940, 1, 1), date(2026, 1, 1)) == "85+"


def test_cli_smoke_gate_passes(capsys):
    assert main(["--set", "smoke", "--backend", "oracle", "--gate-only", "--no-write"]) == 0
    out = capsys.readouterr().out
    assert "safety gate HOLDS" in out and "Harness check, not a scorecard result" in out
    assert "## Quality" not in out


def test_cli_exit_code_on_gate_failure(monkeypatch, smoke):
    forged = _swap(smoke, "CASE-034-17", route=Route.APPROVE_READY)
    monkeypatch.setattr(run_eval, "run_cases", lambda *a, **k: forged)
    assert main(["--set", "smoke", "--backend", "oracle", "--no-write"]) == 1


def test_cli_all_model_errors_is_unscoreable(monkeypatch):
    def broken(case_ids, make, workers=1, checkpoint=None, resume=None):
        return [
            run_one(c, lambda _c: FakeClient([ModelError("x")], hard_model=None)) for c in case_ids
        ]

    monkeypatch.setattr(run_eval, "run_cases", broken)
    assert main(["--cases", "CASE-021-01", "CASE-047-12", "--backend", "oracle", "--no-write"]) == 2


def test_cli_anthropic_without_key(monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert main(["--set", "smoke", "--backend", "anthropic", "--no-write"]) == 2
    assert "ANTHROPIC_API_KEY" in capsys.readouterr().err


def test_cli_writes_dated_report(tmp_path):
    assert main(["--cases", "CASE-021-01", "--backend", "oracle", "--out", str(tmp_path)]) == 0
    md = list(tmp_path.glob("*-custom-oracle.md"))
    js = list(tmp_path.glob("*-custom-oracle.json"))
    assert len(md) == 1 and len(js) == 1
    data = json.loads(js[0].read_text())
    assert data["overall"]["gate_passed"] is True
    assert data["cases"][0]["route"] == "approve_ready"


def test_checkpoint_and_resume(tmp_path, oracle):
    ck = tmp_path / "ck.jsonl"
    first = run_eval.run_cases(["CASE-021-01", "CASE-047-12"], oracle, checkpoint=ck)
    assert len(ck.read_text().splitlines()) == 2

    def no_model(_c):
        raise AssertionError("a resumed case must not call the model")

    saved = run_eval.load_checkpoint(ck)
    again = run_eval.run_cases(
        ["CASE-021-01", "CASE-047-12"], no_model, checkpoint=ck, resume=saved
    )
    assert [r.route for r in again] == [r.route for r in first]
    assert len(ck.read_text().splitlines()) == 2  # resumed cases are not appended twice
    assert score(again).criterion_agreement == 1.0
