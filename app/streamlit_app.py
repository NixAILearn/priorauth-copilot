"""PriorAuth Copilot reviewer app (week 5, docs/app-design.md). Run: make app."""

import streamlit as st

st.set_page_config(page_title="PriorAuth Copilot", page_icon="🩺", layout="wide")

pages = st.navigation(
    [
        st.Page("views/inbox.py", title="Inbox", icon="📥", default=True),
        st.Page("views/case.py", title="Case review", icon="🔎"),
        st.Page("views/director.py", title="Medical director", icon="🩺"),
        st.Page("views/evals.py", title="Eval dashboard", icon="📊"),
    ]
)
pages.run()
