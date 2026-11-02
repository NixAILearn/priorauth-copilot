# Case brief: CASE-021-08

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Jory Valcourt (synthetic ID SYN-0010)
- Date of birth: 12/05/1964; sex: female
- Background diagnoses (ICD-10-CM): G47.33, F41.9, I10
- Summary: 61-year-old woman who stopped CPAP within weeks because of claustrophobia; no mask change or desensitization was tried.

## Request
- Received 09/01/2026 (standard review); service NHP-P-1042: First implant of a complete hypoglossal nerve stimulator system for obstructive sleep apnea.
- Diagnoses: G47.33

## Clinicians (use these names and nobody else)
- Sleep medicine physician (interpreting): Dr. Marisol Ardent
- Durable medical equipment supplier: Talia Rasmussen-Vale
- Sleep medicine physician: Dr. Ines Calloway-Reyes
- Otolaryngologist: Dr. Lucan Thackeray-Ng

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 01/01/2026 | sleep_study_report | Attended in-lab diagnostic polysomnogram | Dr. Marisol Ardent |
| D02 | 04/15/2026 | pap_usage_report | CPAP device compliance download | Talia Rasmussen-Vale |
| D04 | 05/01/2026 | dise_report | Drug-induced sleep endoscopy report | Dr. Lucan Thackeray-Ng |
| D03 | 07/18/2026 | sleep_consult_note | Sleep medicine follow-up visit | Dr. Ines Calloway-Reyes |
| D05 | 08/11/2026 | surgical_consult_note | ENT surgical consultation for HGNS | Dr. Lucan Thackeray-Ng |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. BMI: the only values allowed anywhere in the packet are 30.6.
8. AHI: the only values allowed anywhere in the packet are 33.0.

## Forbidden phrases (whole packet)
"changed mask", "desensitiz", "humidif", "mask change", "nasal pillow", "pressure was lowered", "pressure was reduced", "refit"
