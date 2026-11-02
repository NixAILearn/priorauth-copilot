# PriorAuth Copilot

> **Non-commercial educational demo.** Northwind Health Plan, its medical policies, procedure codes and patients are fictional. Contains no real patient data and no CPT, CDT or UB-04 content. Not affiliated with or endorsed by CMS or any health plan.

An AI utilization-review copilot. It reads a prior authorization request and its clinical documents, checks them against Northwind Health Plan's written medical policy, and gives a human nurse reviewer a cited, criterion-by-criterion recommendation. It never denies: the only outcomes are **approve-ready**, **request info** and **clinician review**.

**Status:** week 3. Policies, specs, 60 labeled cases and the review pipeline are in; the eval runner and scorecard come in week 4.

## Why

*Coming soon: the 40-requests-a-week problem, and CMS-0057-F decision clocks (72 hours expedited, 7 days standard).*

## Demo

*Coming soon: 30-second GIF.*

## What it does

*Coming soon.* See [`docs/PRD.md`](docs/PRD.md).

## Architecture

*Coming soon: diagram.*

## Results

*Coming soon: table from the latest report in `evals/reports/`.* Targets are in [`docs/metrics.md`](docs/metrics.md).

## Guardrails

- No denial path exists in code: three outcomes only.
- Criteria come only from Northwind's published policies, compiled into versioned JSON specs that are reviewed by hand.
- Every finding cites a document ID and a verbatim quote; no quote means "insufficient evidence".
- Text inside clinical documents is data, never instructions.
- CI fails on any CPT-, CDT- or UB-04-style code (`scripts/scan_codes.py`).

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make check   # lint, tests, code scan
```

### Review a case

The model backend is chosen by environment variable (D-044). Only `anthropic` runs count toward the scorecard; the others are for cheap or free development runs. Quote checks, derived values, thresholds and routing are code and behave the same on every backend.

| Backend | Set | Models |
| --- | --- | --- |
| `anthropic` (default) | `ANTHROPIC_API_KEY` | `claude-sonnet-5-5` extraction, `claude-opus-5-5` hard cases |
| `openrouter` | `OPENROUTER_API_KEY`, `PRIORAUTH_EXTRACT_MODEL` | any model with JSON-schema output |
| `lmstudio` | LM Studio server on `localhost:1234`, model loaded with at least a 32k context | Gemma 4 12B (`PRIORAUTH_EXTRACT_MODEL` must match `lms ls`) |

```bash
PRIORAUTH_BACKEND=lmstudio python -m priorauth review data/cases/CASE-021-01
python -m priorauth review data/cases/CASE-034-02 --audit runs.db --json
```

The tests need no key: they replay a perfect extractor built from the labels through the real pipeline (`tests/oracle.py`) and use a scripted fake client for retries, low confidence and adversarial behaviour.

## Data and disclaimer

All data is synthetic (Synthea FHIR R4 plus generated clinical notes) or invented (Northwind policies and `NHP-P-####` procedure codes). Diagnosis codes are ICD-10-CM, which is public domain.

This is a portfolio demonstration using a fictional health plan, its invented medical policies and synthetic patients. It is not a medical device, makes no coverage decisions, and must not be used with real patient data. In the real world, a Medicare Advantage plan must follow Medicare's national coverage determinations where they exist, and one exists for arthroscopic debridement of the osteoarthritic knee; Northwind's fictional world assumes none apply to its four services, and its policies are written independently (D-011, D-016).

## Repo map

| Path | Contents |
| --- | --- |
| `docs/` | PRD, metrics, decision log |
| `codes/` | Northwind procedure code table |
| `policies/source/`, `policies/specs/` | Northwind policies (Markdown) and reviewed criteria specs (JSON) |
| `data/` | Case specs, raw Synthea bundles, built cases with labels |
| `src/priorauth/` | Pipeline: intake, extractor, evaluator, router, letters, audit |
| `generator/` | Synthetic case builder |
| `evals/` | Eval runner and dated reports |
| `app/` | Streamlit pages |
| `scripts/` | CI guards |
| `tests/` | pytest suite |

## What's next

*Coming soon.*
