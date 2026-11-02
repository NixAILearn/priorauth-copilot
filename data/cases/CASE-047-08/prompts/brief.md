# Case brief: CASE-047-08

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Farrukh Thackeray-Ng (synthetic ID SYN-0049)
- Date of birth: 02/11/1966; sex: female
- Background diagnoses (ICD-10-CM): M17.12, E66.9
- Summary: 60-year-old woman on Medicare through disability; her radiograph report does not say the views were standing.

## Request
- Received 08/27/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the left knee.
- Diagnoses: M17.12
- Requested side: left knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Yusra Whitlock-Abara
- Radiologist: Dr. Quilla Quarrington
- Physical therapist: Zeno Marchetti-Lowe
- Primary care physician: Dr. Corinne Rasmussen-Vale
- Orthopedic clinic: Rosalind Ellery

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D05 | 04/27/2026 | office_visit_note | Primary care visit for knee pain | Dr. Corinne Rasmussen-Vale |
| D03 | 07/18/2026 | mri_report | MRI left knee without contrast | Dr. Quilla Quarrington |
| D02 | 07/30/2026 | radiograph_report | Left knee radiographs | Dr. Quilla Quarrington |
| D04 | 08/03/2026 | physical_therapy_note | Physical therapy discharge summary | Zeno Marchetti-Lowe |
| D01 | 08/13/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Yusra Whitlock-Abara |
| D06 | 08/13/2026 | medication_list | Current medication list | Rosalind Ellery |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. KL_GRADE: the only values allowed anywhere in the packet are 2.0.

## Forbidden phrases (whole packet)
"standing", "weight bearing", "weight-bearing"
