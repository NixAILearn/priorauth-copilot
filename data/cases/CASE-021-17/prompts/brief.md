# Case brief: CASE-021-17

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Talia Ostrander (synthetic ID SYN-0019)
- Date of birth: 09/14/1951; sex: male
- Background diagnoses (ICD-10-CM): G47.33, I10, I48.91
- Summary: 74-year-old man with two diagnostic studies in the window: AHI 31 twenty months ago and AHI 13 eight months ago after weight loss.

## Request
- Received 08/19/2026 (standard review); service NHP-P-1042: First implant of a complete hypoglossal nerve stimulator system for obstructive sleep apnea.
- Diagnoses: G47.33

## Clinicians (use these names and nobody else)
- Sleep medicine physician (interpreting): Dr. Soren Jessop
- Durable medical equipment supplier: Wren Calloway-Reyes
- Sleep medicine physician: Dr. Ines Kittredge
- Otolaryngologist: Dr. Yusra Fenwick-Osei

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D06 | 12/19/2024 | sleep_study_report | Attended in-lab diagnostic polysomnogram | Dr. Soren Jessop |
| D01 | 12/19/2025 | sleep_study_report | Attended in-lab diagnostic polysomnogram | Dr. Soren Jessop |
| D02 | 04/02/2026 | pap_usage_report | CPAP device compliance download | Wren Calloway-Reyes |
| D04 | 04/19/2026 | dise_report | Drug-induced sleep endoscopy report | Dr. Yusra Fenwick-Osei |
| D03 | 07/05/2026 | sleep_consult_note | Sleep medicine follow-up visit | Dr. Ines Kittredge |
| D05 | 07/29/2026 | surgical_consult_note | ENT surgical consultation for HGNS | Dr. Yusra Fenwick-Osei |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. BMI: the only values allowed anywhere in the packet are 28.8.
8. AHI: the only values allowed anywhere in the packet are 13.0, 31.0.

## Forbidden phrases (whole packet)
none
