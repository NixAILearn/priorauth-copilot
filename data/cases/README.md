# Generated cases

Each folder is one synthetic case built from its spec in [`../case_specs/`](../case_specs/) by the generator ([design](../../docs/generator-design.md)). Every patient, clinician, organization and NPI is invented.

| File | What it is |
| --- | --- |
| `request.json` | The prior authorization request the copilot receives |
| `documents/D01.md …` | The clinical packet, one file per document |
| `label.json` | The expected answer: each criterion's status with document ID and verbatim quote |
| `prompts/` | The brief and per-document prompts the documents were written from |
| `manifest.json` | Hashes of the spec, prompts and text, so a changed spec shows as stale |

`python -m generator check` (also in CI) re-runs every check on every case here.

## Status

All 60 planned cases are written and pass `generator check`. The three demo cases below were written freehand; the other 57 reuse shared layouts for each document type (D-042).

## Demo cases

| Case | Service | Archetype | Expected route | What to look for |
| --- | --- | --- | --- | --- |
| CASE-021-01 | Hypoglossal nerve stimulator | Clean | Approve-ready | Every criterion met; AHI 38.0 with few central events; CPAP failure documented with refit and download |
| CASE-034-07 | Bilayer skin substitute | Missing documentation | Request info | Five weeks of weekly wound care, but no note says how the ulcer was offloaded |
| CASE-047-12 | Knee arthroscopic debridement | Clearly not met | Clinician review | Arthritis pain only: no locking or catching, full extension, no MRI |
