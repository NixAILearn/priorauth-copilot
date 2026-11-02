"""Fictional clinicians, organizations and synthetic NPIs, chosen deterministically per case.

Names are invented combinations, never real people. NPIs pass the standard check-digit test
but start with 9, a leading digit no issued NPI uses (D-040).
"""

from __future__ import annotations

import hashlib

FIRST = [
    "Amara",
    "Bastien",
    "Corinne",
    "Dashiell",
    "Elowen",
    "Farrukh",
    "Greer",
    "Hollis",
    "Ines",
    "Jory",
    "Kestrel",
    "Lucan",
    "Marisol",
    "Nadir",
    "Odile",
    "Pell",
    "Quilla",
    "Rosalind",
    "Soren",
    "Talia",
    "Umberto",
    "Vesna",
    "Wren",
    "Yusra",
    "Zeno",
]
LAST = [
    "Ardent",
    "Brightwater",
    "Calloway-Reyes",
    "Duvane",
    "Ellery",
    "Fenwick-Osei",
    "Galbrecht",
    "Holloway-Tan",
    "Iverholt",
    "Jessop",
    "Kittredge",
    "Lindqvist-Amari",
    "Marchetti-Lowe",
    "Northcote",
    "Ostrander",
    "Pemberly",
    "Quarrington",
    "Rasmussen-Vale",
    "Strathmore",
    "Thackeray-Ng",
    "Underhill",
    "Valcourt",
    "Whitlock-Abara",
    "Yardley",
]
PRIMARY_CARE = "Willow Street Primary Care"
# The requesting clinician is the case's author in this role, at this organization.
REQUESTER = {
    "Otolaryngology": ("Otolaryngologist", "Lakemont ENT Associates"),
    "Orthopedic surgery": ("Orthopedic surgeon", "Riverbend Orthopedics"),
    "Wound care": ("Wound care nurse practitioner", "Lakemont Wound Care Clinic"),
}


def _pick(seq: list[str], key: str) -> str:
    h = int(hashlib.sha256(key.encode()).hexdigest(), 16)
    return seq[h % len(seq)]


def clinician_name(case_id: str, role: str) -> str:
    """A stable fictional name for one author role within one case."""
    first = _pick(FIRST, f"{case_id}|{role}|first")
    last = _pick(LAST, f"{case_id}|{role}|last")
    title = (
        ""
        if any(w in role.lower() for w in ("lab", "clinic", "supplier", "department"))
        else (
            "Dr. "
            if any(
                w in role.lower()
                for w in ("physician", "surgeon", "radiologist", "ologist", "hospitalist")
            )
            else ""
        )
    )
    return f"{title}{first} {last}"


def luhn_check_digit(digits: str) -> str:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 0:
            d *= 2
            d = d - 9 if d > 9 else d
        total += d
    return str((10 - total % 10) % 10)


def synthetic_npi(key: str) -> str:
    """Ten digits starting with 9; the check digit uses the 80840 prefix as real NPIs do."""
    body = "9" + str(int(hashlib.sha256(key.encode()).hexdigest(), 16))[:8]
    return body + luhn_check_digit("80840" + body)


def npi_is_valid(npi: str) -> bool:
    return len(npi) == 10 and npi.isdigit() and luhn_check_digit("80840" + npi[:9]) == npi[9]
