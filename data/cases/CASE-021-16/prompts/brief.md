# Case brief: CASE-021-16

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Soren Marchetti-Lowe (synthetic ID SYN-0018)
- Date of birth: 12/02/1956; sex: female
- Background diagnoses (ICD-10-CM): G47.33, I10, E78.5
- Summary: 69-year-old woman whose only diagnostic study was exactly 24 months before the request, with AHI exactly 15.0.

## Request
- Received 10/09/2026 (standard review); service NHP-P-1042: First implant of a complete hypoglossal nerve stimulator system for obstructive sleep apnea.
- Diagnoses: G47.33

## Clinicians (use these names and nobody else)
- Sleep medicine physician (interpreting): Dr. Odile Galbrecht
- Durable medical equipment supplier: Jory Lindqvist-Amari
- Sleep medicine physician: Dr. Zeno Yardley
- Otolaryngologist: Dr. Greer Kittredge

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 10/09/2024 | sleep_study_report | Attended in-lab diagnostic polysomnogram | Dr. Odile Galbrecht |
| D02 | 01/21/2025 | pap_usage_report | CPAP device compliance download | Jory Lindqvist-Amari |
| D04 | 06/09/2026 | dise_report | Drug-induced sleep endoscopy report | Dr. Greer Kittredge |
| D03 | 08/25/2026 | sleep_consult_note | Sleep medicine follow-up visit | Dr. Zeno Yardley |
| D05 | 09/18/2026 | surgical_consult_note | ENT surgical consultation for HGNS | Dr. Greer Kittredge |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. BMI: the only values allowed anywhere in the packet are 30.4.
8. AHI: the only values allowed anywhere in the packet are 15.0.

## Forbidden phrases (whole packet)
none
