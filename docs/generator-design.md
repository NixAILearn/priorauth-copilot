# PriorAuth Copilot: Case Generator Design (v0.1)

**Owner:** Nick · **Status:** Accepted · **Updated:** 2026-11-02 (rev. 2: documents written in-session, D-041) · Input: [`data/case_specs/`](../data/case_specs/) · Output: [`data/cases/`](../data/cases/) · Decisions: D-033 to D-041 in [`decision-log.md`](decision-log.md)

The generator turns each of the 60 reviewed case specs into what the copilot will actually see: a request, a packet of clinical documents and, for the eval, a label file. The spec already fixes the answer, so the generator's only job is to write convincing text **around** fixed facts, then prove in code that the text says what the spec says and nothing that would change the answer.

**Terms used here.** *FHIR R4*: the HL7 standard format for health records; Synthea exports patients as FHIR "bundles" (one JSON file per patient). *PAS*: Da Vinci Prior Authorization Support, the FHIR guide for sending a PA request; we use a simplified PAS-style JSON, not a full bundle.

## 1. Pipeline, per case

```text
case spec ──► 1. Synthea background ──► 2. Sanitize ──► 3. Case brief
                                                            │
                     ┌──────────────────────────────────────┘
                     ▼
              4. Write each document (Claude, in-session) ──► 5. Check document ──► fail: rewrite
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
| 4. Write each document | `python -m generator brief CASE-…` renders the case brief and one writing prompt per document (plan, facts with anchors, forbidden phrases, value guards, noise). Claude, working in a Claude Code session, writes each document from its prompt into `documents/D01.md …` | Claude in-session, no API key (D-041) |
| 5. Check document | Every anchor for this document appears verbatim; no forbidden phrase appears; no other value for a cited number; no date after the document's date; no licensed code shapes; length fits the plan | Code (D-036) |
| 6. Insert injection | For adversarial cases, the spec's injection text is inserted verbatim at a position chosen by code (in a paragraph, a footer or a header, by style) | Code (D-037) |
| 7. Case-level checks | Forbidden phrases absent from every document; each buried fact sits past the first third of a long document; documents read in date order; `scan_codes` passes on the whole case folder | Code |
| 8. Derive label | For each finding, each fact becomes a citation: document ID and the full sentence that holds the anchor. Contraindications and exclusions not listed in the spec are added as not found | Code (D-026) |
| 9. Save | `request.json`, `documents/D01.md …`, `label.json`, `manifest.json` under `data/cases/CASE-…/` | Code |

A document that fails step 5 is rewritten from the same prompt; a case that still fails step 5 or step 7 is reported and left out of the run. Its spec is not changed by the generator; a person fixes the spec or the prompt.

## 2. What goes into each document prompt

1. **System prompt:** you write one synthetic clinical document for a fictional health plan's test set; every patient, clinician and organization is invented; write in the voice of the stated author; never write procedure billing codes; use ICD-10-CM codes only where given.
2. **Case brief:** shared by every document in the case, so the packet stays consistent (same patient, same clinicians, same timeline).
3. **This document's plan:** type, title, date, author role, length, guidance, noise.
4. **Must state:** each fact for this document, with its anchor phrase to be copied exactly, inside a natural sentence.
5. **Must not state:** every forbidden phrase in the case, plus each criterion's value guard (for example "no BMI other than 31.2 on this date").
6. **Output:** one tool call returning the document text in Markdown, with a header block (document type, date, author).

Each document is written from its own prompt, which keeps a rewrite local. The case brief carries what documents share (patient, clinicians, timeline). The prompts are committed next to the documents, so anyone can see exactly what each document was asked to say.

## 3. Outputs

```text
data/cases/CASE-021-01/
├── request.json      # simplified PAS-style request (schema in src/priorauth/schemas.py, D-038)
├── documents/
│   ├── D01.md        # one file per planned document, in the plan's order
│   └── ...
├── label.json        # Label (src/priorauth/case_spec.py), derived in step 8
├── prompts/          # the brief and per-document prompts the text was written from
└── manifest.json     # spec SHA-256, generator version, writer, prompt SHA-256 per document, Synthea seed if used
```

The `manifest.json` pins what produced each case. If a spec or prompt changes, the affected cases show as stale and are regenerated; nothing is silently reused. Generated cases are committed, because language model output is not reproducible run to run and the eval must run against the same text every time (D-039).

## 4. Commands

```text
python -m generator brief CASE-021-01        # step 3: write prompts/ for one case
python -m generator finalize CASE-021-01     # steps 5 to 9 once documents/ exist
python -m generator check                    # re-run steps 5 and 7 on every committed case
python -m generator status                   # which cases are missing, stale or done
make cases-check                             # same as check, used in CI
```

`generator check` runs in CI with no API key, so a hand edit to a generated document that breaks an anchor fails the build.

## 5. Rollout

1. Build steps 3 and 5 to 9 with tests (a tiny hand-written fixture case).
2. Write the three demo cases; Nick reads them end to end.
3. Write the rest service by service, one PR per service.
4. Synthea background (D-034) is added after the demo cases, only if the notes read thin without it.

## 6. Ambiguities and recommended readings

1. **What Synthea is for.** It can't produce our facts (dates, values, notes), and its random history can include a contraindication that silently breaks a label. Readings: drop Synthea; or use it for background only. **Recommended:** background only, sanitized against a denylist, and the generator still runs if Synthea is unavailable (D-034).
2. **One prompt per document or one per case.** One per case reads more consistently; one per document is simpler to check and to rewrite. **Recommended:** per document with a shared case brief (D-035, still applies to in-session writing).
3. **Who writes the injection text.** A model asked to write an injection may soften or refuse it. **Recommended:** code inserts the spec's text verbatim (D-037).
4. **Synthetic NPIs.** The kickoff asks for check-digit-valid NPIs (the 10-digit national provider identifier). Any valid-looking number could belong to a real clinician. **Recommended:** valid check digit but a leading digit of 9; issued NPIs start with 1 or 2, so a synthetic NPI cannot match a real one today (D-040).
5. **Commit generated text or regenerate on demand.** **Recommended:** commit (D-039).

## 7. What Nick needs to do

- Nothing for the generator: no API key is needed (D-041). The week 3 pipeline will need `ANTHROPIC_API_KEY`.
- Review D-033 to D-041.

## 8. Next steps

1. Nick reviews this design and D-033 to D-041.
2. Build steps 3 and 5 to 9 with tests.
3. Write the three demo cases.
