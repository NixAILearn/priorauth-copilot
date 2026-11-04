"""Letter drafts from code templates, no model (D-071).

Three drafts, each traceable line by line to the recommendation and the reviewed spec:

- request_info_letter: the missing documentation items, the policy section and criterion each
  supports, and what it must show (CMS-0057-F asks for specific reasons).
- approval_notice: only after a person approves.
- md_brief: the one-page case brief for the medical director.

There is no adverse determination letter. A physician makes and writes that decision outside
the copilot. Every draft is for a reviewer to edit and send; none is sent by the app.
"""

from __future__ import annotations

from datetime import date

from priorauth.schemas import Finding, PriorAuthRequest, Recommendation, Route
from priorauth.spec import CriteriaSpec, Node

PLAN = "Northwind Health Plan"
FOOTER = (
    "Draft prepared by PriorAuth Copilot for a Northwind reviewer to check, edit and send. "
    "Fictional health plan, synthetic member: demonstration only."
)
STATUS_WORDS = {
    "met": "met",
    "not_met": "not met",
    "insufficient": "insufficient evidence",
    "found": "found",
    "not_found": "not found",
}


def _long(d: date) -> str:
    return f"{d:%B} {d.day}, {d.year}"


def diagnoses(req: PriorAuthRequest) -> str:
    return ", ".join(d.code + (" (primary)" if d.role == "primary" else "") for d in req.diagnoses)


def _nodes(spec: CriteriaSpec) -> dict[str, Node]:
    return {n.id: n for n in spec.nodes()}


def _unit(unit_id: str | None, req: PriorAuthRequest) -> str:
    if unit_id is None:
        return ""
    for u in req.service.target_ulcers:
        if u.id == unit_id:
            return f" (target ulcer {u.id}, {u.laterality} {u.site})"
    return f" ({unit_id})"


def _header(req: PriorAuthRequest, rec: Recommendation, subject: str, today: date) -> list[str]:
    p = req.requesting_provider
    return [
        f"{PLAN} · Utilization Management",
        f"Date: {_long(today)}",
        "",
        f"To: {p.name}, {p.specialty}, {p.organization} (NPI {p.npi})",
        f"Member: {req.member.synthetic_id}",
        f"Request: {req.request_id}, received {_long(req.received_at.date())}"
        f" ({req.review_type} review)",
        f"Service: {req.service.code} {req.service.description}",
        f"Medical policy: {rec.policy_id} version {rec.policy_version}",
        "",
        f"Re: {subject}",
        "",
    ]


def request_info_letter(
    rec: Recommendation, req: PriorAuthRequest, spec: CriteriaSpec, today: date
) -> str:
    if not rec.missing:
        raise ValueError(f"{rec.case_id}: no missing documentation to request")
    nodes = _nodes(spec)
    lines = _header(req, rec, "Request for additional information", today)
    lines += [
        f"Dear {req.requesting_provider.name},",
        "",
        f"We are reviewing the prior authorization request above under {rec.policy_id}. "
        "This is not a decision on the request. To complete the review we need the "
        "documentation listed below. Each item names the policy section it supports and what "
        "the record must show.",
        "",
    ]
    for i, m in enumerate(rec.missing, 1):
        node = nodes.get(m.node_id)
        criterion = node.summary if node else m.section
        lines += [
            f"{i}. {m.name}{_unit(m.unit_id, req)}",
            f"   Policy section: {m.section} ({criterion})",
            f"   Documentation item: {m.doc_item}",
            f"   The record must show: {m.must_show}",
            "",
        ]
    lines += [
        "Please send these records by [response date set by reviewer]. If they are not "
        "available, tell us, and a Northwind clinician will review the request with the "
        "records on file.",
        "",
        "Sincerely,",
        "[Reviewer name], RN, Utilization Management",
        "",
        FOOTER,
    ]
    return "\n".join(lines)


def approval_notice(
    rec: Recommendation, req: PriorAuthRequest, spec: CriteriaSpec, reviewer: str, today: date
) -> str:
    nodes = _nodes(spec)
    lines = _header(req, rec, "Prior authorization approved", today)
    lines += [
        f"Dear {req.requesting_provider.name},",
        "",
        f"{PLAN} has approved the service above. A Northwind reviewer checked the request "
        f"against {rec.policy_id} version {rec.policy_version}. The record shows:",
        "",
    ]
    for f in rec.findings:
        node = nodes.get(f.node_id)
        if node is None or f.status != "met" or not _is_top(spec, f.node_id):
            continue
        lines.append(f"- {f.section}{_unit(f.unit_id, req)}: {node.summary}")
    lines += [
        "",
        "This approval covers the service, code and units on the request.",
        "",
        "Sincerely,",
        f"{reviewer}, Utilization Management",
        "",
        FOOTER,
    ]
    return "\n".join(lines)


def _is_top(spec: CriteriaSpec, node_id: str) -> bool:
    return any(n.id == node_id for n in (*spec.criteria, *spec.contraindications, *spec.exclusions))


def _evidence(f: Finding) -> list[str]:
    out = []
    for c in f.citations:
        tag = "" if c.verified else " [quote NOT found in the document]"
        out.append(f'    {c.doc_id}: "{c.quote}"{tag}')
    return out or ["    No cited evidence."]


def md_brief(rec: Recommendation, req: PriorAuthRequest, spec: CriteriaSpec, today: date) -> str:
    """One page for the medical director: what is unresolved and what would resolve it."""
    nodes = _nodes(spec)
    docs = {d.id: d for d in spec.documentation}
    tops = {n.id for n in (*spec.criteria, *spec.contraindications, *spec.exclusions)}
    lines = [
        f"CASE BRIEF FOR MEDICAL DIRECTOR · {rec.case_id} · {today:%Y-%m-%d}",
        "",
        f"Member {req.member.synthetic_id}, born {req.member.birth_date:%Y}, {req.member.sex}",
        f"Service: {req.service.code} {req.service.description.rstrip('.')}"
        + (f", {req.service.side} side" if req.service.side else ""),
        f"Diagnoses: {diagnoses(req)}",
        f"Requested by: {req.requesting_provider.name}, {req.requesting_provider.specialty}",
        f"Policy: {rec.policy_id} version {rec.policy_version}",
        f"Copilot route: {rec.route.value.replace('_', ' ')}. The copilot does not deny; "
        "this case needs a physician's judgment.",
        "",
        "WHY IT WAS ROUTED HERE",
        *[f"- {r}" for r in rec.reasons],
        "",
    ]
    if rec.flags:
        lines.append("FLAGS")
        for fl in rec.flags:
            rule = f" {fl.rule_id}" if fl.rule_id else ""
            lines.append(f"- {fl.kind}{rule}{_unit(fl.unit_id, req)}: {fl.detail}")
            for c in fl.citations:
                lines.append(f'    {c.doc_id}: "{c.quote}"')
        lines.append("")
    open_items = [f for f in rec.findings if f.node_id in tops and f.status in NOT_CLEAR]
    lines.append("CRITERIA NOT CLEARED")
    if not open_items:
        lines.append("- None: every criterion is met and nothing was found. See flags above.")
    needs: dict[str, set[str]] = {}
    for f in open_items:
        node = nodes[f.node_id]
        value = f" Value compared: {f.value}." if f.value else ""
        lines.append(
            f"- {f.section}{_unit(f.unit_id, req)} {STATUS_WORDS[f.status]}: {node.summary}.{value}"
        )
        lines += _evidence(f)
        if f.status == "insufficient":
            for d in _docs_for(node, spec):
                needs.setdefault(d, set()).add(f.section)
    lines += ["", "WHAT THE PROVIDER WOULD NEED TO SEND"]
    if needs:
        for d_id in sorted(needs, key=lambda x: [int(p) for p in x.split(".") if p.isdigit()]):
            d = docs[d_id]
            secs = ", ".join(sorted(needs[d_id]))
            lines.append(f"- {d.name} (item {d.id}, for {secs}): {d.must_show}")
    else:
        lines.append(
            "- Nothing would change the route by documentation alone: the open items are "
            "not met, found or flagged, which need clinical judgment."
        )
    lines += ["", FOOTER]
    return "\n".join(lines)


NOT_CLEAR = {"not_met", "insufficient", "found"}


def _docs_for(node: Node, spec: CriteriaSpec) -> list[str]:
    ids = list(node.documentation)
    for n in node.walk():
        ids += [d for d in n.documentation if d not in ids]
    if not ids:
        base = node.section.split("(")[0]
        ids = [d.id for d in spec.documentation if base in d.supports]
    known = {d.id for d in spec.documentation}
    return [i for i in ids if i in known]


def draft_for(
    rec: Recommendation, req: PriorAuthRequest, spec: CriteriaSpec, today: date
) -> tuple[str, str] | None:
    """The draft that matches the copilot's route, if any: (title, text)."""
    if rec.route == Route.REQUEST_INFO and rec.missing:
        return "Request for information (draft)", request_info_letter(rec, req, spec, today)
    if rec.route == Route.CLINICIAN_REVIEW:
        return "Medical director brief", md_brief(rec, req, spec, today)
    return None
