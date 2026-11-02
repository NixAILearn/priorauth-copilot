# Case brief: CASE-021-04

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Amara Iverholt (synthetic ID SYN-0006)
- Date of birth: 06/14/1961; sex: male
- Background diagnoses (ICD-10-CM): G47.33, I10, K21.9
- Summary: 65-year-old man; ENT note records height and weight but no BMI; sleep follow-up done by video.

## Request
- Received 10/02/2026 (standard review); service NHP-P-1042: First implant of a complete hypoglossal nerve stimulator system for obstructive sleep apnea.
- Diagnoses: G47.33

## Clinicians (use these names and nobody else)
- Sleep medicine physician (interpreting): Dr. Umberto Ardent
- Durable medical equipment supplier: Marisol Jessop
- Sleep medicine physician: Dr. Yusra Ellery
- Otolaryngologist: Dr. Nadir Underhill

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 02/02/2026 | sleep_study_report | Attended in-lab diagnostic polysomnogram | Dr. Umberto Ardent |
| D02 | 05/17/2026 | pap_usage_report | CPAP device compliance download | Marisol Jessop |
| D04 | 06/02/2026 | dise_report | Drug-induced sleep endoscopy report | Dr. Nadir Underhill |
| D03 | 08/18/2026 | sleep_consult_note | Sleep medicine follow-up visit | Dr. Yusra Ellery |
| D05 | 09/11/2026 | surgical_consult_note | ENT surgical consultation for HGNS | Dr. Nadir Underhill |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. BMI: the only values allowed anywhere in the packet are 28.4.
8. AHI: the only values allowed anywhere in the packet are 33.0.

## Forbidden phrases (whole packet)
none
