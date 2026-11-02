# Case brief: CASE-021-02

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Nadir Lindqvist-Amari (synthetic ID SYN-0004)
- Date of birth: 03/09/1955; sex: female
- Background diagnoses (ICD-10-CM): G47.33, I10, E03.9
- Summary: 71-year-old woman with severe OSA who uses CPAP nightly but still has a residual AHI of 22 at the best tolerated pressure.

## Request
- Received 09/18/2026 (standard review); service NHP-P-1042: First implant of a complete hypoglossal nerve stimulator system for obstructive sleep apnea.
- Diagnoses: G47.33

## Clinicians (use these names and nobody else)
- Sleep medicine physician (interpreting): Dr. Yusra Valcourt
- Sleep medicine physician: Dr. Vesna Pemberly
- Otolaryngologist: Dr. Elowen Iverholt

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 01/18/2026 | sleep_study_report | Attended in-lab diagnostic polysomnogram | Dr. Yusra Valcourt |
| D02 | 02/08/2026 | titration_study_report | Attended CPAP titration study | Dr. Yusra Valcourt |
| D04 | 05/18/2026 | dise_report | Drug-induced sleep endoscopy report | Dr. Elowen Iverholt |
| D03 | 08/04/2026 | sleep_consult_note | Sleep medicine follow-up visit | Dr. Vesna Pemberly |
| D05 | 08/28/2026 | surgical_consult_note | ENT surgical consultation for HGNS | Dr. Elowen Iverholt |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. BMI: the only values allowed anywhere in the packet are 29.4.
8. AHI: the only values allowed anywhere in the packet are 22.0, 42.0.

## Forbidden phrases (whole packet)
none
