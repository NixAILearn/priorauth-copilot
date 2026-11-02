# Case brief: CASE-021-13

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Pell Strathmore (synthetic ID SYN-0015)
- Date of birth: 01/12/1958; sex: male
- Background diagnoses (ICD-10-CM): G47.33, I10
- Summary: 68-year-old man whose DISE shows complete concentric collapse at the soft palate.

## Request
- Received 08/05/2026 (standard review); service NHP-P-1042: First implant of a complete hypoglossal nerve stimulator system for obstructive sleep apnea.
- Diagnoses: G47.33

## Clinicians (use these names and nobody else)
- Sleep medicine physician (interpreting): Dr. Odile Iverholt
- Durable medical equipment supplier: Yusra Underhill
- Sleep medicine physician: Dr. Hollis Ardent
- Otolaryngologist: Dr. Ines Ostrander

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 12/05/2025 | sleep_study_report | Attended in-lab diagnostic polysomnogram | Dr. Odile Iverholt |
| D02 | 03/19/2026 | pap_usage_report | CPAP device compliance download | Yusra Underhill |
| D04 | 04/05/2026 | dise_report | Drug-induced sleep endoscopy report | Dr. Ines Ostrander |
| D03 | 06/21/2026 | sleep_consult_note | Sleep medicine follow-up visit | Dr. Hollis Ardent |
| D05 | 07/15/2026 | surgical_consult_note | ENT surgical consultation for HGNS | Dr. Ines Ostrander |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. BMI: the only values allowed anywhere in the packet are 29.8.
8. AHI: the only values allowed anywhere in the packet are 33.0.

## Forbidden phrases (whole packet)
none
