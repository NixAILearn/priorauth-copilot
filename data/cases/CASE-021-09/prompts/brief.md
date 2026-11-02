# Case brief: CASE-021-09

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Nadir Quarrington (synthetic ID SYN-0011)
- Date of birth: 02/22/1957; sex: female
- Background diagnoses (ICD-10-CM): G47.33, E11.9, I10
- Summary: 69-year-old woman; her sleep study gives an AHI but no breakdown by apnea type.

## Request
- Received 08/12/2026 (standard review); service NHP-P-1042: First implant of a complete hypoglossal nerve stimulator system for obstructive sleep apnea.
- Diagnoses: G47.33

## Clinicians (use these names and nobody else)
- Sleep medicine physician (interpreting): Dr. Zeno Marchetti-Lowe
- Durable medical equipment supplier: Kestrel Ostrander
- Sleep medicine physician: Dr. Amara Ardent
- Otolaryngologist: Dr. Elowen Kittredge

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 12/12/2025 | sleep_study_report | Attended in-lab diagnostic polysomnogram | Dr. Zeno Marchetti-Lowe |
| D02 | 03/26/2026 | pap_usage_report | CPAP device compliance download | Kestrel Ostrander |
| D04 | 04/12/2026 | dise_report | Drug-induced sleep endoscopy report | Dr. Elowen Kittredge |
| D03 | 06/28/2026 | sleep_consult_note | Sleep medicine follow-up visit | Dr. Amara Ardent |
| D05 | 07/22/2026 | surgical_consult_note | ENT surgical consultation for HGNS | Dr. Elowen Kittredge |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. BMI: the only values allowed anywhere in the packet are 27.9.
8. AHI: the only values allowed anywhere in the packet are 31.0.

## Forbidden phrases (whole packet)
"Central apneas", "Mixed apneas", "central apnea index", "mixed apnea index"
