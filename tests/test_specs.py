"""Checks that every criteria spec in policies/specs/ is valid and faithful to its policy."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import pytest

from priorauth.spec import CriteriaSpec, load_spec

ROOT = Path(__file__).resolve().parent.parent
SPECS = sorted((ROOT / "policies" / "specs").glob("NHP-MP-*.json"))


def normalize(text: str) -> str:
    """Drop Markdown bold markers and collapse whitespace, so quotes compare as plain text."""
    return re.sub(r"\s+", " ", text.replace("**", "")).strip()


@pytest.fixture(params=SPECS, ids=lambda p: p.stem)
def spec(request: pytest.FixtureRequest) -> CriteriaSpec:
    return load_spec(request.param)


def source_text(spec: CriteriaSpec) -> str:
    return (ROOT / spec.source_file).read_text(encoding="utf-8")


def policy_sections(spec: CriteriaSpec, prefix: str) -> set[str]:
    """Numbered items in the policy body (Appendix A excluded), e.g. 3.1 or 5.1.4."""
    body = source_text(spec).split("## Appendix A")[0]
    found = re.findall(r"^\*\*(\d+\.\d+(?:\.\d+)?)[ .*]", body, re.M)
    found += re.findall(r"^- \*\*(\d+\.\d+\.\d+)\*\*", body, re.M)
    return {s for s in found if s.startswith(prefix)}


def test_at_least_one_spec_exists() -> None:
    assert SPECS, "no specs in policies/specs/"


def test_spec_is_pinned_to_its_source(spec: CriteriaSpec) -> None:
    """A policy edit must be followed by a recompile and a fresh review."""
    digest = hashlib.sha256((ROOT / spec.source_file).read_bytes()).hexdigest()
    assert digest == spec.source_sha256, f"{spec.source_file} changed; recompile the spec"


def test_header_matches_source_front_matter(spec: CriteriaSpec) -> None:
    text = source_text(spec)
    assert f"policy_id: {spec.policy_id}" in text
    assert f'version: "{spec.policy_version}"' in text
    assert f"effective_date: {spec.effective_date.isoformat()}" in text
    assert spec.scope.service_code in text


def test_service_code_maps_to_this_policy(spec: CriteriaSpec) -> None:
    with (ROOT / "codes" / "nhp_procedures.csv").open(newline="", encoding="utf-8") as f:
        table = {r["code"]: r["policy_id"] for r in csv.DictReader(f)}
    assert table.get(spec.scope.service_code) == spec.policy_id


def test_diagnoses_match_section_2_2(spec: CriteriaSpec) -> None:
    text = source_text(spec)
    block = text.split("### 2.2")[1].split("### 2.3")[0]
    listed = re.findall(r"^\| ([A-Z]\d{2}(?:\.\w+)?) \|", block, re.M)
    assert sorted(listed) == sorted(spec.scope.primary_diagnoses + spec.scope.unit_diagnoses)


def test_every_policy_text_is_verbatim(spec: CriteriaSpec) -> None:
    source = normalize(source_text(spec).split("## Appendix A")[0])
    missing = [n.id for n in spec.nodes() if normalize(n.policy_text) not in source]
    assert not missing, f"policy_text not found verbatim in source: {missing}"


def test_ids_are_unique(spec: CriteriaSpec) -> None:
    ids = [n.id for n in spec.nodes()]
    ids += [r.id for n in spec.nodes() for r in n.flag_rules]
    ids += [a.id for a in spec.ambiguities]
    assert len(ids) == len(set(ids))


def test_every_policy_item_is_compiled(spec: CriteriaSpec) -> None:
    """Each numbered item in sections 3, 4 and 5 appears as a top-level spec node."""
    expected = {s for p in ("3.", "4.", "5.1.", "5.2.") for s in policy_sections(spec, p)}
    compiled = {n.section for n in (*spec.criteria, *spec.contraindications, *spec.exclusions)}
    assert expected == compiled


def test_fields_are_declared(spec: CriteriaSpec) -> None:
    declared = {f.name for f in spec.fields}
    used = {n.field for n in spec.nodes() if n.field}
    assert used <= declared, f"undeclared fields: {used - declared}"
    for f in spec.fields:
        assert set(f.derived_from) <= declared, f.name
        assert (f.evaluator == "code") == bool(f.derived_from), f.name


def test_documentation_covers_every_criterion(spec: CriteriaSpec) -> None:
    doc_ids = {d.id for d in spec.documentation}
    for node in spec.nodes():
        assert node.documentation, f"{node.id} names no documentation item"
        assert set(node.documentation) <= doc_ids, node.id
    supported = {s for d in spec.documentation for s in d.supports}
    for top in spec.criteria:
        # A doc item may support a lettered sub-item, e.g. "3.10(a)", which counts for 3.10.
        covered = any(s == top.section or s.startswith(f"{top.section}(") for s in supported)
        assert covered, f"{top.section} has no documentation item"


def test_no_deny_outcome_anywhere(spec: CriteriaSpec) -> None:
    raw = json.dumps(spec.model_dump(mode="json")).lower()
    assert '"deny' not in raw and "denial" not in raw


def test_per_unit_nodes_use_per_unit_fields(spec: CriteriaSpec) -> None:
    """A request-level node must not read a per-unit field, or the unit would be lost."""
    per = {f.name: f.per for f in spec.fields}
    for node in spec.nodes():
        if node.field and per[node.field] != "request":
            assert node.per == per[node.field], f"{node.id} reads per-unit field {node.field}"


def test_group_children_share_the_parent_unit(spec: CriteriaSpec) -> None:
    for node in spec.nodes():
        for child in node.children:
            assert child.per == node.per, f"{child.id} unit differs from {node.id}"
