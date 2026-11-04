"""Hosted demo settings (D-078): requirements.txt matches the package's runtime dependencies."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_requirements_match_pyproject():
    deps = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["dependencies"]
    lines = (ROOT / "requirements.txt").read_text().splitlines()
    reqs = [ln.strip() for ln in lines if ln.strip() and not ln.startswith("#")]
    assert sorted(reqs) == sorted(deps)
