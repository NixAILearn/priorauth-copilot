"""Router: approve-ready, request info or clinician review. Nothing else exists (kickoff 6, 8).

Deterministic code, not a prompt. The route can only be a `Route`, and `Route` has no denial
value; a test checks both. Written separately from the label oracle in case_spec.py (D-030).

1. Approve-ready only if every top-level criterion is met, nothing is found, and no flag.
2. Clinician review if a criterion is not met, a contraindication or exclusion is found,
   evidence conflicts, or the case is flagged (flag-rule routes come from the spec).
3. Request info if the only problems are criteria with insufficient evidence.
"""

from __future__ import annotations

from priorauth.evaluator import Evaluation
from priorauth.schemas import ROUTE_SEVERITY, Finding, Flag, MissingDoc, Route
from priorauth.spec import CriteriaSpec, Node


def route_case(
    spec: CriteriaSpec, unit_ids: list[str], ev: Evaluation, extra_flags: list[Flag]
) -> tuple[Route, list[str]]:
    reasons: list[tuple[Route, str]] = []

    def units(node: Node) -> list[str | None]:
        return [None] if node.per == "request" else list(unit_ids)

    def at(unit: str | None) -> str:
        return f" for {unit}" if unit else ""

    for node in spec.criteria:
        for unit in units(node):
            f = ev.get(node.id, unit)
            if f is None:  # defensive: an unevaluated criterion can never pass
                reasons.append((Route.CLINICIAN_REVIEW, f"{node.section}{at(unit)} not evaluated"))
            elif f.status == "not_met":
                reasons.append(
                    (Route.CLINICIAN_REVIEW, f"{node.section}{at(unit)} not met: {node.summary}")
                )
            elif f.status != "met":
                reasons.append(
                    (
                        Route.REQUEST_INFO,
                        f"{node.section}{at(unit)} insufficient evidence: {node.summary}",
                    )
                )
    for nodes, rule_route, label in (
        (spec.contraindications, spec.rules.contraindication_found_route, "contraindication"),
        (spec.exclusions, spec.rules.exclusion_found_route, "exclusion"),
    ):
        for node in nodes:
            for unit in units(node):
                f = ev.get(node.id, unit)
                if f is not None and f.status == "found":
                    reasons.append(
                        (
                            Route(rule_route),
                            f"{label} {node.section}{at(unit)} found: {node.summary}",
                        )
                    )
    for flag in [*extra_flags, *ev.flags]:
        reasons.append((flag.route, f"{flag.kind} flag{at(flag.unit_id)}: {flag.detail}"))

    if not reasons:
        return Route.APPROVE_READY, ["every criterion met with verified evidence; nothing found"]
    route = max((r for r, _ in reasons), key=ROUTE_SEVERITY.__getitem__)
    return route, [text for _, text in reasons]


def missing_documents(spec: CriteriaSpec, unit_ids: list[str], ev: Evaluation) -> list[MissingDoc]:
    """Letter items: for each insufficient criterion, the documents its insufficient leaves need.

    Only built when the route is request info; a clinician-review letter is the clinician's.
    """
    items = {d.id: d for d in spec.documentation}
    out: list[MissingDoc] = []

    def walk(node: Node, unit: str | None, inherited: list[str]) -> None:
        f: Finding | None = ev.get(node.id, unit)
        if f is None or f.status != "insufficient":
            return
        docs = node.documentation or inherited
        if node.children:
            for c in node.children:
                walk(c, unit, docs)
            return
        if not docs:
            docs = [d.id for d in spec.documentation if node.section.split("(")[0] in d.supports]
        for doc_id in docs:
            d = items.get(doc_id)
            if d is None:
                continue
            m = MissingDoc(
                node_id=node.id,
                unit_id=unit,
                section=node.section,
                doc_item=d.id,
                name=d.name,
                must_show=d.must_show,
            )
            if not any(
                (x.doc_item, x.unit_id, x.section) == (m.doc_item, unit, m.section) for x in out
            ):
                out.append(m)

    for node in spec.criteria:
        for unit in [None] if node.per == "request" else unit_ids:
            walk(node, unit, [])
    return out
