"""Smoke test the Streamlit pages and the review gate (docs/app-design.md)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py")
PAGES = ["views/inbox.py", "views/case.py", "views/director.py", "views/evals.py"]


@pytest.fixture(autouse=True)
def _state(tmp_path, monkeypatch):
    monkeypatch.setenv("PRIORAUTH_APP_STATE", str(tmp_path))
    monkeypatch.delenv("PRIORAUTH_BACKEND", raising=False)


def _page(page: str, **state) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=60)
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    at.switch_page(page)
    at.run()
    return at


@pytest.mark.parametrize("page", PAGES)
def test_page_renders_with_banner(page):
    at = _page(page)
    assert not at.exception, [e.value for e in at.exception]
    assert any("Synthetic data only" in w.value for w in at.warning)


def test_final_action_is_locked_until_flags_and_gaps_are_reviewed():
    at = _page("views/case.py", case_id="CASE-021-20")
    assert not at.exception
    submit = [b for b in at.button if b.label == "Record action"][0]
    assert submit.disabled
    while True:
        todo = [b for b in at.button if b.label == "Mark reviewed"]
        if not todo:
            break
        todo[0].click()
        at.run()
        assert not at.exception
    submit = [b for b in at.button if b.label == "Record action"][0]
    assert not submit.disabled
    labels = [o for r in at.radio for o in r.options]
    assert not [x for x in labels if "deny" in x.lower()]


def test_rerun_button_is_disabled_without_a_backend():
    at = _page("views/case.py", case_id="CASE-021-01")
    rerun = [b for b in at.button if b.label.startswith("Re-run")][0]
    assert rerun.disabled
