"""Provider pre-submission gap check: the same engine in provider wording (PRD R8, D-077)."""

import streamlit as st
from common import banner, case_input, live_backend, sidebar

from priorauth import gapcheck
from priorauth import reviewdesk as rd
from priorauth.schemas import Route

ctx = sidebar()
banner()
st.title("Provider gap check")
st.caption(
    "For the practice's prior authorization coordinator: check a draft packet against the "
    "Northwind medical policy before you submit, so it is not pended for missing records."
)

ids = sorted(ctx.runs)
if st.session_state.get("gap_case") not in ids:
    st.session_state.gap_case = "CASE-034-07" if "CASE-034-07" in ids else ids[0]


def label(cid: str) -> str:
    req = case_input(cid).request
    return f"{cid} · {req.service.code} {req.service.description[:50]} · {req.member.synthetic_id}"


cid = st.selectbox("Draft packet", ids, key="gap_case", format_func=label)
case = case_input(cid)
req, spec = case.request, case.spec
report = gapcheck.gap_check(ctx.runs[cid].rec, req, spec)

st.markdown(
    f"**Service** {req.service.code}, {req.service.description}  \n"
    f"**Policy** {spec.policy_id} version {spec.policy_version}  \n"
    f"**Documents in the packet** {len(case.documents) - 1}"
)
if live_backend() is None:
    st.caption(
        "The hosted demo checks the committed sample packets from "
        f"{ctx.snapshot.header.label}. Checking a new upload needs a live model backend (D-077)."
    )

box = {
    Route.APPROVE_READY: st.success,
    Route.REQUEST_INFO: st.warning,
    Route.CLINICIAN_REVIEW: st.info,
}[report.route]
box(f"**{report.headline}.** {report.outlook}")

c1, c2 = st.columns([3, 2], gap="large")
with c1:
    st.subheader("Add before you submit")
    if not report.to_send:
        st.markdown("Nothing to add from the policy's documentation list.")
    for s in report.to_send:
        st.markdown(
            f"**{rd.md_escape(s.name)}** · item {s.item}, supports {', '.join(s.sections)}  \n"
            f"Must show: {rd.md_escape(s.must_show)}"
        )
    if report.gaps:
        st.subheader("Criteria not shown as the policy requires")
        for g in report.gaps:
            st.markdown(
                f"- **{g.section}{rd.md_escape(g.unit)}** {rd.md_escape(g.summary)}. *{g.words}.*"
            )
with c2:
    st.subheader("Checklist to copy")
    text = report.checklist()
    st.text_area("Checklist", text, height=360, key=f"gap:{cid}", label_visibility="collapsed")
    st.download_button("Download checklist", text, file_name=f"{cid}-precheck.txt")
    st.caption(
        "This check never predicts a denial. Only a Northwind physician can make an adverse "
        "determination, after reviewing the full record."
    )
