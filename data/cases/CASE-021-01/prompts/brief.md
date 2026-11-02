# Case brief: CASE-021-01

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Dashiell Iverholt (synthetic ID SYN-0001)
- Date of birth: 07/22/1958; sex: male
- Background diagnoses (ICD-10-CM): G47.33, I10, E78.5
- Summary: 68-year-old man with moderate-to-severe obstructive sleep apnea, treated hypertension and high cholesterol; stopped CPAP after three months because of mask discomfort and air leak.

## Request
- Received 10/15/2026 (standard review); service NHP-P-1042: First implant of a complete hypoglossal nerve stimulator system for obstructive sleep apnea.
- Diagnoses: G47.33, I10

## Clinicians (use these names and nobody else)
- Sleep medicine physician (interpreting): Dr. Quilla Kittredge
- Durable medical equipment supplier: Jory Underhill
- Sleep medicine physician: Dr. Hollis Valcourt
- Otolaryngologist: Dr. Kestrel Marchetti-Lowe

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 03/12/2026 | sleep_study_report | Attended in-lab diagnostic polysomnogram | Dr. Quilla Kittredge |
| D04 | 06/04/2026 | dise_report | Drug-induced sleep endoscopy report | Dr. Kestrel Marchetti-Lowe |
| D02 | 06/09/2026 | pap_usage_report | CPAP device compliance download | Jory Underhill |
| D03 | 08/27/2026 | sleep_consult_note | Sleep medicine follow-up visit | Dr. Hollis Valcourt |
| D05 | 09/20/2026 | surgical_consult_note | ENT surgical consultation for HGNS | Dr. Kestrel Marchetti-Lowe |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. BMI: the only values allowed anywhere in the packet are 31.2, 31.6.
8. AHI: the only values allowed anywhere in the packet are 38.0.

## Forbidden phrases (whole packet)
none
