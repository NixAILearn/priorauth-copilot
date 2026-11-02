# Case brief: CASE-047-16

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Nadir Holloway-Tan (synthetic ID SYN-0056)
- Date of birth: 02/07/1953; sex: male
- Background diagnoses (ICD-10-CM): M17.11
- Summary: 73-year-old man whose only MRI is one day older than the 6-month window.

## Request
- Received 09/29/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the right knee.
- Diagnoses: M17.11
- Requested side: right knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Quilla Iverholt
- Radiologist: Dr. Rosalind Ardent
- Physical therapist: Amara Northcote
- Primary care physician: Dr. Zeno Ostrander
- Orthopedic clinic: Hollis Quarrington

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D03 | 03/28/2026 | mri_report | MRI right knee without contrast | Dr. Rosalind Ardent |
| D05 | 05/30/2026 | office_visit_note | Primary care visit for knee pain | Dr. Zeno Ostrander |
| D02 | 09/01/2026 | radiograph_report | Right knee radiographs | Dr. Rosalind Ardent |
| D04 | 09/05/2026 | physical_therapy_note | Physical therapy discharge summary | Amara Northcote |
| D01 | 09/15/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Quilla Iverholt |
| D06 | 09/15/2026 | medication_list | Current medication list | Hollis Quarrington |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. KL_GRADE: the only values allowed anywhere in the packet are 2.0.

## Forbidden phrases (whole packet)
none
