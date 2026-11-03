"""The safety guarantees that hold by construction: three routes, no denial path (kickoff 8)."""

import itertools
import sqlite3

import pytest

from priorauth.audit import AuditLog
from priorauth.evaluator import Evaluation
from priorauth.router import route_case
from priorauth.schemas import ROUTE_SEVERITY, Finding, Flag, Recommendation, Route
from priorauth.spec import load_spec

DENY_WORDS = ("deny", "denied", "denial", "reject", "decline", "not_covered", "adverse")


def test_route_enum_has_exactly_three_outcomes_and_no_denial():
    assert {r.value for r in Route} == {"approve_ready", "request_info", "clinician_review"}
    for r in Route:
        assert not any(w in r.value or w in r.name.lower() for w in DENY_WORDS)


def test_recommendation_route_rejects_a_denial_value():
    fields = Recommendation.model_fields["route"]
    assert fields.annotation is Route
    with pytest.raises(ValueError):
        Route("deny")


def test_audit_table_refuses_a_denial_route():
    log = AuditLog()
    with pytest.raises(sqlite3.IntegrityError):
        log.db.execute(
            "INSERT INTO runs (case_id, request_id, policy_id, policy_version,"
            " policy_source_sha256, prompt_version, backend, official, route,"
            " recommendation_json, created_at)"
            " VALUES ('c', 'r', 'p', '1', 'h', 'v', 'b', 0, 'deny', '{}', 't')"
        )


def test_every_severity_is_defined():
    assert set(ROUTE_SEVERITY) == set(Route)


SPEC = load_spec("policies/specs/NHP-MP-047.json")


def _eval(top_status: dict[str, str], found: set[str] = frozenset()) -> Evaluation:
    ev = Evaluation()
    for n in SPEC.criteria:
        ev.findings.append(
            Finding(
                node_id=n.id, section=n.section, status=top_status.get(n.id, "met"), source="code"
            )
        )
    for n in (*SPEC.contraindications, *SPEC.exclusions):
        ev.findings.append(
            Finding(
                node_id=n.id,
                section=n.section,
                status="found" if n.id in found else "not_found",
                source="model",
            )
        )
    return ev


def test_router_rules():
    assert route_case(SPEC, [], _eval({}), [])[0] == Route.APPROVE_READY
    assert route_case(SPEC, [], _eval({"047-C3": "insufficient"}), [])[0] == Route.REQUEST_INFO
    both = _eval({"047-C3": "insufficient", "047-C5": "not_met"})
    assert route_case(SPEC, [], both, [])[0] == Route.CLINICIAN_REVIEW
    assert route_case(SPEC, [], _eval({}, {"047-CI01"}), [])[0] == Route.CLINICIAN_REVIEW
    flag = Flag(kind="injection", route=Route.CLINICIAN_REVIEW, detail="x")
    assert route_case(SPEC, [], _eval({}), [flag])[0] == Route.CLINICIAN_REVIEW


def test_unevaluated_criterion_never_passes():
    ev = _eval({})
    ev.findings = ev.findings[1:]  # drop the first criterion's finding
    assert route_case(SPEC, [], ev, [])[0] == Route.CLINICIAN_REVIEW


@pytest.mark.parametrize(
    "statuses",
    list(itertools.product(["met", "not_met", "insufficient"], repeat=3)),
)
def test_approve_ready_only_when_everything_is_met(statuses):
    ids = [n.id for n in SPEC.criteria[:3]]
    route, reasons = route_case(SPEC, [], _eval(dict(zip(ids, statuses, strict=True))), [])
    assert route in Route
    assert (route == Route.APPROVE_READY) == all(s == "met" for s in statuses)
    assert reasons
