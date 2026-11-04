"""PriorAuth Copilot reviewer app (weeks 5 and 6, docs/app-design.md). Run: make app."""

import sys
from pathlib import Path

import streamlit as st

# Streamlit Community Cloud installs requirements.txt but not this package itself, so make the
# src/ layout importable when `priorauth` is not installed (D-078). A local `pip install -e .`
# is found first and this does nothing.
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

st.set_page_config(page_title="PriorAuth Copilot", page_icon="🩺", layout="wide")

pages = st.navigation(
    [
        st.Page("views/inbox.py", title="Inbox", icon="📥", default=True),
        st.Page("views/case.py", title="Case review", icon="🔎"),
        st.Page("views/director.py", title="Medical director", icon="🩺"),
        st.Page("views/provider.py", title="Provider gap check", icon="📋"),
        st.Page("views/evals.py", title="Eval dashboard", icon="📊"),
    ]
)
pages.run()
