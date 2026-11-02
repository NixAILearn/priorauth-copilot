#!/usr/bin/env python3
"""CI guard: fail if any repo file contains CPT-, CDT- or UB-04-style codes.

The project uses only invented Northwind codes (NHP-P-####) and public-domain
ICD-10-CM diagnosis codes. Licensed code sets must never appear. This scanner
looks for their *shapes*, so it errs toward false alarms; a false alarm is
cleared with an entry in scripts/scan_codes_allowlist.txt, never by weakening
the patterns.

What it flags
  cpt         five-digit numbers, e.g. a Category I code
  cpt-cat2-3  four digits followed by F, T or U (Category II, III, PLA shapes)
  cdt         D followed by four digits (dental code shape)
  ub04-rev    a four-digit, zero-led number after "rev"/"revenue code"
  coding      a FHIR coding whose system is a CPT, CDT or NUBC (UB-04) system

What it skips, on purpose
  numbers inside longer tokens (dates, NPIs, UUIDs, LOINC "12345-6", decimals);
  in JSON: numeric values, postalCode fields, and the code of a coding whose
  system is a known public one (LOINC, SNOMED CT, RxNorm, ICD-10, CVX, NHP).

Usage: python scripts/scan_codes.py [PATH ...]   (default: whole repo)
Exit code 0 = clean, 1 = findings, 2 = usage or read error.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_PATH = REPO_ROOT / "scripts" / "scan_codes_allowlist.txt"

# A code-shaped token must stand alone: not glued to letters, digits, or the
# separators used in dates, IDs, LOINC codes, times, URLs and decimals.
_BEFORE = r"(?<![\w.\-/:#])"
_AFTER = r"(?![\w\-/:]|\.\d)"

TEXT_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("cpt", re.compile(_BEFORE + r"(\d{5})" + _AFTER)),
    ("cpt-cat2-3", re.compile(_BEFORE + r"(\d{4}[FTU])" + _AFTER)),
    ("cdt", re.compile(_BEFORE + r"(D\d{4})" + _AFTER)),
    (
        "ub04-rev",
        re.compile(r"(?i)\brev(?:enue)?\.?\s*(?:code|cd)?\s*[:#]?\s*(0\d{3})" + _AFTER),
    ),
]

BANNED_SYSTEM_HINTS = ("ama-assn.org", "/cpt", "cpt-4", "ada.org", "/cdt", "nubc.org")
SAFE_SYSTEM_HINTS = (
    "loinc.org",
    "snomed.info",
    "nlm.nih.gov/research/umls/rxnorm",
    "hl7.org/fhir/sid/icd-10",
    "hl7.org/fhir/sid/cvx",
    "northwind",
)
SAFE_JSON_KEYS = {"postalCode"}

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules"}
MAX_BYTES = 50 * 1024 * 1024


@dataclass(frozen=True)
class Finding:
    path: str
    location: str  # "line 12" for text, a JSON path for JSON
    token: str
    rule: str

    def __str__(self) -> str:
        return f"{self.path}: {self.location}: {self.token!r} [{self.rule}]"


def scan_text(text: str) -> Iterator[tuple[int, str, str]]:
    """Yield (line_number, token, rule) for each code-shaped token in text."""
    for lineno, line in enumerate(text.splitlines(), start=1):
        for rule, pattern in TEXT_RULES:
            for match in pattern.finditer(line):
                yield lineno, match.group(1), rule


def _system_kind(system: str) -> str:
    s = system.lower()
    if any(h in s for h in BANNED_SYSTEM_HINTS):
        return "banned"
    if any(h in s for h in SAFE_SYSTEM_HINTS):
        return "safe"
    return "unknown"


def scan_json(obj: object, path: str = "$") -> Iterator[tuple[str, str, str]]:
    """Yield (json_path, token, rule) for code-shaped content in parsed JSON."""
    if isinstance(obj, dict):
        system = obj.get("system")
        kind = _system_kind(system) if isinstance(system, str) else None
        if kind == "banned":
            yield f"{path}.system", str(obj.get("code", system)), "coding"
        for key, value in obj.items():
            if key in SAFE_JSON_KEYS:
                continue
            if key == "code" and kind == "safe":
                continue
            yield from scan_json(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            yield from scan_json(item, f"{path}[{i}]")
    elif isinstance(obj, str):
        for _, token, rule in scan_text(obj):
            yield path, token, rule


def scan_file(path: Path, rel: str) -> list[Finding]:
    data = path.read_bytes()
    if len(data) > MAX_BYTES or b"\x00" in data[:8192]:
        return []  # binary or oversized: not authored text
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return []
    if path.suffix.lower() == ".json":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            pass  # malformed JSON falls back to a line scan
        else:
            return [Finding(rel, loc, tok, rule) for loc, tok, rule in scan_json(parsed)]
    return [Finding(rel, f"line {n}", tok, rule) for n, tok, rule in scan_text(text)]


def load_allowlist(path: Path = ALLOWLIST_PATH) -> list[tuple[str, str]]:
    """Each non-comment line: '<path glob> <token or *>  # reason'."""
    entries: list[tuple[str, str]] = []
    if not path.exists():
        return entries
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"bad allowlist line (want '<glob> <token>'): {raw!r}")
        entries.append((parts[0], parts[1]))
    return entries


def is_allowed(finding: Finding, allowlist: Iterable[tuple[str, str]]) -> bool:
    return any(
        fnmatch.fnmatch(finding.path, glob) and token in ("*", finding.token)
        for glob, token in allowlist
    )


def repo_files(root: Path) -> list[Path]:
    """Tracked plus untracked-not-ignored files when in Git; else a directory walk."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout
        return [root / p for p in out.decode().split("\0") if p and (root / p).is_file()]
    except (OSError, subprocess.CalledProcessError):
        files = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            files.extend(Path(dirpath) / f for f in filenames)
        return files


def expand(paths: list[str], root: Path) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            out.extend(f for f in repo_files(path))
        elif path.is_file():
            out.append(path)
        else:
            raise FileNotFoundError(p)
    return out


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    root = REPO_ROOT
    try:
        files = expand(argv, root) if argv else repo_files(root)
        allowlist = load_allowlist()
    except (FileNotFoundError, ValueError) as exc:
        print(f"scan_codes: {exc}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    for f in sorted(set(files)):
        try:
            rel = f.resolve().relative_to(root).as_posix()
        except ValueError:
            rel = f.as_posix()
        findings.extend(x for x in scan_file(f, rel) if not is_allowed(x, allowlist))

    if findings:
        print(f"scan_codes: {len(findings)} code-shaped token(s) found. Licensed code sets")
        print("(CPT, CDT, UB-04) must not appear. Remove them, or add a reviewed entry")
        print("with a reason to scripts/scan_codes_allowlist.txt.\n")
        for x in findings:
            print(f"  {x}")
        return 1
    print(f"scan_codes: clean ({len(files)} files scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
