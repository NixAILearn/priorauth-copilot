"""Evaluator: a status for every node, in code, from verified evidence (D-045, D-046).

- numeric, date_window and enum nodes: code applies the threshold or window to the most
  recent verified (or derived) value. Evidence only outside a window is insufficient (D-029).
- fact nodes: the model's assessment, kept only when its quote verifies.
- groups: all_of / any_of logic in code.
- contraindications and exclusions are found or not found; never insufficient (D-024).
"""

from __future__ import annotations

import operator
import re
from dataclasses import dataclass, field
from datetime import date

from priorauth.derive import Store, derive_all, in_window
from priorauth.extractor import Obs, Verified, kind_of
from priorauth.intake import REQUEST_DOC, CaseInput
from priorauth.quotes import norm
from priorauth.schemas import Evidence, Finding, Flag, Route, Status
from priorauth.spec import CriteriaSpec, Node

OPS = {">=": operator.ge, ">": operator.gt, "<=": operator.le, "<": operator.lt}
CRITERION_STATUSES = {"met", "not_met", "insufficient"}
FLAGGED_STATUSES = {"found", "not_found"}


@dataclass
class Evaluation:
    findings: list[Finding] = field(default_factory=list)
    flags: list[Flag] = field(default_factory=list)

    def get(self, node_id: str, unit_id: str | None) -> Finding | None:
        return next(
            (f for f in self.findings if f.node_id == node_id and f.unit_id == unit_id), None
        )


def _fmt(o: Obs) -> str:
    v = o.value
    shown = f"{v:g}" if isinstance(v, float) else str(v)
    return f"{shown} {o.unit or ''}".strip() + (f" on {o.on}" if o.on else "")


class _Run:
    def __init__(self, case: CaseInput, verified: Verified):
        self.case = case
        self.spec: CriteriaSpec = case.spec
        self.v = verified
        self.kinds = kind_of(self.spec)
        self.rd: date = case.request_date
        self.out = Evaluation()
        self._conflicts: set[tuple[str, str | None]] = set()
        rules = {r.id: (n, r) for n in self.spec.nodes() for r in n.flag_rules}
        self.soften = {
            (rules[c.rule_id][0].id, c.unit_id)
            for c, cites in verified.flag_claims
            if rules[c.rule_id][1].route == "request_info" and any(x.verified for x in cites)
        }
        self.store: Store = {k: list(obs) for k, obs in verified.obs.items()}
        derive_all(self.store, self.spec, case)

    # -- helpers ------------------------------------------------------------------------------

    def flag(self, **kw) -> None:
        f = Flag(**kw)
        if f not in self.out.flags:
            self.out.flags.append(f)

    def low_confidence(self, node: Node, unit: str | None, detail: str, cites=()) -> None:
        self.flag(
            kind="low_confidence",
            route=Route.CLINICIAN_REVIEW,
            unit_id=unit,
            detail=f"{node.id} ({node.section}): {detail}",
            citations=list(cites),
        )

    def candidates(self, node: Node, unit: str | None) -> list[Obs]:
        return [
            o
            for o in self.store.get((node.field or "", unit), [])
            if o.on is None or o.on <= self.rd
        ]

    def latest(self, node: Node, unit: str | None, obs: list[Obs]) -> Obs:
        top = max(obs, key=lambda o: o.on or date.min)
        ties = [o for o in obs if o.on == top.on]
        if len({o.value for o in ties}) > 1 and (node.field, unit) not in self._conflicts:
            self._conflicts.add((node.field or "", unit))
            self.flag(
                kind="conflict",
                route=Route(self.spec.rules.conflict_route),
                unit_id=unit,
                detail=f"{node.field}: values on {top.on} disagree "
                f"({', '.join(sorted(_fmt(o) for o in ties))})",
                citations=[e for o in ties for e in o.evidence()],
            )
        return top

    # -- node evaluation ----------------------------------------------------------------------

    def finding(
        self,
        node: Node,
        unit,
        status: Status,
        source,
        *,
        obs: Obs | None = None,
        cites: list[Evidence] | None = None,
        note: str = "",
    ) -> Finding:
        f = Finding(
            node_id=node.id,
            unit_id=unit,
            section=node.section,
            status=status,
            source=source,
            value=_fmt(obs) if obs else None,
            citations=cites if cites is not None else (obs.evidence() if obs else []),
            note=note,
        )
        self.out.findings.append(f)
        return f

    def evaluate(self, node: Node, unit: str | None) -> Status:
        positive_kind = self.kinds[node.id] != "criterion"  # contraindication / exclusion
        yes: Status = "found" if positive_kind else "met"
        no: Status = "not_found" if positive_kind else "not_met"
        gap: Status = "not_found" if positive_kind else "insufficient"

        if node.type in ("all_of", "any_of"):
            kids = [self.evaluate(c, unit) for c in node.children]
            if node.type == "any_of" and not positive_kind:
                kids = self.unused_branches(node, unit, kids)
            status = self.softened(node, unit, group_status(node.type, kids, positive_kind))
            self.finding(node, unit, status, "group")
            return status

        if node.type == "fact":
            return self.fact(node, unit, yes, no, gap)

        obs = self.candidates(node, unit)
        if node.type == "date_window":
            dated = [o for o in obs if isinstance(o.value, date)]
            inside = [o for o in dated if in_window(o.value, self.rd, node.window)]  # type: ignore[arg-type]
            if inside:
                o = max(inside, key=lambda o: o.value)  # type: ignore[arg-type,return-value]
                self.finding(node, unit, yes, "code", obs=o)
                return yes
            note = "only outside the window" if dated else "no dated evidence"
            last = max(dated, key=lambda o: o.value) if dated else None  # type: ignore[arg-type,return-value]
            self.finding(node, unit, gap, "code" if dated else "none", obs=last, note=note)
            return gap

        if node.window:
            inside = [o for o in obs if in_window(o.on, self.rd, node.window)]
            if not inside:
                note = "only outside the window" if obs else "no value found"
                self.finding(node, unit, gap, "none", note=note)
                return gap
            obs = inside
        if node.type == "numeric":
            obs = [o for o in obs if isinstance(o.value, float)]
        if not obs:
            self.finding(node, unit, gap, "none", note="no value found")
            return gap
        o = self.latest(node, unit, obs)
        if node.type == "numeric":
            holds = OPS[node.op](o.value, node.value)  # type: ignore[index,arg-type]
            note = f"{_fmt(o)} {node.op} {node.value:g} is {'true' if holds else 'false'}"  # type: ignore[union-attr]
        else:  # enum
            holds = o.value == node.equals
            note = f"{node.field} is {o.value}"
        status = self.softened(node, unit, yes if holds else no)
        self.finding(node, unit, status, "code", obs=o, note=note)
        return status

    def softened(self, node: Node, unit, status: Status) -> Status:
        """A verified flag rule that routes to request info turns not met into insufficient.

        NHP-MP-034 3.9's rule says so in words: a gap spanning visits whose notes are missing
        is insufficient evidence, not not met.
        """
        if status == "not_met" and (node.id, unit) in self.soften:
            return "insufficient"
        return status

    def has_evidence(self, node: Node, unit) -> bool:
        ids = {n.id for n in node.walk()}
        return any(
            f.node_id in ids
            and f.unit_id == unit
            and (f.status in ("met", "not_met") or f.citations or f.value)
            for f in self.out.findings
        )

    def unused_branches(self, node: Node, unit, kids: list[Status]) -> list[Status]:
        """D-029 rule 4: once one branch of an any-of is documented, an alternative *test*
        branch (numeric, date or enum nodes only) that the record shows no sign of using is
        not met, so the letter does not ask for it (D-050). Fact branches stay insufficient:
        a provider can still document them."""
        documented = [k in ("met", "not_met") for k in kids]
        if not any(documented):
            return kids
        out = list(kids)
        for i, child in enumerate(node.children):
            tests_only = all(n.type != "fact" for n in child.walk())
            if kids[i] == "insufficient" and tests_only and not self.has_evidence(child, unit):
                out[i] = "not_met"
                ids = {n.id for n in child.walk()}
                self.out.findings = [
                    f.model_copy(
                        update={"status": "not_met", "note": "branch not used (D-029 rule 4)"}
                    )
                    if f.node_id in ids and f.unit_id == unit and f.status == "insufficient"
                    else f
                    for f in self.out.findings
                ]
        return out

    def fact(self, node: Node, unit, yes: Status, no: Status, gap: Status) -> Status:
        code = CODE_FACTS.get(node.id)
        decided = code(self, node, unit) if code else None
        if decided is not None:
            status, cites, note = decided
            self.finding(node, unit, status, "code", cites=cites, note=note)
            return status
        allowed = FLAGGED_STATUSES if yes == "found" else CRITERION_STATUSES
        got = self.v.facts.get((node.id, unit))
        if got is None or got[0].status not in allowed:
            if yes == "found":  # a contraindication the model did not assess (D-046)
                self.low_confidence(node, unit, "the model returned no assessment")
            self.finding(node, unit, gap, "none", note="no assessment")
            status = gap
        else:
            a, cites = got
            ok = [c for c in cites if c.verified]
            status = a.status  # type: ignore[assignment]
            note = a.rationale
            if status in (yes, no) and status != "not_found" and not ok:
                blocking = status in ("found", "not_met")
                note = f"quote not verified; model said {a.status}. {a.rationale}"
                if blocking:  # an unverified warning never becomes a clean pass (D-046)
                    self.low_confidence(node, unit, f"unverified {a.status} claim", cites)
                status = gap
            if status == "met" and node.id in EVERY_NOTE:
                gaps = uncovered_notes(self, node, unit, cites)
                if gaps:  # D-065: one visit's quote cannot show "every note"
                    status = gap
                    missing = ", ".join(gaps)
                    note = f"no verified quote from {missing}; model said met. {a.rationale}"
            if a.confidence == "low":
                self.low_confidence(node, unit, "the model marked this low confidence", cites)
            self.finding(node, unit, status, "model", cites=cites, note=note)
        idx = len(self.out.findings) - 1
        if node.exception is not None:
            exc = self.evaluate_exception(node.exception, unit)
            if exc and status == "found":
                self.out.findings[idx] = self.out.findings[idx].model_copy(
                    update={"status": "not_found", "note": f"exception {node.exception.id} met"}
                )
                return "not_found"
        return status

    def evaluate_exception(self, node: Node, unit) -> bool:
        """An exception inside a contraindication is found (applies) or not found."""
        got = self.v.facts.get((node.id, unit))
        applies = bool(got and got[0].status == "found" and any(c.verified for c in got[1]))
        self.finding(
            node,
            unit,
            "found" if applies else "not_found",
            "model",
            cites=got[1] if got else [],
            note="exception",
        )
        return applies


def group_status(kind: str, kids: list[Status], flagged: bool) -> Status:
    if flagged:  # contraindication groups: any found / all found
        found = [k == "found" for k in kids]
        return "found" if (any(found) if kind == "any_of" else all(found)) else "not_found"
    if kind == "all_of":
        if "not_met" in kids:
            return "not_met"
        return "insufficient" if "insufficient" in kids else "met"
    if "met" in kids:
        return "met"
    return "insufficient" if "insufficient" in kids else "not_met"


# --- Checks code makes from verified values instead of the model's judgment (D-063) -----------
# Each returns None when the verified values cannot settle it; the model's answer then stands.


def _on(run: _Run, name: str, unit, when: date) -> set[str]:
    return {str(o.value) for o in run.store.get((name, unit), []) if o.on == when}


def method_changed(run: _Run, unit) -> tuple[bool, list[Evidence]] | None:
    """034-C7-F1: the measurement method at baseline versus at the current measurement."""
    base = [o for o in run.store.get(("baseline_date", unit), []) if isinstance(o.value, date)]
    cur = run.store.get(("current_measurement_date", unit), [])
    if not base or not cur:
        return None
    b = max(base, key=lambda o: o.value).value  # type: ignore[arg-type,return-value]
    c = cur[0].value
    mb, mc = _on(run, "measurement_method", unit, b), _on(run, "measurement_method", unit, c)  # type: ignore[arg-type]
    if not mb or not mc or "not_stated" in mb | mc:
        return None
    cites = [
        e
        for o in run.store.get(("measurement_method", unit), [])
        if o.on in (b, c)
        for e in o.evidence()
    ]
    return mb != mc, cites


def ahi_rule_only_3pct_or_arousal(run: _Run, unit) -> tuple[bool, list[Evidence]] | None:
    """021-C3-F2 (D-066): the scoring rule of the latest verified study's AHI."""
    obs = [o for o in run.store.get(("ahi_scoring_rule", unit), []) if o.value != "not_stated"]
    if not obs:
        return None
    last = max((o.on for o in obs if o.on), default=None)
    latest = [o for o in obs if o.on == last] if last else obs
    rules = {str(o.value) for o in latest}
    cites = [e for o in latest for e in o.evidence()]
    if "4_percent" in rules:
        return False, cites
    if rules <= {"3_percent", "arousal_based"}:
        return True, cites
    return None


CODE_FLAG_RULES = {"034-C7-F1": method_changed, "021-C3-F2": ahi_rule_only_3pct_or_arousal}

_OPPOSITE = {"right": "left", "left": "right"}


def knee_side(run: _Run, node: Node, unit) -> tuple[Status, list[Evidence], str] | None:
    """047-C2: every verified document side is the requested side, both, or not stated."""
    req = {
        str(o.value)
        for o in run.store.get(("requested_knee_side", unit), [])
        if o.value in _OPPOSITE
    }
    sides = run.store.get(("evidence_knee_side", unit), [])
    if len(req) != 1 or not sides:
        return None
    want = req.pop()
    wrong = [o for o in sides if o.value == _OPPOSITE[want]]
    if wrong:
        cites = [e for o in wrong for e in o.evidence()]
        return "not_met", cites, f"a document names the {_OPPOSITE[want]} knee"
    if not any(o.value in (want, "both") for o in sides):
        return None
    cites = [e for o in sides for e in o.evidence()]
    return "met", cites, f"every verified document side is {want}, both or not stated"


CODE_FACTS = {"047-C2": knee_side}


def same_site_as_request(run: _Run, unit, cites: list[Evidence]) -> bool:
    """034-C4-F1 (D-064): True when the claim's own wound-note quotes show the request's side
    and site, so the claimed mismatch contradicts its evidence. Code can only drop such a claim,
    never raise one: it cannot see notes the model did not quote."""
    side = {str(o.value) for o in run.store.get(("ulcer_laterality", unit), [])}
    site = {str(o.value).strip().lower() for o in run.store.get(("ulcer_site", unit), [])}
    notes = [c for c in cites if c.verified and c.doc_id != REQUEST_DOC]
    if len(side) != 1 or len(site) != 1 or not notes or side & {"not_stated"}:
        return False
    want, where = side.pop(), site.pop()
    other = _OPPOSITE[want]
    for c in notes:
        q = norm(c.quote).lower()
        if not re.search(rf"\b{want}\b", q) or re.search(rf"\b{other}\b", q) or where not in q:
            return False
    return True


CLAIM_CHECKS = {"034-C4-F1": same_site_as_request}

# --- "Every note" facts (D-065): met only when each note of the period has a verified quote ---

EVERY_NOTE = {"034-C14b": "wound_care_note"}
_HEAD = re.compile(r"\A\s*---(.*?)---", re.S)


def doc_meta(text: str) -> tuple[str | None, date | None]:
    m = _HEAD.match(text)
    if not m:
        return None, None
    t = re.search(r"\btype:\s*(\S+)", m[1])
    d = re.search(r"\bdate:\s*(\d{4})-(\d{2})-(\d{2})", m[1])
    return (t[1] if t else None), (date(int(d[1]), int(d[2]), int(d[3])) if d else None)


def uncovered_notes(run: _Run, node: Node, unit, cites: list[Evidence]) -> list[str]:
    """Notes of the kind the node needs, in the standard-care period, with no verified quote.
    Without a verified baseline and current date, every such note up to the request counts."""
    base = [
        o.value for o in run.store.get(("baseline_date", unit), []) if isinstance(o.value, date)
    ]
    cur = [o.value for o in run.store.get(("current_measurement_date", unit), [])]
    lo = max(base) if base else date.min  # type: ignore[type-var]
    hi = cur[0] if cur and isinstance(cur[0], date) else run.rd
    cited = {c.doc_id for c in cites if c.verified}
    out = []
    for doc_id, text in run.case.documents.items():
        kind, on = doc_meta(text)
        if kind == EVERY_NOTE[node.id] and on and lo <= on <= hi and doc_id not in cited:
            out.append(doc_id)
    return sorted(out)


def evaluate(case: CaseInput, verified: Verified) -> Evaluation:
    run = _Run(case, verified)
    for top in (*case.spec.criteria, *case.spec.contraindications, *case.spec.exclusions):
        for unit in [None] if top.per == "request" else case.unit_ids:
            run.evaluate(top, unit)

    rules = {r.id: (n, r) for n in case.spec.nodes() for r in n.flag_rules}
    settled: set[tuple[str, str | None]] = set()
    for rule_id, check in CODE_FLAG_RULES.items():
        if rule_id not in rules:
            continue
        node, rule = rules[rule_id]
        for unit in [None] if node.per == "request" else case.unit_ids:
            got = check(run, unit)
            if got is None:
                continue
            settled.add((rule_id, unit))
            if got[0]:
                run.flag(
                    kind="flag_rule",
                    route=Route(rule.route),
                    rule_id=rule.id,
                    unit_id=unit,
                    detail=f"{rule.id}: {rule.when}",
                    citations=got[1],
                )
    for claim, cites in verified.flag_claims:
        node, rule = rules[claim.rule_id]
        if (claim.rule_id, claim.unit_id) in settled:
            continue  # code decided this rule from verified values
        drop = CLAIM_CHECKS.get(claim.rule_id)
        if drop and drop(run, claim.unit_id, cites):
            continue  # the claim's own verified quotes contradict it (D-064)
        if any(c.verified for c in cites):
            run.flag(
                kind="flag_rule",
                route=Route(rule.route),
                rule_id=rule.id,
                unit_id=claim.unit_id,
                detail=f"{rule.id}: {rule.when}",
                citations=cites,
            )
        elif cites:
            # Quoted but the quote fails the check: still blocks, as a reviewer flag (D-046).
            run.low_confidence(
                node, claim.unit_id, f"flag rule {rule.id} claimed without a verified quote", cites
            )
        # No quote at all: no evidence was offered, so the claim is not raised (D-060).
    if verified.injections:
        run.flag(
            kind="injection",
            route=Route.CLINICIAN_REVIEW,
            detail="the model reported text aimed at an AI reviewer; treated as data",
            citations=verified.injections,
        )
    return run.out
