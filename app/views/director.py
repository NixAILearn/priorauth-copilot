"""Medical director queue: clinician-review cases only, each with its brief (D-070, D-071)."""

import streamlit as st
from common import banner, case_input, case_status, open_case, sidebar

from priorauth import letters
from priorauth import reviewdesk as rd
from priorauth.schemas import Route

ctx = sidebar()
banner()
st.title("Medical director queue")
st.caption(
    "Cases the copilot could not mark approve-ready and sent for clinical judgment. The copilot "
    "does not draft adverse determinations: a physician makes and writes that decision."
)

queue = sorted(cid for cid, r in ctx.runs.items() if r.rec.route == Route.CLINICIAN_REVIEW)
if not queue:
    st.info("No clinician-review cases in this snapshot.")
    st.stop()
arrivals = ctx.arrivals()


def label(cid: str) -> str:
    req = case_input(cid).request
    left = rd.sla_due(arrivals[cid], req.review_type) - ctx.clock
    return f"{cid} · {ctx.runs[cid].rec.policy_id} · {rd.fmt_remaining(left)} left · " + (
        case_status(ctx.log, ctx.runs[cid].run_id)
    )


queue.sort(key=lambda c: arrivals[c])
cid = st.selectbox("Case", queue, format_func=label)
run = ctx.runs[cid]
case = case_input(cid)
brief = letters.md_brief(run.rec, case.request, case.spec, ctx.clock.date())

c1, c2 = st.columns([3, 2], gap="large")
with c1:
    st.text_area("Case brief", brief, height=520, key=f"brief:{cid}")
    st.download_button("Download brief", brief, file_name=f"{cid}-brief.txt")
    st.button("Open full case review", on_click=open_case, args=(cid,))
with c2:
    st.subheader("Record an outcome")
    actions = ctx.log.actions(run.run_id)
    for a in actions:
        st.success(
            f"{rd.ACTION_LABEL[a['action']]} by {rd.md_escape(a['reviewer'])}: "
            f"{rd.md_escape(a['reason'])}"
        )
    with st.form(f"md:{cid}", clear_on_submit=True):
        who = st.text_input("Medical director", value="Dr. Okafor, MD")
        choice = st.radio("Outcome", rd.MD_ACTIONS, format_func=rd.ACTION_LABEL.get)
        why = st.text_area("Reason (required)")
        st.caption(
            '"Determination made outside the copilot" records only that the case left the '
            "copilot. The copilot stores no adverse decision and drafts no denial letter."
        )
        if st.form_submit_button("Record"):
            if not why.strip():
                st.error("A reason is required.")
            else:
                ctx.log.reviewer_action(run.run_id, who.strip() or "Medical director", choice, why)
                st.rerun()
