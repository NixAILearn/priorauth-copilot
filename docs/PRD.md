# PriorAuth Copilot: Product Requirements (v0.1)

**Owner:** Nick · **Status:** Draft for review · **Updated:** 2026-11-01 · **Source:** Project Kickoff (Nov 1, 2026)

> Non-commercial educational demo. Northwind Health Plan, its medical policies, procedure codes and patients are fictional. Contains no real patient data and no CPT, CDT or UB-04 content. Not affiliated with or endorsed by CMS or any health plan.

## Problem

Before a plan pays for certain services, it requires **prior authorization (PA)**: the provider sends clinical documents, and the plan checks them against its written **medical policy** (the rules for when a service is covered). On the payer side this check is **utilization management (UM)**, done first by a nurse reviewer. Reviewers read long, unstructured charts against dense policy text under hard clocks: since Jan 1, 2026, CMS-0057-F requires Medicare Advantage plans to decide in **72 hours (expedited)** or **7 days (standard)** and to give a specific reason for any denial. The work is slow, inconsistent, and hard to audit.

## Solution

An AI copilot for Northwind Health Plan (fictional Medicare Advantage) that reads one PA request and its documents, checks each policy criterion, and gives the reviewer a **cited, criterion-by-criterion recommendation** plus a drafted letter. The model finds and quotes evidence; code verifies quotes, applies numeric rules, and routes. **It never denies.**

## Users

| Persona | Need |
| --- | --- |
| **Priya, UM nurse reviewer (primary)** | "Tell me fast whether this meets policy, and show me where in the chart." |
| Dr. Okafor, medical director | Only the hard cases, with a one-page brief. (The **medical director** is the plan physician who must sign any adverse decision.) |
| Marcus, provider PA coordinator (secondary) | "Tell me what's missing before I submit." |

## Goals and non-goals

**Goals:** (1) cut reviewer time per case while (2) never approving a case that fails policy, and (3) prove both with a reproducible eval on labeled synthetic cases.

**Non-goals:** real patient data, real payer or CMS policy text, licensed code sets, real payer/EHR integration, X12 278 transactions, drug PA, and any automated denial.

## Scope (MVP)

Services, all under fictional Northwind policies and codes: hypoglossal nerve stimulator for sleep apnea (NHP-MP-021, NHP-P-1042), skin substitute grafts for diabetic foot ulcers (NHP-MP-034, NHP-P-2017), arthroscopic debridement of the osteoarthritic knee (NHP-MP-047, NHP-P-3005). Stretch: epidural steroid injection (NHP-MP-052, NHP-P-4011).

| # | Requirement | Priority | Acceptance criterion |
| --- | --- | --- | --- |
| R1 | Case inbox with SLA clock | Must | Sorted by time remaining; overdue flagged |
| R2 | Policy compiled to versioned JSON criteria spec | Must | Each spec reviewed by Nick and versioned in Git |
| R3 | Evidence mapping per criterion: met / not met / insufficient / contraindicated | Must | Every finding has a document ID and a verbatim quote that code confirms; no quote = insufficient |
| R4 | Deterministic router: **approve-ready, request info, clinician review** | Must | Routing enum has no denial value (unit test) |
| R5 | Letter drafts: **request for information (RFI)**, the letter asking the provider for missing documents, and determination drafts | Must | Names the exact criterion, policy section and missing item |
| R6 | Reviewer override with required reason; audit log | Must | Every override and model call logged |
| R7 | Eval dashboard vs. ground-truth labels | Must | `make eval` runs all cases in one command |
| R8 | Provider pre-submission gap check | Should | Same engine, provider wording |

**Routing rules (code, not prompt):** *Approve-ready* only if every required criterion is met with a verified quote, no contraindication, and no flag (conflict, injection, low confidence). *Request info* if the only problems are insufficient evidence. *Clinician review* for everything else.

## Success metrics

Full tree and definitions in [`docs/metrics.md`](metrics.md).

- **Safety gate (must hold to ship any change):** 0 false approve-ready; 0 auto-denials; 100% injection resistance (D-004).
- **Quality targets:** criterion agreement ≥ 90%; missing-doc recall ≥ 95%; missing-doc precision ≥ 90%; citation precision ≥ 95%; approve-ready yield ≥ 80%.
- **North star:** approve-ready decisions per reviewer-hour, read only alongside the gate.

## Guardrails

Criteria come only from Northwind's reviewed specs. Clinical documents are data, never instructions; imperative text aimed at the AI is flagged. One patient per model context, no cross-patient statistics. A synthetic-data banner shows on every screen.

## Risks and open questions

1. **Over-escalation hides behind the gate.** A copilot that sends everything to clinician review scores 0% false approve-ready. Mitigation: an approve-ready yield counter-metric, target ≥ 80% (D-002).
2. **Small eval set.** 20 held-out cases give weak statistical evidence for "zero"; report counts and confidence bounds, not just rates.
3. **Policy ambiguity** (e.g. "symptoms other than pain alone" in NHP-MP-047) will be listed with a recommended reading during spec compilation, not resolved silently.

## Timeline

Six weeks part-time. Week 1: PRD, metrics, policies and reviewed specs (gate: all three specs reviewed). Weeks 2–6: case generator, pipeline, eval runner, Streamlit app, README. The safety gate after the pipeline phase is not moved past until it holds.
