"""Reviewer app logic, kept out of Streamlit so it can be tested (docs/app-design.md).

- the demo clock and SLA (D-069)
- the criteria checklist built from the spec tree and the recommendation's findings
- which items a reviewer must mark reviewed before a final action (D-070)
- document highlighting with every character escaped (D-072)

Nothing here can change a route: the router's output is shown as is, and reviewer overrides
are recorded beside it.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from priorauth.schemas import SLA, Evidence, Finding, Flag, PriorAuthRequest, Recommendation, Route
from priorauth.spec import CriteriaSpec, Node

# --- Labels -----------------------------------------------------------------------------------

ROUTE_LABEL = {
    Route.APPROVE_READY: "Approve-ready",
    Route.REQUEST_INFO: "Request info",
    Route.CLINICIAN_REVIEW: "Clinician review",
}
STATUS_LABEL = {
    "met": "Met",
    "not_met": "Not met",
    "insufficient": "Insufficient evidence",
    "found": "Found",
    "not_found": "Not found",
}
NEEDS_REVIEW = {"not_met", "insufficient", "found"}
ACTION_LABEL = {
    "approve": "Approve",
    "request_info": "Send request for information",
    "refer_md": "Refer to medical director",
    "left_copilot": "Determination made outside the copilot",
}
# The action that agrees with each route; any other action needs a typed reason (D-070).
AGREEING_ACTION = {
    Route.APPROVE_READY: "approve",
    Route.REQUEST_INFO: "request_info",
    Route.CLINICIAN_REVIEW: "refer_md",
}
NURSE_ACTIONS = ("approve", "request_info", "refer_md")
MD_ACTIONS = ("approve", "left_copilot")


# --- Demo clock (D-069) -----------------------------------------------------------------------

NEWEST_AGE = timedelta(hours=2)
OLDEST_AGE = timedelta(days=9)


def rebased_arrivals(received: dict[str, datetime], clock: datetime) -> dict[str, datetime]:
    """Display-only arrival times: same order, spacing scaled into the last 9 days."""
    if not received:
        return {}
    newest, oldest = max(received.values()), min(received.values())
    span = (newest - oldest).total_seconds()
    out = {}
    for case_id, t in received.items():
        frac = (newest - t).total_seconds() / span if span else 0.0
        out[case_id] = clock - NEWEST_AGE - frac * (OLDEST_AGE - NEWEST_AGE)
    return out


def sla_due(arrival: datetime, review_type: str) -> datetime:
    return arrival + SLA[review_type]


def fmt_remaining(delta: timedelta) -> str:
    sign = "-" if delta < timedelta(0) else ""
    secs = abs(int(delta.total_seconds()))
    days, rem = divmod(secs, 86_400)
    hours = rem // 3600
    if days:
        return f"{sign}{days}d {hours}h"
    return f"{sign}{hours}h {(rem % 3600) // 60}m"


# --- Checklist --------------------------------------------------------------------------------


@dataclass(frozen=True)
class Row:
    """One line of the criteria checklist."""

    kind: str  # criterion, contraindication, exclusion
    node: Node
    unit_id: str | None
    depth: int
    finding: Finding | None
    top: bool

    @property
    def key(self) -> str:
        return f"{self.node.id}@{self.unit_id or '-'}"

    @property
    def status(self) -> str:
        # A node with no finding can never pass (router does the same): show it as insufficient.
        return self.finding.status if self.finding else "insufficient"

    @property
    def needs_review(self) -> bool:
        return self.top and self.status in NEEDS_REVIEW


def checklist(spec: CriteriaSpec, rec: Recommendation, unit_ids: list[str]) -> list[Row]:
    found = {(f.node_id, f.unit_id): f for f in rec.findings}
    rows: list[Row] = []

    def add(kind: str, node: Node, unit: str | None, depth: int) -> None:
        rows.append(Row(kind, node, unit, depth, found.get((node.id, unit)), depth == 0))
        for child in node.children:
            add(kind, child, unit, depth + 1)
        if node.exception:
            add(kind, node.exception, unit, depth + 1)

    for kind, nodes in (
        ("criterion", spec.criteria),
        ("contraindication", spec.contraindications),
        ("exclusion", spec.exclusions),
    ):
        for node in nodes:
            for unit in [None] if node.per == "request" else (unit_ids or [None]):
                add(kind, node, unit, 0)
    return rows


def flag_key(i: int) -> str:
    return f"flag:{i}"


@dataclass
class ReviewState:
    """What the reviewer has done on one run, rebuilt from the audit log."""

    reviewed: set[str] = field(default_factory=set)  # row keys and flag keys
    overrides: dict[str, tuple[str, str]] = field(default_factory=dict)  # key -> (status, why)

    @classmethod
    def from_rows(cls, rows) -> ReviewState:
        st = cls()
        for r in rows:
            key = (
                r["item_id"]
                if r["item_id"].startswith("flag:")
                else (f"{r['item_id']}@{r['unit_id'] or '-'}")
            )
            st.reviewed.add(key)
            if r["kind"] == "override":
                st.overrides[key] = (r["to_status"], r["reason"])
        return st


def pending_reviews(rows: list[Row], flags: list[Flag], state: ReviewState) -> list[str]:
    """Keys still to be marked reviewed before a final action is allowed (D-070)."""
    todo = [r.key for r in rows if r.needs_review and r.key not in state.reviewed]
    todo += [flag_key(i) for i in range(len(flags)) if flag_key(i) not in state.reviewed]
    return todo


def action_needs_reason(route: Route, action: str) -> bool:
    return AGREEING_ACTION.get(route) != action


# --- Highlighting (D-072) ---------------------------------------------------------------------

_QUOTES = {"’": "'", "‘": "'", "“": '"', "”": '"'}


def _normalize(text: str) -> tuple[str, list[tuple[int, int]]]:
    """quotes.py normalization, keeping each output character's span in the original text.

    Asterisks drop; quote marks fold; a run of whitespace becomes one space, and a run of
    whitespace containing a table bar or colon becomes " | " (D-062).
    """
    out: list[str] = []
    spans: list[tuple[int, int]] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "*":
            i += 1
            continue
        if c.isspace() or c in "|:":
            j, sep = i, False
            while j < n and (text[j].isspace() or text[j] in "|:*"):
                sep = sep or text[j] in "|:"
                j += 1
            for ch in " | " if sep else " ":
                out.append(ch)
                spans.append((i, j))
            i = j
            continue
        out.append(_QUOTES.get(c, c))
        spans.append((i, i + 1))
        i += 1
    return "".join(out), spans


def locate(doc: str, quote: str) -> tuple[int, int] | None:
    """Character span of a quote in the original document, or None if it is not there."""
    nd, spans = _normalize(doc)
    nq = _normalize(quote)[0].strip(" |")
    if len(nq) < 2:
        return None
    for q in (nq, nq[0].swapcase() + nq[1:]):
        k = nd.find(q)
        if k >= 0:
            start, end = spans[k][0], spans[k + len(q) - 1][1]
            while end > start and doc[end - 1] in " \t\n|:*":  # trailing separator run
                end -= 1
            return start, end
    return None


@dataclass(frozen=True)
class Mark:
    quote: str
    style: str  # "evidence", "focus" or "injection"


def highlight(doc: str, marks: list[Mark]) -> tuple[str, list[Mark]]:
    """HTML for a document with marks added. Every document character is escaped first.

    Returns the HTML and the marks that could not be located.
    """
    spans: list[tuple[int, int, str]] = []
    missing: list[Mark] = []
    for m in marks:
        loc = locate(doc, m.quote)
        if loc is None:
            missing.append(m)
        else:
            spans.append((loc[0], loc[1], m.style))
    # Paint character by character so overlaps resolve to the strongest style.
    rank = {"evidence": 1, "focus": 2, "injection": 3}
    paint = [""] * len(doc)
    for s, e, style in spans:
        for k in range(s, e):
            if rank[style] > rank.get(paint[k], 0):
                paint[k] = style
    parts: list[str] = []
    k = 0
    while k < len(doc):
        style = paint[k]
        j = k
        while j < len(doc) and paint[j] == style:
            j += 1
        chunk = html.escape(doc[k:j])
        parts.append(f'<mark class="{style}">{chunk}</mark>' if style else chunk)
        k = j
    return "".join(parts), missing


DOC_CSS = """
<style>
.pa-doc { white-space: pre-wrap; font-family: ui-monospace, Menlo, Consolas, monospace;
  font-size: 0.82rem; line-height: 1.45; padding: 0.9rem 1rem; border-radius: 6px;
  border: 1px solid rgba(128,128,128,0.35); max-height: 34rem; overflow-y: auto; }
.pa-doc mark { padding: 0 1px; border-radius: 2px; color: inherit; }
.pa-doc mark.evidence { background: rgba(255, 213, 79, 0.35); }
.pa-doc mark.focus { background: rgba(255, 179, 0, 0.75); outline: 1px solid #b26a00; }
.pa-doc mark.injection { background: rgba(229, 57, 53, 0.30); outline: 1px dashed #c62828; }
</style>
"""


def document_html(doc: str, marks: list[Mark]) -> tuple[str, list[Mark]]:
    body, missing = highlight(doc, marks)
    return f'{DOC_CSS}<div class="pa-doc">{body}</div>', missing


def evidence_by_doc(rec: Recommendation) -> dict[str, list[Evidence]]:
    out: dict[str, list[Evidence]] = {}
    for f in rec.findings:
        for c in f.citations:
            out.setdefault(c.doc_id, []).append(c)
    for fl in rec.flags:
        for c in fl.citations:
            out.setdefault(c.doc_id, []).append(c)
    return out


_MD_SPECIAL = set("\\`*_{}[]()#+-.!|<>~$&:/")


def md_escape(text: str) -> str:
    """Backslash-escape Markdown so document text shown in the app cannot form links, images,
    emphasis or HTML (D-072). Newlines become spaces."""
    flat = " ".join(text.split())
    return "".join("\\" + c if c in _MD_SPECIAL else c for c in flat)


def doc_title(doc: str, doc_id: str) -> str:
    """The `title:` line of a document's front matter, else its ID."""
    for line in doc.splitlines()[:12]:
        if line.startswith("title:"):
            return f"{doc_id} · {line.split(':', 1)[1].strip()}"
    return doc_id


def member_label(req: PriorAuthRequest) -> str:
    return f"{req.member.synthetic_id} ({req.member.sex}, born {req.member.birth_date:%Y})"
