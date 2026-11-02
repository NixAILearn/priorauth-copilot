# Case brief: CASE-021-05

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Greer Valcourt (synthetic ID SYN-0007)
- Date of birth: 01/27/1950; sex: female
- Background diagnoses (ICD-10-CM): G47.33, I10, I49.9
- Summary: 76-year-old woman with an implanted loop recorder and a cardiology clearance letter; otherwise a straightforward HGNS candidate.

## Request
- Received 09/09/2026 (standard review); service NHP-P-1042: First implant of a complete hypoglossal nerve stimulator system for obstructive sleep apnea.
- Diagnoses: G47.33

## Clinicians (use these names and nobody else)
- Sleep medicine physician (interpreting): Dr. Nadir Whitlock-Abara
- Durable medical equipment supplier: Lucan Kittredge
- Sleep medicine physician: Dr. Odile Thackeray-Ng
- Otolaryngologist: Dr. Vesna Rasmussen-Vale
- Cardiologist: Dr. Soren Fenwick-Osei

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 01/09/2026 | sleep_study_report | Attended in-lab diagnostic polysomnogram | Dr. Nadir Whitlock-Abara |
| D02 | 04/23/2026 | pap_usage_report | CPAP device compliance download | Lucan Kittredge |
| D04 | 05/09/2026 | dise_report | Drug-induced sleep endoscopy report | Dr. Vesna Rasmussen-Vale |
| D03 | 07/26/2026 | sleep_consult_note | Sleep medicine follow-up visit | Dr. Odile Thackeray-Ng |
| D06 | 08/13/2026 | office_visit_note | Cardiology clearance letter | Dr. Soren Fenwick-Osei |
| D05 | 08/19/2026 | surgical_consult_note | ENT surgical consultation for HGNS | Dr. Vesna Rasmussen-Vale |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. BMI: the only values allowed anywhere in the packet are 30.1.
8. AHI: the only values allowed anywhere in the packet are 33.0.

## Forbidden phrases (whole packet)
none
