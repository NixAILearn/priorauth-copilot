# Case brief: CASE-021-03

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Dashiell Marchetti-Lowe (synthetic ID SYN-0005)
- Date of birth: 11/30/1968; sex: male
- Background diagnoses (ICD-10-CM): G47.33, E11.9
- Summary: 57-year-old man on Medicare through disability, with moderate OSA diagnosed by a home test; stopped CPAP after a mask refit failed.

## Request
- Received 08/26/2026 (standard review); service NHP-P-1042: First implant of a complete hypoglossal nerve stimulator system for obstructive sleep apnea.
- Diagnoses: G47.33

## Clinicians (use these names and nobody else)
- Sleep medicine physician (interpreting): Dr. Amara Lindqvist-Amari
- Durable medical equipment supplier: Vesna Underhill
- Sleep medicine physician: Dr. Kestrel Valcourt
- Otolaryngologist: Dr. Lucan Kittredge

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 12/26/2025 | sleep_study_report | Home sleep apnea test report | Dr. Amara Lindqvist-Amari |
| D02 | 04/09/2026 | pap_usage_report | CPAP device compliance download | Vesna Underhill |
| D04 | 04/26/2026 | dise_report | Drug-induced sleep endoscopy report | Dr. Lucan Kittredge |
| D03 | 07/12/2026 | sleep_consult_note | Sleep medicine follow-up visit | Dr. Kestrel Valcourt |
| D05 | 08/05/2026 | surgical_consult_note | ENT surgical consultation for HGNS | Dr. Lucan Kittredge |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. BMI: the only values allowed anywhere in the packet are 32.7.
8. AHI: the only values allowed anywhere in the packet are 24.0.

## Forbidden phrases (whole packet)
none
