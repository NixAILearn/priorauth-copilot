"""Generator checks (D-033 to D-041), run on packets built mechanically from the specs.

`fixture_docs` writes the plainest packet that could pass: front matter, filler sentences and
each anchor in its own sentence. If it passes, the checks accept a correct packet; each
mutation then shows one check catching one kind of mistake.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from generator import core, people
from priorauth.case_spec import load_case
from priorauth.schemas import PriorAuthRequest

FILLER = "Routine entry reviewed and unchanged from the prior visit."
ALL_IDS = [p.stem for p in sorted(core.SPECS.glob("CASE-*.json"))]


def fixture_docs(case) -> dict[str, str]:
    docs = {}
    for d in case.documents:
        lo, _ = core.WORDS[d.length]
        lead = [FILLER] * (lo // 8 + 2)
        facts = core.doc_facts(case, d)
        lines = [f"Note for {d.title}."]
        if d.length == "long" and any(f.placement == "buried" for f in facts):
            lines += lead
            lead = []
        lines += [f"Documented: {f.anchor}." for f in facts]
        lines += lead
        who = core.roster(case)[d.author_role]
        head = (
            f"---\ndoc_id: {d.id}\ntype: {d.type}\ntitle: {d.title}\n"
            f"date: {d.date.isoformat()}\nauthor: {who}, {d.author_role}\n---\n"
        )
        docs[d.id] = head + "\n\n".join(lines) + "\n"
    return core.insert_injection(case, docs)


def load(cid: str):
    case = load_case(core.SPECS / f"{cid}.json")
    return case, core.spec_for(case)


@pytest.mark.parametrize("cid", ALL_IDS)
def test_fixture_packet_passes_and_labels_build(cid):
    case, spec = load(cid)
    docs = fixture_docs(case)
    assert core.check_documents(case, spec, docs) == []
    label = core.build_label(case, spec, docs)
    for f in label.findings:
        for c in f.citations:
            if c.doc_id != core.REQUEST_DOC:
                assert core.norm(c.quote) in core.norm(docs[c.doc_id]), (f.node_id, c.quote)
    assert label.expected_route == case.expected_route


@pytest.mark.parametrize("cid", ALL_IDS)
def test_request_json_valid(cid):
    case, spec = load(cid)
    req = core.build_request(case, spec)
    PriorAuthRequest.model_validate_json(req.model_dump_json())
    assert people.npi_is_valid(req.requesting_provider.npi)
    assert req.requesting_provider.npi.startswith("9")
    assert req.requesting_provider.name in core.roster(case).values()  # requester wrote a document


def first_anchor_fact(case):
    return next(f for f in case.facts if f.anchor and f.doc_id.startswith("D"))


def test_missing_anchor_is_caught():
    case, spec = load("CASE-021-01")
    docs = fixture_docs(case)
    f = first_anchor_fact(case)
    docs[f.doc_id] = docs[f.doc_id].replace(f.anchor, f.anchor.upper() + "x")
    assert any(f"anchor for {f.id}" in e for e in core.check_documents(case, spec, docs))


def test_forbidden_phrase_is_caught():
    cid = next(c for c in ALL_IDS if core.forbidden_phrases(load(c)[0]))
    case, spec = load(cid)
    docs = fixture_docs(case)
    did = case.documents[0].id
    docs[did] += f"\nAlso: {core.forbidden_phrases(case)[0]}\n"
    assert any("forbidden phrase" in e for e in core.check_documents(case, spec, docs))


def test_future_date_is_caught():
    case, spec = load("CASE-021-01")
    docs = fixture_docs(case)
    d = case.documents[0]
    later = (d.date + timedelta(days=3)).strftime("%m/%d/%Y")
    docs[d.id] += f"\nFollow-up on {later}.\n"
    assert any("after the document date" in e for e in core.check_documents(case, spec, docs))


def test_unknown_guarded_value_is_caught():
    case, spec = load("CASE-021-01")
    docs = fixture_docs(case)
    docs["D03"] += "\nRepeat BMI 29.9 today.\n"
    assert any("value the spec does not know" in e for e in core.check_documents(case, spec, docs))


def test_code_shape_is_caught():
    case, spec = load("CASE-021-01")
    docs = fixture_docs(case)
    shape = "0" * 5  # built at runtime and never a real code, so this file passes its scan
    docs["D03"] += f"\nBilled as {shape}.\n"
    assert any("looks like" in e for e in core.check_documents(case, spec, docs))


def test_word_band_and_front_matter():
    case, spec = load("CASE-021-01")
    docs = fixture_docs(case)
    docs["D02"] = docs["D02"].replace("type: pap_usage_report", "type: note")
    docs["D02"] += " ".join([FILLER] * 80)
    errors = core.check_documents(case, spec, docs)
    assert any("front matter" in e for e in errors)
    assert any("outside the short band" in e for e in errors)


def test_injection_is_inserted_once():
    cid = next(c for c in ALL_IDS if load(c)[0].injection)
    case, _ = load(cid)
    once = fixture_docs(case)
    twice = core.insert_injection(case, once)
    assert twice == once
    assert once[case.injection.doc_id].count(case.injection.text) == 1


def test_sentence_for_picks_the_sentence_and_cell():
    text = "Seen today. Her BMI 31.2 was stable. Plan: follow up.\n| AHI | AHI 38.0 events/hour |\n"
    assert core.sentence_for(text, "BMI 31.2") == "Her BMI 31.2 was stable."
    assert core.sentence_for("Ms. Yardley is 65. Next.", "is 65") == "Ms. Yardley is 65."
    assert core.sentence_for(text, "AHI 38.0") == "AHI | AHI 38.0 events/hour"


def test_npi():
    npi = people.synthetic_npi("x")
    assert people.npi_is_valid(npi) and npi[0] == "9"
    assert not people.npi_is_valid(npi[:9] + str((int(npi[9]) + 1) % 10))
    # A published example NPI (CMS check-digit documentation): 123456789 -> 3.
    assert people.luhn_check_digit("80840123456789") == "3"


def test_sla():
    case, spec = load("CASE-021-01")
    req = core.build_request(case, spec)
    assert req.sla_due_at - req.received_at in (timedelta(hours=72), timedelta(days=7))


def test_value_guard_skips_dates_and_other_units():
    assert core.guarded_value("HbA1c drawn 05/21/2026.", 5)[0] is None
    assert core.guarded_value(" at 12 cm H2O: 22.0 events/hour", 0)[0] == 22.0


def test_bmi_must_match_weight_and_height():
    assert core.bmi_mismatch("Wt 217.8 lb, Ht 5'10\", BMI 31.2 kg/m2") is None
    assert core.bmi_mismatch("Wt 211 lb, Ht 5'10\", BMI 31.2 kg/m2") is not None
