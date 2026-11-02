"""Checks on codes/nhp_procedures.csv, the Northwind procedure code table."""

from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path

TABLE = Path(__file__).resolve().parent.parent / "codes" / "nhp_procedures.csv"
COLUMNS = [
    "code", "short_name", "description", "policy_id", "scope", "setting",
    "unit_basis", "laterality_required", "pa_required", "effective_date", "end_date",
]


def rows() -> list[dict[str, str]]:
    with TABLE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == COLUMNS
        return list(reader)


def test_codes_are_northwind_format_and_unique() -> None:
    codes = [r["code"] for r in rows()]
    assert all(re.fullmatch(r"NHP-P-\d{4}", c) for c in codes)
    assert len(codes) == len(set(codes))


def test_each_code_maps_to_one_northwind_policy() -> None:
    for r in rows():
        assert re.fullmatch(r"NHP-MP-\d{3}", r["policy_id"]), r["code"]


def test_flags_and_dates_are_valid() -> None:
    for r in rows():
        assert r["scope"] in {"mvp", "stretch"}
        assert r["laterality_required"] in {"Y", "N"}
        assert r["pa_required"] in {"Y", "N"}
        start = date.fromisoformat(r["effective_date"])
        if r["end_date"]:
            assert date.fromisoformat(r["end_date"]) > start


def test_the_four_kickoff_services_are_present() -> None:
    pairs = {(r["code"], r["policy_id"]) for r in rows()}
    assert pairs == {
        ("NHP-P-1042", "NHP-MP-021"),
        ("NHP-P-2017", "NHP-MP-034"),
        ("NHP-P-3005", "NHP-MP-047"),
        ("NHP-P-4011", "NHP-MP-052"),
    }
