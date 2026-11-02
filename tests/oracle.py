"""A perfect extractor built from the ground truth, for testing the deterministic pipeline.

It answers the extraction call with exactly what a flawless model would return for a
committed case: every fact in the case spec as a quoted value, every labeled fact-node status
with the label's citations, and every expected flag-rule claim. Running the pipeline on it
checks intake, quote checks, derivations, evaluation and routing against all 60 labels with no
API key. Injections are left to the code detector on purpose.
"""

from __future__ import annotations

import json
from pathlib import Path

from generator.core import sentence_for
from priorauth.case_spec import load_case as load_case_spec
from priorauth.extractor import fact_nodes, kind_of, model_fields
from priorauth.intake import load_case
from priorauth.quotes import date_in, norm

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "data" / "cases"
CASE_SPECS = ROOT / "data" / "case_specs"


def _fmt(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def _quote_for(doc: str, anchor: str, when) -> str:
    q = sentence_for(doc, anchor) or anchor
    if when is None or date_in(q, when):
        return q
    for line in norm(doc).splitlines():  # a date fact: quote the line that carries the date
        if date_in(line, when) and len(line.strip()) >= 10:
            return line.strip().strip("|").strip()
    return q


def oracle_output(case_id: str) -> dict:
    case = load_case(CASES / case_id)
    cs = load_case_spec(CASE_SPECS / f"{case_id}.json")
    label = json.loads((CASES / case_id / "label.json").read_text(encoding="utf-8"))
    spec, docs = case.spec, case.documents
    fields = {f.name: f for f in model_fields(spec)}
    facts = {f.id: f for f in cs.facts}

    values = []
    for f in cs.facts:
        fd = fields.get(f.field or "")
        if fd is None or f.doc_id == "DERIVED":
            continue
        is_date = fd.type == "date"
        value = f.date.isoformat() if is_date else _fmt(f.value)
        if f.doc_id == "REQUEST":
            quote = f"{f.field}: {f.date.isoformat() if is_date else _fmt(f.value)}"
        else:
            quote = _quote_for(docs[f.doc_id], f.anchor or "", f.date if is_date else None)
        values.append(
            {
                "field": f.field,
                "unit_id": f.unit_id,
                "value": value,
                "unit": f.unit,
                "observed_on": f.date.isoformat(),
                "period_start": None,
                "period_end": None,
                "record": f"{f.doc_id}:{f.anchor}",
                "doc_id": f.doc_id,
                "quote": quote,
            }
        )

    labeled = {(x["node_id"], x["unit_id"]): x for x in label["findings"]}
    kinds = kind_of(spec)
    assessments = []
    for node in fact_nodes(spec):
        for unit in [None] if node.per == "request" else case.unit_ids:
            x = labeled.get((node.id, unit))
            default = "insufficient" if kinds[node.id] == "criterion" else "not_found"
            assessments.append(
                {
                    "node_id": node.id,
                    "unit_id": unit,
                    "status": x["status"] if x else default,
                    "confidence": "high",
                    "citations": x["citations"] if x else [],
                    "rationale": "oracle",
                }
            )

    claims = []
    for fl in cs.flags:
        if fl.kind != "flag_rule":
            continue
        cites = []
        for fid in fl.facts:
            f = facts[fid]
            if f.doc_id in docs and f.anchor:
                cites.append(
                    {"doc_id": f.doc_id, "quote": _quote_for(docs[f.doc_id], f.anchor, None)}
                )
        claims.append(
            {
                "rule_id": fl.rule_id,
                "unit_id": fl.unit_id,
                "citations": cites,
                "rationale": fl.rationale,
            }
        )
    return {"values": values, "facts": assessments, "flag_rules": claims, "injections": []}
