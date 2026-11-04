"""Inbox: every case with its SLA clock, sorted by time left (PRD R1)."""

import pandas as pd
import streamlit as st
from common import banner, case_input, case_status, open_case, sidebar

from priorauth import reviewdesk as rd

ctx = sidebar()
banner()
st.title("Inbox")
st.caption(
    "Northwind Health Plan utilization management queue. Decision clocks: 72 hours expedited, "
    "7 days standard (CMS-0057-F). Overdue cases sort first."
)

arrivals = ctx.arrivals()
rows = []
for cid, run in ctx.runs.items():
    req = case_input(cid).request
    due = rd.sla_due(arrivals[cid], req.review_type)
    left = due - ctx.clock
    rows.append(
        {
            "Time left": rd.fmt_remaining(left),
            "Overdue": left.total_seconds() < 0,
            "Case": cid,
            "Policy": run.rec.policy_id,
            "Service": f"{req.service.code} {req.service.description[:60]}",
            "Member": req.member.synthetic_id,
            "Review": req.review_type,
            "Copilot route": rd.ROUTE_LABEL[run.rec.route],
            "Status": case_status(ctx.log, run.run_id),
            "_left": left.total_seconds(),
        }
    )
df = pd.DataFrame(rows).sort_values("_left")

c1, c2, c3 = st.columns(3)
route = c1.multiselect("Copilot route", list(rd.ROUTE_LABEL.values()))
policy = c2.multiselect("Policy", sorted(df["Policy"].unique()))
status = c3.multiselect("Status", ["New", "In review", "Done"])
if route:
    df = df[df["Copilot route"].isin(route)]
if policy:
    df = df[df["Policy"].isin(policy)]
if status:
    df = df[df["Status"].isin(status)]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Cases", len(df))
m2.metric("Overdue", int(df["Overdue"].sum()))
m3.metric("Approve-ready", int((df["Copilot route"] == "Approve-ready").sum()))
m4.metric("Done", int((df["Status"] == "Done").sum()))

shown = df.drop(columns=["_left"]).reset_index(drop=True)
event = st.dataframe(
    shown.style.apply(
        lambda r: ["color: #c62828; font-weight: 600" if r["Overdue"] else "" for _ in r], axis=1
    ),
    hide_index=True,
    width="stretch",
    on_select="rerun",
    selection_mode="single-row",
    column_config={"Overdue": st.column_config.CheckboxColumn("Overdue")},
)
st.caption("Select a row to open the case.")
picked = event.selection.rows if event else []
if picked:
    open_case(shown.iloc[picked[0]]["Case"])
