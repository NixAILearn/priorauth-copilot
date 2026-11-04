"""Provider pre-submission gap check (PRD R8, D-077).

The same recommendation the nurse reviewer sees, reworded for the provider PA coordinator who
is about to submit: which policy criteria the packet does not show yet, and which documents
would show them. Code templates, no model, like letters.py.

Two things are left out on purpose (D-077):

- Flag details (injection, low confidence, flag rules, model errors) are reviewer aids. A
  submitter is told only that a clinician will look at the request.
- No wording predicts a denial. A request the copilot cannot clear goes to a Northwind
  physician reviewer, and the provider is told what that reviewer will look at.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from priorauth.letters import NOT_CLEAR, _docs_for, _nodes, _unit
from priorauth.schemas import PriorAuthRequest, Recommendation, Route
from priorauth.spec import CriteriaSpec

OUTLOOK = {
    Route.APPROVE_READY: (
        "Ready to submit",
        "Your packet appears to show every criterion in {policy}. A Northwind nurse reviewer "
        "still checks each item before any decision is made.",
    ),
    Route.REQUEST_INFO: (
        "Likely to be pended for information",
        "As it stands, the reviewer would likely ask you for more records. Adding the items "
        "below before you submit can avoid that pend and the wait that comes with it.",
    ),
    Route.CLINICIAN_REVIEW: (
        "Goes to a physician reviewer",
        "As it stands, this request would go to a Northwind physician reviewer for clinical "
        "judgment. That is not a decision. The items below are what the reviewer will look at.",
    ),
}

GAP_WORDS = {
    "insufficient": "Your documents do not show this yet",
    "not_met": "Your documents describe something other than what the policy requires",
    "found": "Your documents mention something the policy lists as a reason it does not apply",
}


@dataclass(frozen=True)
class Gap:
    section: str
    summary: str
    status: str
    unit: str = ""

    @property
    def words(self) -> str:
        return GAP_WORDS[self.status]


@dataclass(frozen=True)
class ToSend:
    item: str
    name: str
    must_show: str
    sections: tuple[str, ...]


@dataclass(frozen=True)
class GapReport:
    case_id: str
    policy_id: str
    route: Route
    headline: str
    outlook: str
    gaps: list[Gap] = field(default_factory=list)
    to_send: list[ToSend] = field(default_factory=list)

    def checklist(self) -> str:
        """Plain text the coordinator can paste into their own tracker."""
        lines = [f"Pre-submission check · {self.case_id} · {self.policy_id}", self.headline, ""]
        if self.to_send:
            lines.append("Add before you submit:")
            for s in self.to_send:
                lines.append(f"[ ] {s.name} (item {s.item}, for {', '.join(s.sections)})")
                lines.append(f"    Must show: {s.must_show}")
        if self.gaps:
            lines += ["", "Criteria your documents do not show as the policy requires:"]
            for g in self.gaps:
                lines.append(f"- {g.section}{g.unit}: {g.summary}. {g.words}.")
        if not self.to_send and not self.gaps:
            lines.append("Nothing to add.")
        lines += ["", "Demonstration only: fictional health plan, synthetic patient."]
        return "\n".join(lines)


def _item_key(item: str) -> list[int]:
    return [int(p) for p in item.split(".") if p.isdigit()]


def gap_check(rec: Recommendation, req: PriorAuthRequest, spec: CriteriaSpec) -> GapReport:
    nodes = _nodes(spec)
    docs = {d.id: d for d in spec.documentation}
    tops = {n.id for n in (*spec.criteria, *spec.contraindications, *spec.exclusions)}
    headline, outlook = OUTLOOK[rec.route]

    gaps = [
        Gap(f.section, nodes[f.node_id].summary, f.status, _unit(f.unit_id, req))
        for f in rec.findings
        if f.node_id in tops and f.status in NOT_CLEAR
    ]

    # Request info: exactly the items the reviewer's letter would ask for, so the provider is not
    # asked for more than Northwind would ask (missing-doc precision, D-005). Otherwise: the
    # documents that would resolve each insufficient criterion, as in the medical director brief.
    needs: dict[str, set[str]] = {}
    for m in rec.missing:
        needs.setdefault(m.doc_item, set()).add(m.section)
    if not rec.missing:
        for f in rec.findings:
            if f.node_id in tops and f.status == "insufficient":
                for d in _docs_for(nodes[f.node_id], spec):
                    needs.setdefault(d, set()).add(f.section)
    to_send = [
        ToSend(i, docs[i].name, docs[i].must_show, tuple(sorted(needs[i])))
        for i in sorted(needs, key=_item_key)
        if i in docs
    ]
    return GapReport(
        rec.case_id,
        rec.policy_id,
        rec.route,
        headline,
        outlook.format(policy=f"{rec.policy_id} version {rec.policy_version}"),
        gaps,
        to_send,
    )
