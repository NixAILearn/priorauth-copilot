"""Tests for scripts/scan_codes.py.

Code-shaped strings are built by concatenation so this file never contains a
literal one and passes its own scan.
"""

from __future__ import annotations

import json

import pytest
import scan_codes as sc

FIVE = "4" + "7" + "1" + "2" + "3"  # a five-digit token
CAT3 = "0" + "1" + "2" + "3" + "T"
CAT2 = "3" + "0" + "1" + "4" + "F"
DENTAL = "D" + "1" + "1" + "1" + "0"


def rules(text: str) -> list[str]:
    return [rule for _, _, rule in sc.scan_text(text)]


@pytest.mark.parametrize(
    "text, rule",
    [
        (f"Procedure {FIVE} was requested.", "cpt"),
        (f"Code {FIVE}.", "cpt"),
        (f"({FIVE})", "cpt"),
        (f"Tracking code {CAT3} on file", "cpt-cat2-3"),
        (f"Quality code {CAT2}", "cpt-cat2-3"),
        (f"Dental {DENTAL} cleaning", "cdt"),
        ("Rev code 0" + "450 billed", "ub04-rev"),
        ("revenue code: 0" + "360", "ub04-rev"),
    ],
)
def test_flags_code_shapes(text: str, rule: str) -> None:
    assert rule in rules(text)


@pytest.mark.parametrize(
    "text",
    [
        "Northwind code NHP-P-1042 under policy NHP-MP-021",
        "Diagnoses G47.33, E11.621, M17.11",
        "Effective 2026-01-01, decided 2026-11-01T17:09:14Z",
        "Synthetic NPI 1234567893",
        "LOINC 3" + "9156-5 recorded",
        "BMI 33.8; value 1" + "2345.6 ml",
        "CMS-0057-F and CMS-0062-P",
        "Vitals at 0800 and 1400",
        "Case id 3f2a" + "1234-9abc-4def-8123-1234" + "56789abc",
        "Decision D-004",
    ],
)
def test_ignores_safe_tokens(text: str) -> None:
    assert rules(text) == []


def test_json_skips_safe_codings_and_postal_codes() -> None:
    bundle = {
        "address": [{"postalCode": "0" + "1970"}],
        "code": {
            "coding": [
                {"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "1" + "9840"}
            ]
        },
        "valueQuantity": {"value": int(FIVE)},
    }
    assert list(sc.scan_json(bundle)) == []


def test_json_flags_banned_system_and_free_text() -> None:
    bundle = {
        "coding": [{"system": "http://www.ama-assn.org/go/cpt", "code": "x"}],
        "note": [{"text": f"Billed as {FIVE}"}],
    }
    found = {rule for _, _, rule in sc.scan_json(bundle)}
    assert found == {"coding", "cpt"}


def test_scan_file_and_allowlist(tmp_path) -> None:
    doc = tmp_path / "note.md"
    doc.write_text(f"Walked {FIVE} steps\n", encoding="utf-8")
    findings = sc.scan_file(doc, "data/cases/c1/note.md")
    assert [(f.location, f.token) for f in findings] == [("line 1", FIVE)]

    assert sc.is_allowed(findings[0], [("data/cases/*/note.md", FIVE)])
    assert not sc.is_allowed(findings[0], [("data/cases/*/note.md", "other")])


def test_malformed_json_falls_back_to_line_scan(tmp_path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text('{"text": "code ' + FIVE + '"', encoding="utf-8")
    assert [f.rule for f in sc.scan_file(bad, "bad.json")] == ["cpt"]


def test_valid_json_reports_json_path(tmp_path) -> None:
    good = tmp_path / "doc.json"
    good.write_text(json.dumps({"notes": ["ok", f"code {FIVE}"]}), encoding="utf-8")
    assert [f.location for f in sc.scan_file(good, "doc.json")] == ["$.notes[1]"]


def test_bad_allowlist_line_raises(tmp_path) -> None:
    allow = tmp_path / "allow.txt"
    allow.write_text("only-one-field\n", encoding="utf-8")
    with pytest.raises(ValueError):
        sc.load_allowlist(allow)
