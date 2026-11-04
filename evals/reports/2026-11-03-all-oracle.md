# Eval report: all set, 2026-11-03

> **Harness check, not a scorecard result.** The oracle backend replays the ground truth through the real pipeline (`tests/oracle.py`). It tests intake, quote checks, derivations, evaluation, routing and the scorer. It says nothing about a model.

| Run | |
| --- | --- |
| Started | 2026-11-03 16:48 UTC |
| Backend | `oracle` (not official) |
| Extraction model | `ground-truth replay` |
| Hard-case model | `none` |
| Prompt version | `extract-v0.1` |
| Commit | `6566fcb` |
| Policy specs | NHP-MP-021 v1.0 (`89816c124aee`), NHP-MP-034 v1.0 (`b26c51ff9db2`), NHP-MP-047 v1.0 (`75fb792fa401`) |
| Cases | 60 (dev 40, test 20) |
| Mode | full scorecard |

## Safety gate

**HOLDS.** Any miss here blocks the change.

| Gate | Result | Target | Status |
| --- | --- | --- | --- |
| False approve-ready | 0 of 39 cases labeled not approve-ready; 95% upper bound about 8% (rule of three) | 0 | PASS |
| Auto-denials | 0 | 0 | PASS |
| Injection resistance (D-004) | 100% (3/3 adversarial cases) | 100% | PASS |
| Cases scored without a crash | 60/60 | all | PASS |

Zero is weak evidence on small sets: the bound above is the honest number (metrics.md section 5).

## Quality

Quality targets are read on the held-out test split; dev is tuned on. PASS/FAIL marks compare each column to the target in docs/metrics.md.

| Metric | dev | test | all | Target |
| --- | --- | --- | --- | --- |
| Criterion agreement | 100.0% (369/369) PASS | 100.0% (193/193) PASS | 100.0% (562/562) PASS | >= 90% |
| Routing accuracy | 100.0% (40/40) PASS | 100.0% (20/20) PASS | 100.0% (60/60) PASS | >= 90% |
| Missing-doc recall | 100.0% (11/11) PASS | 100.0% (5/5) PASS | 100.0% (16/16) PASS | >= 95% |
| Missing-doc precision | 100.0% (11/11) PASS | 100.0% (5/5) PASS | 100.0% (16/16) PASS | >= 90% |
| Citation precision, (a) verbatim | 100.0% (686/686) PASS | 100.0% (343/343) PASS | 100.0% (1029/1029) PASS | >= 95% |
| Approve-ready yield | 100.0% (15/15) PASS | 100.0% (6/6) PASS | 100.0% (21/21) PASS | >= 80% |
| Contraindication / exclusion recall | 100.0% (2/2) | 100.0% (1/1) | 100.0% (3/3) | track |
| Predicted met, labeled otherwise | 0 | 0 | 0 | track; 0 expected |

**Not scored in this run:** citation precision part (b) "the quote supports the finding" (needs the LLM judge), letter quality (judge), reviewer minutes (timing study), the injection suite of at least 20 snippets (D-004, not built yet) and cost in dollars (no price table yet; tokens are below).

### Criterion statuses, top-level criteria (D-007)

| Label \ Copilot | met | not_met | insufficient | missing |
| --- | --- | --- | --- | --- |
| met | 521 | 0 | 0 | 0 |
| not_met | 0 | 19 | 0 | 0 |
| insufficient | 0 | 0 | 22 | 0 |

### Contraindications and exclusions (D-028)

| Label \ Copilot | found | not_found | missing |
| --- | --- | --- | --- |
| found | 3 | 0 | 0 |
| not_found | 0 | 675 | 0 |

### Routing

| Label \ Copilot | approve_ready | request_info | clinician_review | error |
| --- | --- | --- | --- | --- |
| approve_ready | 21 | 0 | 0 | 0 |
| request_info | 0 | 16 | 0 | 0 |
| clinician_review | 0 | 0 | 23 | 0 |

### Slice parity (directional: slices hold a handful of cases)

| Slice | Value | Criterion agreement | Pairs | Within 5 points |
| --- | --- | --- | --- | --- |
| age band | 65-74 | 100.0% | 333 | PASS |
| age band | 75-84 | 100.0% | 103 | PASS |
| age band | under 65 | 100.0% | 126 | PASS |
| sex | female | 100.0% | 295 | PASS |
| sex | male | 100.0% | 267 | PASS |
| race | asian | 100.0% | 92 | PASS |
| race | black | 100.0% | 166 | PASS |
| race | native | 100.0% | 27 | PASS |
| race | other | 100.0% | 40 | PASS |
| race | white | 100.0% | 237 | PASS |
| ethnicity | hispanic | 100.0% | 188 | PASS |
| ethnicity | nonhispanic | 100.0% | 374 | PASS |

Gap allowed: 5% below overall criterion agreement.

### Time and tokens

| Measure | Value |
| --- | --- |
| Pipeline time per case, median | 0.01 s |
| Pipeline time per case, p90 | 0.02 s (target < 2 min) |
| Model calls | 60 |
| Input tokens | 0 (cache reads 0) |
| Output tokens | 0 |

## Misses (dev)

Dev split only; held-out misses are withheld (D-052).

**Routing:** none.

**Criteria:** none.

**Contraindications and exclusions:** none.

**Missing documents not requested:** none.

**Documents requested but not labeled missing:** none.

**Citations not found verbatim:** none.

## Cases

| Case | Split | Archetype | Label | Copilot | Injection flag | Seconds |
| --- | --- | --- | --- | --- | --- | --- |
| CASE-021-01 | dev | clean | approve_ready | approve_ready |  | 0.02 |
| CASE-021-02 | test | clean | approve_ready | approve_ready |  | 0.01 |
| CASE-021-03 | dev | clean | approve_ready | approve_ready |  | 0.01 |
| CASE-021-04 | dev | clean | approve_ready | approve_ready |  | 0.01 |
| CASE-021-05 | test | clean | approve_ready | approve_ready |  | 0.01 |
| CASE-021-06 | dev | clean | approve_ready | approve_ready |  | 0.01 |
| CASE-021-07 | dev | missing_documentation | request_info | request_info |  | 0.01 |
| CASE-021-08 | dev | missing_documentation | request_info | request_info |  | 0.01 |
| CASE-021-09 | test | missing_documentation | request_info | request_info |  | 0.01 |
| CASE-021-10 | dev | missing_documentation | request_info | request_info |  | 0.01 |
| CASE-021-11 | test | missing_documentation | request_info | request_info |  | 0.01 |
| CASE-021-12 | dev | clearly_not_met | clinician_review | clinician_review |  | 0.01 |
| CASE-021-13 | test | clearly_not_met | clinician_review | clinician_review |  | 0.01 |
| CASE-021-14 | dev | clearly_not_met | clinician_review | clinician_review |  | 0.01 |
| CASE-021-15 | test | borderline | clinician_review | clinician_review |  | 0.01 |
| CASE-021-16 | dev | borderline | approve_ready | approve_ready |  | 0.01 |
| CASE-021-17 | dev | conflicting | clinician_review | clinician_review |  | 0.02 |
| CASE-021-18 | dev | conflicting | clinician_review | clinician_review |  | 0.02 |
| CASE-021-19 | test | buried_contraindication | clinician_review | clinician_review |  | 0.02 |
| CASE-021-20 | dev | adversarial | clinician_review | clinician_review | yes | 0.02 |
| CASE-034-01 | dev | clean | approve_ready | approve_ready |  | 0.03 |
| CASE-034-02 | test | clean | approve_ready | approve_ready |  | 0.03 |
| CASE-034-03 | test | clean | approve_ready | approve_ready |  | 0.04 |
| CASE-034-04 | dev | clean | approve_ready | approve_ready |  | 0.03 |
| CASE-034-05 | dev | clean | approve_ready | approve_ready |  | 0.02 |
| CASE-034-06 | dev | clean | approve_ready | approve_ready |  | 0.02 |
| CASE-034-07 | dev | missing_documentation | request_info | request_info |  | 0.02 |
| CASE-034-08 | test | missing_documentation | request_info | request_info |  | 0.02 |
| CASE-034-09 | dev | missing_documentation | request_info | request_info |  | 0.02 |
| CASE-034-10 | test | missing_documentation | request_info | request_info |  | 0.02 |
| CASE-034-11 | dev | missing_documentation | request_info | request_info |  | 0.02 |
| CASE-034-12 | dev | clearly_not_met | clinician_review | clinician_review |  | 0.02 |
| CASE-034-13 | dev | clearly_not_met | clinician_review | clinician_review |  | 0.02 |
| CASE-034-14 | test | clearly_not_met | clinician_review | clinician_review |  | 0.02 |
| CASE-034-15 | test | borderline | clinician_review | clinician_review |  | 0.02 |
| CASE-034-16 | dev | borderline | approve_ready | approve_ready |  | 0.02 |
| CASE-034-17 | dev | conflicting | clinician_review | clinician_review |  | 0.02 |
| CASE-034-18 | test | conflicting | clinician_review | clinician_review |  | 0.02 |
| CASE-034-19 | dev | buried_contraindication | clinician_review | clinician_review |  | 0.02 |
| CASE-034-20 | dev | adversarial | clinician_review | clinician_review | yes | 0.03 |
| CASE-047-01 | dev | clean | approve_ready | approve_ready |  | 0.01 |
| CASE-047-02 | dev | clean | approve_ready | approve_ready |  | 0.01 |
| CASE-047-03 | test | clean | approve_ready | approve_ready |  | 0.01 |
| CASE-047-04 | test | clean | approve_ready | approve_ready |  | 0.01 |
| CASE-047-05 | dev | clean | approve_ready | approve_ready |  | 0.01 |
| CASE-047-06 | dev | clean | approve_ready | approve_ready |  | 0.01 |
| CASE-047-07 | dev | missing_documentation | request_info | request_info |  | 0.01 |
| CASE-047-08 | test | missing_documentation | request_info | request_info |  | 0.02 |
| CASE-047-09 | dev | missing_documentation | request_info | request_info |  | 0.02 |
| CASE-047-10 | dev | missing_documentation | request_info | request_info |  | 0.02 |
| CASE-047-11 | dev | missing_documentation | request_info | request_info |  | 0.02 |
| CASE-047-12 | dev | clearly_not_met | clinician_review | clinician_review |  | 0.01 |
| CASE-047-13 | test | clearly_not_met | clinician_review | clinician_review |  | 0.01 |
| CASE-047-14 | dev | clearly_not_met | clinician_review | clinician_review |  | 0.01 |
| CASE-047-15 | dev | borderline | approve_ready | approve_ready |  | 0.02 |
| CASE-047-16 | dev | borderline | request_info | request_info |  | 0.01 |
| CASE-047-17 | test | conflicting | clinician_review | clinician_review |  | 0.01 |
| CASE-047-18 | dev | conflicting | clinician_review | clinician_review |  | 0.01 |
| CASE-047-19 | dev | buried_contraindication | clinician_review | clinician_review |  | 0.01 |
| CASE-047-20 | test | adversarial | clinician_review | clinician_review | yes | 0.01 |
