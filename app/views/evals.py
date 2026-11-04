"""Eval dashboard: the committed scorecards against the targets in docs/metrics.md (D-073)."""

import json

import pandas as pd
import streamlit as st
from common import banner, sidebar

from priorauth.intake import ROOT

REPORTS = ROOT / "evals" / "reports"
TARGETS = {  # docs/metrics.md
    "criterion_agreement": ("Criterion agreement", 0.90),
    "routing_accuracy": ("Routing accuracy", 0.90),
    "missing_doc_recall": ("Missing-doc recall", 0.95),
    "missing_doc_precision": ("Missing-doc precision", 0.90),
    "citation_precision_verbatim": ("Citation precision, verbatim (part a)", 0.95),
    "approve_ready_yield": ("Approve-ready yield", 0.80),
}

sidebar()
banner()
st.title("Eval dashboard")

reports = sorted(REPORTS.glob("*.json"), reverse=True)
if not reports:
    st.info("No reports in evals/reports/. Run `make eval-oracle`.")
    st.stop()


def describe(p) -> str:
    d = json.loads(p.read_text(encoding="utf-8"))
    run = d["run"]
    kind = (
        "harness check"
        if run["backend"] == "oracle"
        else ("scorecard" if run.get("official") else "dev run")
    )
    return f"{p.stem} · {run['extract_model']} · {kind}"


path = st.selectbox("Report", reports, format_func=describe)
d = json.loads(path.read_text(encoding="utf-8"))
o, run = d["overall"], d["run"]
if run["backend"] == "oracle":
    st.info(
        "Harness check: the ground truth replayed through the real pipeline. Not a model score."
    )
st.caption(
    f"Set {d['set']} · backend {run['backend']} · model {run['extract_model']} · prompt "
    f"{d['prompt_version']} · commit {d['commit']} · started {d['started'][:16]}"
)

st.subheader("Safety gate " + ("holds ✅" if o["gate_passed"] else "FAILS ❌"))
g1, g2, g3, g4 = st.columns(4)
g1.metric(
    "False approve-ready",
    len(o["false_approve_ready"]),
    help=f"95% upper bound on the rate: {o['false_approve_upper_95']:.1%}",
)
g2.metric("Auto-denials", len(o["auto_denials"]))
g3.metric("Injection resistance", f"{o['injection_resistance']:.0%}")
g4.metric("Unscorable cases", len(o["errors"]))
if d.get("model_errors"):
    st.warning(f"Model errors (routed to clinician review): {', '.join(d['model_errors'])}")

st.subheader("Quality against targets")
splits = d.get("by_split", {})
table = []
for key, (name, target) in TARGETS.items():
    row = {"Metric": name}
    for s in ("dev", "test"):
        v = splits.get(s, {}).get(key)
        row[f"{s.title()} %"] = None if v is None else round(100 * v, 1)
    row["All %"] = None if o.get(key) is None else round(100 * o[key], 1)
    row["Target"] = f"≥ {target:.0%}"
    judged = splits.get("test", {}).get(key, o.get(key))  # targets are read on test
    row["Meets on test"] = "✅" if (judged or 0) >= target else "—"
    table.append(row)
st.dataframe(pd.DataFrame(table), hide_index=True, width="stretch")
st.caption(
    "Quality targets are judged on the held-out test split; the gate is read on all cases. "
    "Citation part (b), letter quality and the injection suite are not scored yet."
)

if o.get("median_seconds") is not None:
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Median time per case", f"{o['median_seconds']:.0f} s")
    t2.metric("p90 time per case", f"{o['p90_seconds']:.0f} s")
    t3.metric("Input tokens", f"{o['input_tokens']:,}")
    t4.metric("Output tokens", f"{o['output_tokens']:,}")

st.subheader("Dev cases")
st.caption("Held-out test cases are reported as counts only (D-052).")
dev = [c for c in d["cases"] if c["split"] == "dev"]
df = pd.DataFrame(
    [
        {
            "Case": c["case_id"],
            "Archetype": c["archetype"],
            "Expected": c["expected_route"],
            "Copilot": c["route"],
            "Right": "✅" if c["route"] == c["expected_route"] else "✗",
            "Seconds": c.get("seconds"),
        }
        for c in dev
    ]
)
st.dataframe(df, hide_index=True, width="stretch")
test = [c for c in d["cases"] if c["split"] == "test"]
if test:
    right = sum(c["route"] == c["expected_route"] for c in test)
    st.caption(f"Test split: {right} of {len(test)} routes match the labels.")
