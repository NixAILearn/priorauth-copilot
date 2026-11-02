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


def _title(role: str) -> str:
    r = role.lower()
    if any(w in r for w in ("lab", "clinic", "supplier", "department")):
        return ""
    doctor = ("physician", "surgeon", "radiologist", "ologist", "hospitalist")
    return "Dr. " if any(w in r for w in doctor) else ""


def _fresh(seq: list[str], key: str, used: set[str]) -> str:
    """The pick for this key, re-salted until it is not already used."""
    name, salt = _pick(seq, key), 0
    while name in used:
        salt += 1
        name = _pick(seq, f"{key}|{salt}")
    used.add(name)
    return name


def patient_name(synthetic_id: str) -> str:
    """Stable and unique across the case set: earlier synthetic IDs keep their names."""
    n = int(synthetic_id.split("-")[1])
    taken: set[str] = set()
    full = ""
    for k in range(1, n + 1):
        sid = f"SYN-{k:04d}"
        first, last = _pick(FIRST, sid + "|p1"), _pick(LAST, sid + "|p2")
        salt = 0
        while f"{first} {last}" in taken:
            salt += 1
            last = _pick(LAST, f"{sid}|p2|{salt}")
        full = f"{first} {last}"
        taken.add(full)
    return full


def roster(case_id: str, patient: str, roles: list[str]) -> dict[str, str]:
    """A fictional name per author role; no first or last name repeats within a case."""
    first, last = patient.split(" ", 1)
    used_first, used_last = {first}, {last}
    out: dict[str, str] = {}
    for role in roles:
        if role in out:
            continue
        f = _fresh(FIRST, f"{case_id}|{role}|first", used_first)
        la = _fresh(LAST, f"{case_id}|{role}|last", used_last)
        out[role] = f"{_title(role)}{f} {la}"
    return out


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
