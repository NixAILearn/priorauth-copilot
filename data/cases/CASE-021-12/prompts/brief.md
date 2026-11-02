# Case brief: CASE-021-12

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Jory Quarrington (synthetic ID SYN-0014)
- Date of birth: 10/17/1962; sex: female
- Background diagnoses (ICD-10-CM): G47.33, E66.9, I10, E11.9
- Summary: 63-year-old woman with obesity (BMI 37.4) and otherwise qualifying OSA.

## Request
- Received 07/15/2026 (standard review); service NHP-P-1042: First implant of a complete hypoglossal nerve stimulator system for obstructive sleep apnea.
- Diagnoses: G47.33

## Clinicians (use these names and nobody else)
- Sleep medicine physician (interpreting): Dr. Corinne Kittredge
- Durable medical equipment supplier: Soren Ellery
- Sleep medicine physician: Dr. Vesna Pemberly
- Otolaryngologist: Dr. Dashiell Fenwick-Osei

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 11/15/2025 | sleep_study_report | Attended in-lab diagnostic polysomnogram | Dr. Corinne Kittredge |
| D02 | 02/27/2026 | pap_usage_report | CPAP device compliance download | Soren Ellery |
| D04 | 03/15/2026 | dise_report | Drug-induced sleep endoscopy report | Dr. Dashiell Fenwick-Osei |
| D03 | 05/31/2026 | sleep_consult_note | Sleep medicine follow-up visit | Dr. Vesna Pemberly |
| D05 | 06/24/2026 | surgical_consult_note | ENT surgical consultation for HGNS | Dr. Dashiell Fenwick-Osei |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. BMI: the only values allowed anywhere in the packet are 37.4.
8. AHI: the only values allowed anywhere in the packet are 33.0.

## Forbidden phrases (whole packet)
none
