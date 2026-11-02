---
# Northwind medical policy template, v1.0. Copy to NHP-MP-###.md and fill in.
# Files starting with "_" are never compiled into criteria specs.
policy_id: NHP-MP-000
title: "<Service> for <condition>"
version: "1.0"
effective_date: 2026-01-01
status: draft            # draft | published | retired
line_of_business: Medicare Advantage
service_codes: [NHP-P-0000]   # must exist in codes/nhp_procedures.csv
review_type: prior authorization required
owner: Northwind Medical Policy Committee
next_review: 2027-01-01
---

<!--
HOW TO WRITE A NORTHWIND POLICY (delete this block in a real policy)

Ground rules
- Every word is original. Clinical facts come from general medical knowledge;
  never paste or paraphrase sentence-by-sentence from a real CMS or payer policy.
- No CPT, CDT or UB-04 codes or descriptions. Services are named only by their
  Northwind code (NHP-P-####). ICD-10-CM diagnosis codes are allowed.
- The policy states when the service is covered. It never tells a reviewer or a
  system to deny. Anything not clearly met goes to a person.

Write so the compiler can turn each line into one JSON criterion
1. One testable fact per numbered criterion. If you write "and", split it.
2. Numbers: one threshold per criterion, with a unit, using only these words:
     "at least" = >=   "more than" = >   "no more than" = <=   "less than" = <
   Never "over", "under", "up to", "approximately".
3. Time windows are anchored to a named date from section 7, e.g.
   "within 24 months before the request date". Never "recent".
4. Section numbers are stable IDs. 3.2 always means the same criterion within a
   version; a renumber is a new version and goes in the revision history.
5. Groups say their logic in the lead-in: "All of the following" or
   "Any one of the following". Sub-items are lettered (a), (b), (c).
6. Every term a reviewer could read two ways is defined in section 7 and written
   in bold where it is used.
7. Every criterion in sections 3 and 4 is backed by at least one documentation
   item in section 6 ("Supports: 3.2"), so a gap maps to a specific missing item.
8. Put doubts in Appendix A, not in the policy text: thresholds you are unsure
   are clinically plausible, and wording you expect to be ambiguous.
-->

# NHP-MP-000: <Service> for <condition>

**Northwind Health Plan · Medical Policy · Version 1.0 · Effective 2026-01-01**

> Fictional policy for a non-commercial demo. Northwind Health Plan is not a real health plan. This document is not medical advice and does not describe any real payer's coverage.

## 1. Policy statement

<One or two sentences, plain language: what the service is and that Northwind covers it when the criteria in sections 3 and 4 are met and nothing in section 5 applies. Requests that do not clearly meet the criteria are reviewed by a Northwind clinician.>

## 2. Scope

### 2.1 Service

| Northwind code | Service |
| --- | --- |
| NHP-P-0000 | <Name, as in codes/nhp_procedures.csv> |

### 2.2 Diagnoses this policy applies to (ICD-10-CM)

| ICD-10-CM | Description |
| --- | --- |
| <X00.0> | <Diagnosis> |

<A request whose primary diagnosis is not listed here is outside this policy and goes to clinician review.>

### 2.3 Members

<Who the policy applies to, e.g. Northwind Medicare Advantage members. Age limits belong in section 3, not here.>

## 3. Coverage criteria

All of the following must be met unless a criterion says otherwise.

**3.1 <Short name>.** <One testable statement, e.g. "The member is at least 22 years old on the request date.">

**3.2 <Short name>.** <Numeric example: "The member's **body mass index (BMI)** is less than 35 kg/m², measured within 12 months before the request date.">

**3.3 <Short name>.** All of the following:

- (a) <sub-criterion>
- (b) <sub-criterion>

## 4. Alternative pathways

<Use for criteria that can be met more than one way. Each pathway is one numbered item; all numbered items in this section are required unless stated.>

**4.1 <Short name>.** Any one of the following:

- (a) <pathway, e.g. "**failure** of first-line therapy, as defined in 7.3">
- (b) <pathway, e.g. "documented **intolerance** of first-line therapy, as defined in 7.4">

## 5. Contraindications and exclusions

### 5.1 Contraindications

Coverage criteria are not met if any of the following is documented. <Medical reasons the service is unsafe or will not work for this member.>

- **5.1.1** <condition>
- **5.1.2** <condition>

### 5.2 Exclusions

Northwind does not cover the service under this policy in the following situations. <Coverage limits that are not about safety: repeat procedures, frequency limits, cosmetic use.>

- **5.2.1** <situation>

## 6. Required documentation

The request must include the following. Each item names the criteria it supports.

| # | Document or data element | Must show | Supports |
| --- | --- | --- | --- |
| 6.1 | <e.g. Office visit note> | <what the note must state, with date> | 3.1, 3.2 |
| 6.2 | <e.g. Diagnostic report> | <result, date, who performed it> | 3.3 |
| 6.3 | <e.g. Therapy records> | <dates, duration, reason stopped> | 4.1 |

## 7. Definitions

**7.1 Request date.** The date Northwind receives a complete prior authorization request. All time windows in this policy count back from this date unless a criterion names another date.

**7.2 Documented.** Stated in a dated clinical record signed by a licensed clinician and included with the request. A statement made only on the request form is not documentation.

**7.3 <Term>.** <Definition.>

## 8. Clinical basis

<A short summary, in your own words, of why these criteria are reasonable: the evidence and guideline themes they rest on, and why each threshold sits where it does. List sources by name only (title, organization, year); do not quote them.>

Sources considered:

- <Organization, guideline or review title, year>

## 9. Revision history

| Version | Effective date | Change | Approved by |
| --- | --- | --- | --- |
| 1.0 | 2026-01-01 | Initial policy | Northwind Medical Policy Committee |

---

## Appendix A: Author notes (not part of the policy; never compiled)

### A.1 Clinical plausibility flags

| Section | Threshold | Confidence it is medically plausible | Note |
| --- | --- | --- | --- |
| 3.2 | <value> | <high / medium / low> | <why> |

### A.2 Expected ambiguities

| Section | Wording | Possible readings | Recommended reading |
| --- | --- | --- | --- |
| 4.1 | <phrase> | <reading 1; reading 2> | <which, and why> |

### A.3 Planned test complexity

<Which boundary cases, time windows or conflicts this policy is built to produce, matching the kickoff doc's case mix.>
