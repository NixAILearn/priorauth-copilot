# Reviewer app: screens and rules (week 5)

The Streamlit app is the reviewer's view of the copilot. It never decides: it shows a recommendation with its evidence, and a person takes every action. Decisions D-068 to D-073 in [`decision-log.md`](decision-log.md).

Run it with `make app` (or `streamlit run app/streamlit_app.py`).

## Every screen

- A banner: synthetic data only, fictional plan, not a medical device, no real patient data.
- The snapshot in use: backend and model. The oracle snapshot says "ground-truth replay, not model output" (D-068).
- The demo clock (D-069).

## 1. Inbox (nurse reviewer)

| Column | Source |
| --- | --- |
| Time left | Demo-clock due time minus demo clock; overdue rows flagged and sorted first |
| Case, member, service, policy | Request and recommendation |
| Copilot route | approve-ready, request info, clinician review |
| Status | New, In review (any finding reviewed), Done (a final action was recorded) |

Filters: route, policy, status. Sorted by time left.

## 2. Case review

- **Header:** request facts (received date as submitted, review type, provider, service, diagnoses), copilot route and the reasons behind it.
- **Flags** first: injection, conflict, low confidence, flag rules, model error.
- **Criteria checklist:** the spec's tree with each finding's status, the value code compared, and its citations. Groups show their children indented. Per-ulcer criteria show one row per target ulcer.
- **Evidence:** selecting a citation opens the document with the quote highlighted (D-072). A failed quote is struck through and labeled.
- **Review:** each row that is not met, insufficient or found has a *Mark reviewed* control and an *Override* form (new status plus a required reason). Overrides sit beside the copilot's status and do not re-route (D-070).
- **Letters:** the request-for-information draft when there are missing items; the approval notice after an approval; the medical director brief for clinician review (D-071).
- **Final action:** Approve, Send request for information, Refer to medical director. Locked until every non-met row and every flag is reviewed. A reason is required when the action differs from the copilot's route. No deny control.
- **Audit trail:** every review, override and action on this case, newest first.

## 3. Medical director queue

Clinician-review cases only, each with its brief. The medical director can approve or record that the case left the copilot for a determination made outside it (with a reason). An adverse determination is written by the physician, not drafted by the app.

## 4. Eval dashboard

From the committed `evals/reports/*.json`: the safety gate (false approve-ready, auto-denials, injection resistance), the quality metrics against targets by split, time and tokens per case, and a per-case route table for dev cases only (D-052).

## Out of scope this week

The provider pre-submission gap check (D-073), uploads of any kind, and live model calls on the hosted demo.
