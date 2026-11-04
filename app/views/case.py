"""Case review: criteria checklist with cited evidence, overrides, letters, final action."""

from datetime import UTC, datetime

import streamlit as st
from common import CASES, banner, case_input, live_backend, sidebar

from priorauth import letters
from priorauth import reviewdesk as rd
from priorauth.audit import ACTIONS
from priorauth.schemas import Route

ctx = sidebar()
banner()

ids = sorted(ctx.runs)
if st.session_state.get("case_id") not in ids:
    st.session_state.case_id = ids[0]
case_id = st.selectbox("Case", ids, key="case_id")
run = ctx.runs[case_id]
rec = run.rec
case = case_input(case_id)
req, spec = case.request, case.spec
today = ctx.clock.date()
state = rd.ReviewState.from_rows(ctx.log.finding_reviews(run.run_id))
rows = rd.checklist(spec, rec, case.unit_ids)
row_by_key = {r.key: r for r in rows}

# --- Header ------------------------------------------------------------------------------------

st.title(f"{case_id} · {rd.ROUTE_LABEL[rec.route]}")
arrival = ctx.arrivals()[case_id]
left = rd.sla_due(arrival, req.review_type) - ctx.clock
h1, h2, h3, h4 = st.columns(4)
h1.metric("Copilot route", rd.ROUTE_LABEL[rec.route])
h2.metric("Time left (demo clock)", rd.fmt_remaining(left))
h3.metric("Policy", rec.policy_id, help=f"Version {rec.policy_version}")
h4.metric("Member", req.member.synthetic_id)
st.markdown(
    f"**Service** {req.service.code}, {req.service.description}  \n"
    f"**Diagnoses** {letters.diagnoses(req)}  \n"
    f"**Provider** {req.requesting_provider.name}, {req.requesting_provider.specialty}, "
    f"{req.requesting_provider.organization}  \n"
    f"**Received as submitted** {req.received_at:%Y-%m-%d %H:%M} ({req.review_type}); policy "
    "date windows are judged against this date."
)
with st.expander("Why the copilot routed it here", expanded=rec.route != Route.APPROVE_READY):
    for r in rec.reasons:
        st.markdown(f"- {r}")
    st.caption(
        f"Results from {ctx.snapshot.header.label}. The copilot never denies: a person takes "
        "every action below."
    )

backend = live_backend()
if st.button(
    "Re-run this case with the configured backend",
    disabled=backend is None,
    help="Needs PRIORAUTH_BACKEND (and a key where required). The hosted demo has none."
    if backend is None
    else f"Calls the pipeline on {backend}; a local model can take several minutes.",
):
    from priorauth.backends import make_client  # noqa: PLC0415
    from priorauth.config import load_config  # noqa: PLC0415
    from priorauth.pipeline import review_case  # noqa: PLC0415

    cfg = load_config()
    with st.spinner(f"Reviewing {case_id} on {cfg.backend}…"):
        review_case(CASES / case_id, make_client(cfg), ctx.log, official=cfg.official)
    st.rerun()


# --- Focus: which citation the document viewer shows ---------------------------------------


def focus(doc_id: str, quote: str) -> None:
    st.session_state[f"focus:{case_id}"] = (doc_id, quote)
    st.session_state[f"doc:{case_id}"] = doc_id


def cite_buttons(citations, key: str) -> None:
    for i, c in enumerate(citations):
        mark = "✓" if c.verified else "⚠️ not found in the document:"
        cols = st.columns([5, 1])
        text = rd.md_escape(c.quote) if c.verified else f"~~{rd.md_escape(c.quote)}~~"
        cols[0].markdown(f"{mark} **{c.doc_id}** “{text}”")
        cols[1].button("Show", key=f"{key}:{i}", on_click=focus, args=(c.doc_id, c.quote))


def review_controls(key: str, item_id: str, unit_id, status: str, kinds: list[str]) -> None:
    done = key in state.reviewed
    over = state.overrides.get(key)
    c1, c2 = st.columns([1, 1])
    if done:
        c1.success("Reviewed" + (f" · overridden to {rd.STATUS_LABEL[over[0]]}" if over else ""))
    elif c1.button("Mark reviewed", key=f"rev:{key}"):
        ctx.log.finding_review(
            run.run_id, ctx.reviewer, item_id, unit_id, status, status, "reviewed, agree"
        )
        st.rerun()
    if kinds:
        with c2.popover("Override"):
            with st.form(f"ov:{key}", clear_on_submit=True):
                new = st.selectbox(
                    "Reviewer status",
                    [k for k in kinds if k != status],
                    format_func=rd.STATUS_LABEL.get,
                )
                why = st.text_area("Reason (required)")
                if st.form_submit_button("Record override"):
                    if not why.strip():
                        st.error("An override needs a reason.")
                    else:
                        ctx.log.finding_review(
                            run.run_id, ctx.reviewer, item_id, unit_id, status, new, why
                        )
                        st.rerun()


ICON = {"met": "🟢", "not_found": "🟢", "insufficient": "🟡", "not_met": "🔴", "found": "🔴"}
UNIT = {u.id: f"{u.id} · {u.laterality} {u.site}" for u in req.service.target_ulcers}

left_col, right_col = st.columns([3, 2], gap="large")

with left_col:
    # --- Flags ------------------------------------------------------------------------------
    if rec.flags:
        st.subheader("Flags")
        for i, fl in enumerate(rec.flags):
            box = st.error if fl.kind in ("injection", "model_error") else st.warning
            unit = f" · {UNIT.get(fl.unit_id, fl.unit_id)}" if fl.unit_id else ""
            rule = f" {fl.rule_id}" if fl.rule_id else ""
            box(f"**{fl.kind.replace('_', ' ')}{rule}**{unit}: {rd.md_escape(fl.detail)}")
            cite_buttons(fl.citations, f"fl{i}")
            review_controls(rd.flag_key(i), rd.flag_key(i), fl.unit_id, fl.kind, [])

    # --- Checklist --------------------------------------------------------------------------
    st.subheader("Criteria checklist")
    st.caption(
        "Green met or not found, yellow insufficient evidence, red not met or found. Rows that "
        "are not green must be marked reviewed before a final action."
    )
    tops = [r for r in rows if r.top]
    for kind, title in (
        ("criterion", "Coverage criteria"),
        ("contraindication", "Contraindications"),
        ("exclusion", "Exclusions"),
    ):
        group = [r for r in tops if r.kind == kind]
        if not group:
            continue
        st.markdown(f"**{title}**")
        for top in group:
            over = state.overrides.get(top.key)
            unit = f" · {UNIT.get(top.unit_id, top.unit_id)}" if top.unit_id else ""
            label = (
                f"{ICON[top.status]} {top.node.section}{unit} · {top.node.summary} · "
                f"{rd.STATUS_LABEL[top.status]}"
                + (f" → reviewer: {rd.STATUS_LABEL[over[0]]}" if over else "")
                + (" · ✔ reviewed" if top.key in state.reviewed else "")
            )
            with st.expander(label, expanded=top.needs_review and top.key not in state.reviewed):
                start = rows.index(top)
                block = [top]
                for r in rows[start + 1 :]:
                    if r.top:
                        break
                    block.append(r)
                for r in block:
                    pad = "  " * r.depth
                    f = r.finding
                    st.markdown(
                        f"{pad}{ICON[r.status]} **{r.node.section}** {r.node.summary}: "
                        f"*{rd.STATUS_LABEL[r.status]}*"
                        + (f" (source: {f.source})" if f else " (not evaluated)")
                        + (
                            f"  \n{pad}Value compared: {rd.md_escape(f.value)}"
                            if f and f.value
                            else ""
                        )
                        + (f"  \n{pad}{rd.md_escape(f.note)}" if f and f.note else "")
                    )
                    if f and f.citations:
                        cite_buttons(f.citations, r.key)
                    ov = state.overrides.get(r.key)
                    if ov and r is not top:
                        st.info(
                            f"Reviewer override: {rd.STATUS_LABEL[ov[0]]} · {rd.md_escape(ov[1])}"
                        )
                with st.popover("Policy text"):
                    st.text(top.node.policy_text)
                kinds = (
                    ["met", "not_met", "insufficient"]
                    if kind == "criterion"
                    else ["found", "not_found"]
                )
                if over:
                    st.info(
                        f"Reviewer override: {rd.STATUS_LABEL[over[0]]} · {rd.md_escape(over[1])}"
                    )
                review_controls(top.key, top.node.id, top.unit_id, top.status, kinds)

with right_col:
    st.subheader("Documents")
    doc_ids = [d for d in case.documents if d != "REQUEST"] + ["REQUEST"]
    dkey = f"doc:{case_id}"
    if st.session_state.get(dkey) not in doc_ids:
        st.session_state[dkey] = doc_ids[0]
    doc_id = st.selectbox(
        "Document",
        doc_ids,
        key=dkey,
        format_func=lambda d: rd.doc_title(case.documents[d], d),
    )
    by_doc = rd.evidence_by_doc(rec)
    marks = [rd.Mark(c.quote, "evidence") for c in by_doc.get(doc_id, []) if c.verified]
    for fl in rec.flags:
        if fl.kind == "injection":
            marks += [rd.Mark(c.quote, "injection") for c in fl.citations if c.doc_id == doc_id]
    fdoc = st.session_state.get(f"focus:{case_id}")
    if fdoc and fdoc[0] == doc_id:
        marks.append(rd.Mark(fdoc[1], "focus"))
    body, missing = rd.document_html(case.documents[doc_id], marks)
    if fdoc and fdoc[0] == doc_id and any(m.style == "focus" for m in missing):
        st.warning("The selected quote is not in this document, so nothing is highlighted.")
    st.caption(
        "Shown as plain text: nothing inside a document is rendered or followed (D-072). "
        "Yellow: cited evidence. Orange: selected quote. Red dashed: possible injection."
    )
    st.html(body)

# --- Letters and final action -----------------------------------------------------------------

st.divider()
actions = ctx.log.actions(run.run_id)
pending = rd.pending_reviews(rows, rec.flags, state)
lc, ac = st.columns([3, 2], gap="large")

with lc:
    st.subheader("Drafts")
    draft = letters.draft_for(rec, req, spec, today)
    approved = next((a for a in actions if a["action"] == "approve"), None)
    if approved:
        text = letters.approval_notice(rec, req, spec, approved["reviewer"], today)
        st.text_area("Approval notice (draft)", text, height=360, key=f"ltr:{case_id}:ok")
        st.download_button("Download", text, file_name=f"{case_id}-approval.txt")
    elif draft:
        st.text_area(draft[0], draft[1], height=360, key=f"ltr:{case_id}")
        st.download_button("Download", draft[1], file_name=f"{case_id}-draft.txt")
    elif rec.route == Route.APPROVE_READY:
        st.caption("The approval notice is drafted after a reviewer approves.")
    else:
        st.caption(
            "No documentation items were identified, so there is no request-for-information "
            "draft. Write the request yourself if one is needed."
        )

with ac:
    st.subheader("Final action")
    if actions:
        last = actions[-1]
        st.success(
            f"Recorded: **{rd.ACTION_LABEL[last['action']]}** by "
            f"{rd.md_escape(last['reviewer'])} ({last['created_at'][:16].replace('T', ' ')} UTC). "
            f"Reason: {rd.md_escape(last['reason'])}"
        )
    if pending:
        st.info(
            f"Mark {len(pending)} item(s) reviewed first: "
            + ", ".join(
                (row_by_key[k].node.section if k in row_by_key else f"flag {k.split(':')[1]}")
                for k in pending
            )
        )
    with st.form(f"act:{case_id}"):
        choice = st.radio(
            "Action",
            rd.NURSE_ACTIONS,
            index=rd.NURSE_ACTIONS.index(rd.AGREEING_ACTION[rec.route]),
            format_func=rd.ACTION_LABEL.get,
            disabled=bool(pending),
        )
        why = st.text_area(
            "Reason (required when the action differs from the copilot's route)",
            disabled=bool(pending),
        )
        st.caption("There is no deny action. An adverse determination is a physician's decision.")
        if st.form_submit_button("Record action", disabled=bool(pending)):
            needs = rd.action_needs_reason(rec.route, choice)
            if needs and not why.strip():
                st.error("This action differs from the copilot's route: give a reason.")
            else:
                assert choice in ACTIONS
                ctx.log.reviewer_action(
                    run.run_id, ctx.reviewer, choice, why.strip() or "agree with copilot route"
                )
                st.rerun()

# --- Audit trail ------------------------------------------------------------------------------

with st.expander("Audit trail for this case"):
    events = [
        (
            r["created_at"],
            r["reviewer"],
            f"{r['kind']} {r['item_id']}"
            + (f" ({r['unit_id']})" if r["unit_id"] else "")
            + (f": {r['from_status']} → {r['to_status']}" if r["kind"] == "override" else ""),
            r["reason"],
        )
        for r in ctx.log.finding_reviews(run.run_id)
    ] + [(a["created_at"], a["reviewer"], f"action {a['action']}", a["reason"]) for a in actions]
    if not events:
        st.caption("Nothing recorded yet.")
    for at, who, what, why in sorted(events, reverse=True):
        st.markdown(
            f"`{at[:19].replace('T', ' ')}` **{rd.md_escape(who)}** {what} · {rd.md_escape(why)}"
        )
    st.caption(
        f"Run {run.run_id} · backend {run.backend} · viewed {datetime.now(UTC):%Y-%m-%d %H:%M} UTC"
    )
