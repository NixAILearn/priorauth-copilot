# PriorAuth Copilot: Case Generator Design (v0.1)

**Owner:** Nick · **Status:** Draft for review · **Updated:** 2026-11-02 · Input: [`data/case_specs/`](../data/case_specs/) · Output: [`data/cases/`](../data/cases/) · Decisions: D-033 to D-040 in [`decision-log.md`](decision-log.md)

The generator turns each of the 60 reviewed case specs into what the copilot will actually see: a request, a packet of clinical documents and, for the eval, a label file. The spec already fixes the answer, so the generator's only job is to write convincing text **around** fixed facts, then prove in code that the text says what the spec says and nothing that would change the answer.

**Terms used here.** *FHIR R4*: the HL7 standard format for health records; Synthea exports patients as FHIR "bundles" (one JSON file per patient). *PAS*: Da Vinci Prior Authorization Support, the FHIR guide for sending a PA request; we use a simplified PAS-style JSON, not a full bundle.

## 1. Pipeline, per case

```text
case spec ──► 1. Synthea background ──► 2. Sanitize ──► 3. Case brief
                                                            │
                     ┌──────────────────────────────────────┘
                     ▼
              4. Write each document (Claude) ──► 5. Check document ──► fail: retry (max 3)
                     │                                   │
                     │                                pass
                     ▼                                   ▼
              6. Insert injection text (code) ──► 7. Case-level checks ──► 8. Derive label ──► 9. Save
```

| Step | What happens | Who |
| --- | --- | --- |
| 1. Synthea background | Run Synthea for one patient with the spec's sex and an age range around the spec's birth date, seeded by case ID so reruns give the same patient | Code (Java 17+, Synthea jar, not committed) |
| 2. Sanitize | Keep only what can't change an answer: medications, routine labs, vitals history, immunizations and benign chronic conditions. Drop anything on the case's policy denylist (every contraindication and exclusion, plus any procedure or condition that touches a criterion). Overwrite birth date, sex and conditions from the spec. Replace Synthea names with names from a fictional list | Code (D-034) |
| 3. Case brief | One text block per case: patient summary, request, the sanitized record, the timeline of every document, and the rules every document must follow | Code |
| 4. Write each document | One Claude call per document. The prompt holds the case brief, this document's plan, the facts it must state with their anchors, every forbidden phrase in the case, and the noise to add | `claude-sonnet-5-5` via tool use, JSON output validated by Pydantic (D-035) |
| 5. Check document | Every anchor for this document appears verbatim; no forbidden phrase appears; no other value for a cited number; no date after the document's date; no licensed code shapes; length fits the plan | Code (D-036) |
| 6. Insert injection | For adversarial cases, the spec's injection text is inserted verbatim at a position chosen by code (in a paragraph, a footer or a header, by style) | Code (D-037) |
| 7. Case-level checks | Forbidden phrases absent from every document; each buried fact sits past the first third of a long document; documents read in date order; `scan_codes` passes on the whole case folder | Code |
| 8. Derive label | For each finding, each fact becomes a citation: document ID and the full sentence that holds the anchor. Contraindications and exclusions not listed in the spec are added as not found | Code (D-026) |
| 9. Save | `request.json`, `documents/D01.md …`, `label.json`, `manifest.json` under `data/cases/CASE-…/` | Code |

A case that fails step 5 three times for the same document, or fails step 7, is reported and left out of the run. Its spec is not changed by the generator; a person fixes the spec or the prompt.

## 2. What goes into each document prompt

1. **System prompt:** you write one synthetic clinical document for a fictional health plan's test set; every patient, clinician and organization is invented; write in the voice of the stated author; never write procedure billing codes; use ICD-10-CM codes only where given.
2. **Case brief:** shared by every document in the case, so the packet stays consistent (same patient, same clinicians, same timeline).
3. **This document's plan:** type, title, date, author role, length, guidance, noise.
4. **Must state:** each fact for this document, with its anchor phrase to be copied exactly, inside a natural sentence.
5. **Must not state:** every forbidden phrase in the case, plus each criterion's value guard (for example "no BMI other than 31.2 on this date").
6. **Output:** one tool call returning the document text in Markdown, with a header block (document type, date, author).

Each call is independent, which makes a failed document cheap to regenerate. Earlier documents are not fed into later prompts; the case brief carries what they share.

## 3. Outputs

```text
data/cases/CASE-021-01/
├── request.json      # simplified PAS-style request (schema in src/priorauth/schemas.py, D-038)
├── documents/
│   ├── D01.md        # one file per planned document, in the plan's order
│   └── ...
├── label.json        # Label (src/priorauth/case_spec.py), derived in step 8
└── manifest.json     # spec SHA-256, generator version, model, prompt SHA-256, Synthea seed, attempts per document
```

The `manifest.json` pins what produced each case. If a spec or prompt changes, the affected cases show as stale and are regenerated; nothing is silently reused. Generated cases are committed, because language model output is not reproducible run to run and the eval must run against the same text every time (D-039).

## 4. Commands

```text
python -m generator build CASE-021-01        # one case
python -m generator build --policy NHP-MP-034  # one service
python -m generator build --all              # everything stale or missing
python -m generator check                    # re-run steps 5 and 7 on committed cases, no API calls
make cases                                   # same as build --all
```

`generator check` runs in CI with no API key, so a hand edit to a generated document that breaks an anchor fails the build.

## 5. Rollout

1. Build the code path with a fake writer (fixed templates) so steps 5 to 9 are tested in CI without API calls.
2. Generate the three demo cases with Claude; Nick reads them end to end.
3. Generate the 10 smoke cases; spot-check, then the rest service by service.
4. Report token use and cost from the run's manifests, rather than estimating in advance.

## 6. Ambiguities and recommended readings

1. **What Synthea is for.** It can't produce our facts (dates, values, notes), and its random history can include a contraindication that silently breaks a label. Readings: drop Synthea; or use it for background only. **Recommended:** background only, sanitized against a denylist, and the generator still runs if Synthea is unavailable (D-034).
2. **One call per document or one per case.** One per case reads more consistently; one per document is cheaper to fix and simpler to check. **Recommended:** per document with a shared case brief (D-035).
3. **Who writes the injection text.** A model asked to write an injection may soften or refuse it. **Recommended:** code inserts the spec's text verbatim (D-037).
4. **Synthetic NPIs.** The kickoff asks for check-digit-valid NPIs (the 10-digit national provider identifier). Any valid-looking number could belong to a real clinician. **Recommended:** valid check digit but a leading digit of 9; issued NPIs start with 1 or 2, so a synthetic NPI cannot match a real one today (D-040).
5. **Commit generated text or regenerate on demand.** **Recommended:** commit (D-039).

## 7. What Nick needs to do

- **API key:** the generator calls Claude, and this cloud environment has no `ANTHROPIC_API_KEY`. Add it as an environment secret before step 2 of the rollout; steps 1 and `generator check` need no key.
- Review D-033 to D-040.

## 8. Next steps

1. Nick reviews this design and D-033 to D-040.
2. Build steps 1, 3 and 5 to 9 with the fake writer and tests (no key needed).
3. Add Synthea and the Claude writer; generate the three demo cases once the key is in place.
