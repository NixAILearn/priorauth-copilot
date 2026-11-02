"""Case generator: prompts, document checks, label derivation and the request JSON.

Flow per case (docs/generator-design.md, D-033 to D-041):
  brief     -> data/cases/CASE-…/prompts/  (case brief plus one prompt per document)
  (Claude writes data/cases/CASE-…/documents/D01.md … from the prompts)
  finalize  -> inserts any injection text, runs every check, writes request.json, label.json,
               manifest.json
  check     -> re-runs the checks and rebuilds label and request for every committed case

Nothing here changes a case spec. A case that fails a check is reported, never patched.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

from generator import people
from priorauth.case_spec import (
    DERIVED_DOC,
    REQUEST_DOC,
    CaseSpec,
    Citation,
    DocPlan,
    Fact,
    Label,
    LabelFinding,
    check_case,
    load_case,
)
from priorauth.schemas import SLA, PriorAuthRequest
from priorauth.spec import CriteriaSpec, load_spec

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "data" / "case_specs"
CASES = ROOT / "data" / "cases"
POLICY_SPECS = ROOT / "policies" / "specs"
GENERATOR_VERSION = "0.1.0"
WRITER = "claude-code-session"  # D-041

sys.path.insert(0, str(ROOT / "scripts"))
from scan_codes import scan_text  # noqa: E402

WORDS = {"short": (60, 450), "medium": (180, 1100), "long": (450, 2600)}
# Numeric fields whose keyword in the text must only ever be followed by a value the spec
# knows (D-036). Values for the same field anywhere in the case are allowed.
VALUE_GUARDS: dict[str, tuple[str, tuple[str, ...]]] = {
    "bmi_recorded": (r"\bBMI\b", ("bmi_recorded", "bmi")),
    "ahi": (r"\b(?:AHI|REI)\b", ("ahi", "titration_residual_ahi", "pap_device_residual_ahi")),
    "hba1c_pct": (r"\b(?:HbA1c|A1c)\b", ("hba1c_pct",)),
    "kl_grade_reported": (r"Kellgren[- ]Lawrence grade", ("kl_grade_reported",)),
}
DATE_US = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
DATE_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def norm(text: str) -> str:
    """Whitespace and quote-mark normalization only (metrics.md citation rule)."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[ \t]+", " ", text)


def spec_for(case: CaseSpec) -> CriteriaSpec:
    return load_spec(POLICY_SPECS / f"{case.policy_id}.json")


def case_dir(case_id: str) -> Path:
    return CASES / case_id


# --- people and the request ------------------------------------------------------------------


def patient_name(case: CaseSpec) -> str:
    return people.patient_name(case.patient.synthetic_id)


def roster(case: CaseSpec) -> dict[str, str]:
    roles = [d.author_role for d in case.documents]
    if case.request.requesting_specialty in people.REQUESTER:
        roles.append(people.REQUESTER[case.request.requesting_specialty][0])
    return people.roster(case.case_id, patient_name(case), roles)


def build_request(case: CaseSpec, spec: CriteriaSpec) -> PriorAuthRequest:
    r = case.request
    received = datetime.combine(r.request_date, time(9, 0))
    role, org = people.REQUESTER[r.requesting_specialty]
    data = {
        "request_schema_version": "1.0",
        "request_id": f"NHP-PA-{case.case_id[5:].replace('-', '')}",
        "received_at": received.isoformat(),
        "review_type": r.review_type,
        "sla_due_at": (received + SLA[r.review_type]).isoformat(),
        "member": {
            "synthetic_id": case.patient.synthetic_id,
            "birth_date": case.patient.date_of_birth.isoformat(),
            "sex": case.patient.sex,
        },
        "requesting_provider": {
            "name": roster(case)[role],
            "npi": people.synthetic_npi(f"{case.case_id}|{role}"),
            "specialty": r.requesting_specialty,
            "organization": org,
        },
        "service": {
            "code": r.service_code,
            "description": r.service_details,
            "side": r.requested_side,
            "target_ulcers": [u.model_dump() for u in r.target_ulcers],
            "units": sum(u.applications_planned for u in r.target_ulcers) or 1,
        },
        "diagnoses": [{"code": r.primary_diagnosis, "role": "primary"}]
        + [{"code": c, "role": "secondary"} for c in r.secondary_diagnoses]
        + [{"code": u.diagnosis, "role": "secondary"} for u in r.target_ulcers],
        "attachments": [d.id for d in case.documents],
    }
    return PriorAuthRequest.model_validate(data)


# --- prompts ---------------------------------------------------------------------------------


def forbidden_phrases(case: CaseSpec) -> list[str]:
    return sorted({p for f in case.findings for m in f.missing for p in m.forbidden_phrases})


def guards(case: CaseSpec) -> list[str]:
    out = []
    for field, (_, group) in VALUE_GUARDS.items():
        vals = sorted(
            {f.value for f in case.facts if f.field in group and isinstance(f.value, int | float)}
        )
        if vals:
            label = (
                field.replace("_recorded", "").replace("_pct", "").replace("_reported", "").upper()
            )
            out.append(
                f"{label}: the only values allowed anywhere in the packet are {', '.join(str(v) for v in vals)}"
            )
    return out


def render_brief(case: CaseSpec) -> str:
    r = case.request
    people_ = roster(case)
    lines = [
        f"# Case brief: {case.case_id}",
        "",
        "You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a "
        "fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. "
        "The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.",
        "",
        "## Patient",
        f"- Name: {patient_name(case)} (synthetic ID {case.patient.synthetic_id})",
        f"- Date of birth: {case.patient.date_of_birth.strftime('%m/%d/%Y')}; sex: {case.patient.sex}",
        f"- Background diagnoses (ICD-10-CM): {', '.join(case.patient.background_conditions) or 'none'}",
        f"- Summary: {case.patient.summary}",
        "",
        "## Request",
        f"- Received {r.request_date.strftime('%m/%d/%Y')} ({r.review_type} review); service {r.service_code}: {r.service_details}",
        f"- Diagnoses: {', '.join([r.primary_diagnosis, *r.secondary_diagnoses])}",
    ]
    if r.requested_side:
        lines.append(f"- Requested side: {r.requested_side} knee")
    for u in r.target_ulcers:
        lines.append(
            f"- Target ulcer {u.id}: {u.laterality} {u.site} ({u.diagnosis}), {u.applications_planned} applications"
        )
    lines += ["", "## Clinicians (use these names and nobody else)"]
    lines += [f"- {role}: {name}" for role, name in people_.items()]
    lines += [
        "",
        "## Documents in this packet, by date",
        "",
        "| ID | Date | Type | Title | Author |",
        "| --- | --- | --- | --- | --- |",
    ]
    for d in sorted(case.documents, key=lambda d: d.date):
        lines.append(
            f"| {d.id} | {d.date.strftime('%m/%d/%Y')} | {d.type} | {d.title} | {people_[d.author_role]} |"
        )
    lines += [
        "",
        "## Rules for every document",
        "1. Write in the voice of the stated author, as a real clinical record of that type would read.",
        "2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, "
        "and keep each anchor on one line.",
        "3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. "
        "No ZIP codes, phone numbers or other five-digit numbers.",
        "4. No date later than the document's own date. Write dates as MM/DD/YYYY.",
        "5. Never use any phrase in the forbidden list, in any form.",
        "6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra "
        "diagnoses, procedures, devices, allergies or test results that touch the policy.",
    ]
    for n, g in enumerate(guards(case), start=7):
        lines.append(f"{n}. {g}.")
    fp = forbidden_phrases(case)
    lines += [
        "",
        "## Forbidden phrases (whole packet)",
        ", ".join(f'"{p}"' for p in fp) if fp else "none",
    ]
    return "\n".join(lines) + "\n"


def doc_facts(case: CaseSpec, doc: DocPlan) -> list[Fact]:
    seen: set[str] = set()
    out = []
    for f in case.facts:
        if f.doc_id == doc.id and f.anchor and f.anchor not in seen:
            seen.add(f.anchor)
            out.append(f)
    return out


def render_doc_prompt(case: CaseSpec, doc: DocPlan) -> str:
    who = roster(case)[doc.author_role]
    lines = [
        f"# {case.case_id} / {doc.id}: {doc.title}",
        "",
        f"- Type: {doc.type}; date: {doc.date.strftime('%m/%d/%Y')}; author: {who} ({doc.author_role})",
        f"- Length: {doc.length} ({WORDS[doc.length][0]} to {WORDS[doc.length][1]} words)",
        f"- Noise to include: {', '.join(doc.noise) or 'none'}",
        f"- What it covers: {doc.guidance}",
        "",
        "## Must state (copy each anchor exactly)",
    ]
    for f in doc_facts(case, doc):
        where = (
            " Place it past the first third of the document, among routine entries."
            if f.placement == "buried"
            else ""
        )
        note = f" (Distractor: {f.distractor})" if f.distractor else ""
        lines.append(f'- "{f.anchor}": {f.statement}{where}{note}')
    if case.injection and case.injection.doc_id == doc.id:
        lines += [
            "",
            "Leave room for an inserted passage; the generator adds it. Do not write anything like it yourself.",
        ]
    lines += [
        "",
        "## Output format",
        "```",
        "---",
        f"doc_id: {doc.id}",
        f"type: {doc.type}",
        f"title: {doc.title}",
        f"date: {doc.date.isoformat()}",
        f"author: {who}, {doc.author_role}",
        "---",
        "<document body in Markdown>",
        "```",
    ]
    return "\n".join(lines) + "\n"


def write_prompts(case: CaseSpec) -> Path:
    out = case_dir(case.case_id) / "prompts"
    out.mkdir(parents=True, exist_ok=True)
    (out / "brief.md").write_text(render_brief(case), encoding="utf-8")
    for d in case.documents:
        (out / f"{d.id}.md").write_text(render_doc_prompt(case, d), encoding="utf-8")
    return out


# --- documents -------------------------------------------------------------------------------


def read_docs(case: CaseSpec) -> dict[str, str]:
    folder = case_dir(case.case_id) / "documents"
    return (
        {p.stem: p.read_text(encoding="utf-8") for p in sorted(folder.glob("D*.md"))}
        if folder.exists()
        else {}
    )


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if ": " in line)
    return meta, text[m.end() :]


def insert_injection(case: CaseSpec, docs: dict[str, str]) -> dict[str, str]:
    """D-037: the spec's injection text goes in verbatim, placed by style. Idempotent."""
    inj = case.injection
    if inj is None or inj.doc_id not in docs or inj.text in docs[inj.doc_id]:
        return docs
    meta_text = docs[inj.doc_id]
    m = re.match(r"^---\n.*?\n---\n", meta_text, re.S)
    head, body = (meta_text[: m.end()], meta_text[m.end() :]) if m else ("", meta_text)
    if inj.style in ("system_prompt_mimic", "fake_approval"):
        body = f"\n{inj.text}\n\n" + body.lstrip("\n")
    elif inj.style == "hidden_footer":
        body = body.rstrip("\n") + f"\n\n{inj.text}\n"
    else:
        paras = body.split("\n\n")
        k = max(1, len(paras) // 2)
        body = "\n\n".join([*paras[:k], inj.text, *paras[k:]])
    return {**docs, inj.doc_id: head + body}


def find_line(text: str, anchor: str) -> str | None:
    for line in norm(text).splitlines():
        if anchor in line:
            return line
    return None


ABBREVIATION_END = re.compile(r"(?:^|\s)(?:Dr|Mr|Mrs|Ms|St|vs|approx|e\.g|i\.e)\.$")


def sentence_for(text: str, anchor: str) -> str | None:
    """The full sentence (or table cell, or list item) that holds the anchor."""
    line = find_line(text, anchor)
    if line is None:
        return None
    # A table row: quote the whole row, so the value keeps its label.
    if line.strip().startswith("|"):
        return line.strip().strip("|").strip()
    cells = [part.strip() for part in line.split(" · ")]
    for cell in cells:
        if anchor not in cell:
            continue
        parts: list[str] = []
        for piece in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"(])", cell):
            if parts and ABBREVIATION_END.search(parts[-1]):
                parts[-1] += " " + piece  # "Ms. Yardley ..." is one sentence
            else:
                parts.append(piece)
        for part in parts:
            if anchor in part:
                q = re.sub(r"^\s*(?:[-*]\s+|#+\s+|\d+\.\s+)", "", part).replace("**", "").strip()
                return q if anchor in q else part.strip()
        return cell.strip()
    return line.strip()


def parse_dates(text: str) -> list[date]:
    out = []
    for m, d, y in DATE_US.findall(text):
        try:
            out.append(date(int(y), int(m), int(d)))
        except ValueError:
            pass
    for y, m, d in DATE_ISO.findall(text):
        try:
            out.append(date(int(y), int(m), int(d)))
        except ValueError:
            pass
    return out


GUARD_SKIP_UNITS = re.compile(r"\s*(?:cm\b|mm\s*Hg|days?\b|nights?\b)")


def guarded_value(body: str, start: int) -> tuple[float | None, str]:
    """The first number within a short reach after a guarded keyword, skipping numbers that
    carry another unit (for example the pressure in "AHI at 12 cm H2O: 22.0")."""
    tail = body[start : start + 40].split("\n", 1)[0]
    for m in re.finditer(r"(?<![A-Za-z])\d+(?:\.\d+)?", tail):
        if GUARD_SKIP_UNITS.match(tail, m.end()):
            continue
        if m.start() > 24:
            break
        return float(m.group(0)), tail[: m.end()]
    return None, ""


WT_LB = re.compile(r"\bWt (\d+(?:\.\d+)?) lb")
WT_KG = re.compile(r"\bWt (\d+(?:\.\d+)?) kg")
HT_FTIN = re.compile(r"\bHt (\d)'(\d{1,2})\"")
HT_IN = re.compile(r"\bHt (\d+(?:\.\d+)?) in\b")
HT_CM = re.compile(r"\bHt (\d+(?:\.\d+)?) cm\b")
BMI_ON_LINE = re.compile(r"\bBMI (\d+(?:\.\d+)?)")


def bmi_mismatch(line: str) -> str | None:
    """A line that gives weight, height and BMI must agree with itself (within 0.15)."""
    bmi = BMI_ON_LINE.search(line)
    if not bmi:
        return None
    kg = WT_KG.search(line)
    lb = WT_LB.search(line)
    weight_kg = float(kg.group(1)) if kg else float(lb.group(1)) * 0.45359237 if lb else None
    m = None
    if (h := HT_FTIN.search(line)) is not None:
        m = (int(h.group(1)) * 12 + int(h.group(2))) * 0.0254
    elif (h := HT_IN.search(line)) is not None:
        m = float(h.group(1)) * 0.0254
    elif (h := HT_CM.search(line)) is not None:
        m = float(h.group(1)) / 100
    if weight_kg is None or m is None:
        return None
    calc = weight_kg / m**2
    if abs(calc - float(bmi.group(1))) > 0.15:
        return (
            f"BMI {bmi.group(1)} does not match the weight and height on the same line ({calc:.1f})"
        )
    return None


def check_documents(case: CaseSpec, spec: CriteriaSpec, docs: dict[str, str]) -> list[str]:
    """D-036 checks on the written packet. Returns every problem found."""
    errors: list[str] = []
    err = errors.append
    plans = {d.id: d for d in case.documents}
    if set(docs) != set(plans):
        missing, extra = sorted(set(plans) - set(docs)), sorted(set(docs) - set(plans))
        if missing:
            err(f"missing documents: {missing}")
        if extra:
            err(f"documents not in the plan: {extra}")
    forbidden = [p.lower() for p in forbidden_phrases(case)]
    values: dict[str, set[float]] = {}
    for f in case.facts:
        if f.field and isinstance(f.value, int | float) and not isinstance(f.value, bool):
            values.setdefault(f.field, set()).add(float(f.value))
    for did, text in docs.items():
        plan = plans.get(did)
        if plan is None:
            continue
        meta, body = split_front_matter(text)
        if (
            meta.get("doc_id") != did
            or meta.get("type") != plan.type
            or meta.get("date") != plan.date.isoformat()
        ):
            err(
                f"{did}: front matter must give doc_id {did}, type {plan.type}, date {plan.date.isoformat()}"
            )
        n = len(re.findall(r"\b\w+\b", body))
        lo, hi = WORDS[plan.length]
        if not lo <= n <= hi:
            err(f"{did}: {n} words, outside the {plan.length} band {lo}-{hi}")
        low = norm(text).lower()
        for p in forbidden:
            if p in low:
                err(f"{did}: contains forbidden phrase '{p}'")
        for d in parse_dates(body):
            if d > plan.date:
                err(f"{did}: mentions {d.isoformat()}, after the document date")
        for line in body.splitlines():
            problem = bmi_mismatch(line)
            if problem:
                err(f"{did}: {problem}")
        for lineno, token, rule in scan_text(body):
            err(f"{did}: line {lineno}: '{token}' looks like a {rule} code")
        for _field, (kw, group) in VALUE_GUARDS.items():
            allowed = set().union(*(values.get(g, set()) for g in group))
            if not allowed:
                continue
            for m in re.finditer(kw, body):
                v, shown = guarded_value(body, m.end())
                if v is not None and v not in allowed:
                    err(f"{did}: '{m.group(0)}{shown}' gives a value the spec does not know")
    for f in case.facts:
        if f.doc_id in (REQUEST_DOC, DERIVED_DOC) or not f.anchor or f.doc_id not in docs:
            continue
        text = docs[f.doc_id]
        line = find_line(text, f.anchor)
        if line is None:
            err(f"{f.doc_id}: anchor for {f.id} not found verbatim: '{f.anchor}'")
            continue
        if f.placement == "buried" and plans[f.doc_id].length == "long":
            pos = norm(text).find(f.anchor)
            if pos < len(norm(text)) / 3:
                err(f"{f.doc_id}: buried fact {f.id} sits in the first third of the document")
    if (
        case.injection
        and case.injection.doc_id in docs
        and case.injection.text not in docs[case.injection.doc_id]
    ):
        err(f"{case.injection.doc_id}: injection text missing")
    errors.extend(f"spec: {e}" for e in check_case(case, spec))
    return errors


# --- label -----------------------------------------------------------------------------------


def citations(
    case: CaseSpec, fact_ids: list[str], docs: dict[str, str], request: PriorAuthRequest
) -> list[Citation]:
    facts = {f.id: f for f in case.facts}
    out: list[Citation] = []
    seen: set[tuple[str, str]] = set()

    def add(doc_id: str, quote: str) -> None:
        if (doc_id, quote) not in seen:
            seen.add((doc_id, quote))
            out.append(Citation(doc_id=doc_id, quote=quote))

    def walk(fid: str) -> None:
        f = facts[fid]
        if f.doc_id == DERIVED_DOC:
            for src in f.derived_from:
                walk(src)
        elif f.doc_id == REQUEST_DOC:
            v = f.value if f.value is not None else f.date.isoformat()
            if isinstance(v, float) and v.is_integer():
                v = int(v)
            add(REQUEST_DOC, f"{f.field}: {v}")
        else:
            q = sentence_for(docs[f.doc_id], f.anchor or "")
            if q:
                add(f.doc_id, q)

    for fid in fact_ids:
        walk(fid)
    return out


def build_label(case: CaseSpec, spec: CriteriaSpec, docs: dict[str, str]) -> Label:
    request = build_request(case, spec)
    findings = [
        LabelFinding(
            node_id=f.node_id,
            unit_id=f.unit_id,
            status=f.status,
            citations=citations(case, f.facts, docs, request),
            missing=f.missing,
        )
        for f in case.findings
    ]
    have = {(f.node_id, f.unit_id) for f in case.findings}
    units = [u.id for u in case.request.target_ulcers]
    for node in (*spec.contraindications, *spec.exclusions):
        for unit in [None] if node.per == "request" else units:
            if (node.id, unit) not in have:
                findings.append(LabelFinding(node_id=node.id, unit_id=unit, status="not_found"))
    return Label(
        label_schema_version="1.0",
        case_id=case.case_id,
        policy_id=case.policy_id,
        policy_version=case.policy_version,
        archetype=case.archetype,
        split=case.split,
        expected_route=case.expected_route,
        findings=findings,
        flags=case.flags,
    )


def manifest(case: CaseSpec, docs: dict[str, str]) -> dict:
    spec_text = (SPECS / f"{case.case_id}.json").read_text(encoding="utf-8")
    return {
        "case_id": case.case_id,
        "generator_version": GENERATOR_VERSION,
        "writer": WRITER,
        "case_spec_sha256": sha256(spec_text),
        "brief_sha256": sha256(render_brief(case)),
        "documents": {
            d.id: {
                "prompt_sha256": sha256(render_doc_prompt(case, d)),
                "text_sha256": sha256(docs[d.id]),
            }
            for d in case.documents
            if d.id in docs
        },
        "synthea_seed": None,
    }


def dump(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def finalize(case_id: str) -> list[str]:
    case = load_case(SPECS / f"{case_id}.json")
    spec = spec_for(case)
    docs = insert_injection(case, read_docs(case))
    folder = case_dir(case_id)
    for did, text in docs.items():
        (folder / "documents" / f"{did}.md").write_text(text, encoding="utf-8")
    errors = check_documents(case, spec, docs)
    if errors:
        return errors
    write_prompts(case)
    dump(folder / "request.json", json.loads(build_request(case, spec).model_dump_json()))
    dump(folder / "label.json", json.loads(build_label(case, spec, docs).model_dump_json()))
    dump(folder / "manifest.json", manifest(case, docs))
    return []


def verify(case_id: str) -> list[str]:
    """CI check for a committed case: still matches its spec, checks pass, outputs rebuild."""
    case = load_case(SPECS / f"{case_id}.json")
    spec = spec_for(case)
    folder = case_dir(case_id)
    docs = read_docs(case)
    errors = check_documents(case, spec, docs)
    try:
        man = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [*errors, "manifest.json missing: run finalize"]
    want = manifest(case, docs)
    if man["case_spec_sha256"] != want["case_spec_sha256"]:
        errors.append("stale: the case spec changed after generation")
    for did, entry in want["documents"].items():
        if man["documents"].get(did, {}).get("prompt_sha256") != entry["prompt_sha256"]:
            errors.append(f"stale: the prompt for {did} changed after generation")
    for name, obj in (
        ("label.json", build_label(case, spec, docs)),
        ("request.json", build_request(case, spec)),
    ):
        on_disk = json.loads((folder / name).read_text(encoding="utf-8"))
        if on_disk != json.loads(obj.model_dump_json()):
            errors.append(f"{name} does not match what the spec and documents give; run finalize")
    return errors


def status() -> dict[str, str]:
    out = {}
    for p in sorted(SPECS.glob("CASE-*.json")):
        folder = case_dir(p.stem)
        if not (folder / "manifest.json").exists():
            out[p.stem] = (
                "documents written, not finalized"
                if (folder / "documents").exists()
                else ("prompts ready" if (folder / "prompts").exists() else "missing")
            )
        else:
            out[p.stem] = "stale" if verify(p.stem) else "done"
    return out


_ = timedelta  # keep import for callers computing SLA windows
