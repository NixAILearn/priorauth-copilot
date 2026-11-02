# Case brief: CASE-047-05

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Lucan Rasmussen-Vale (synthetic ID SYN-0046)
- Date of birth: 11/13/1950; sex: male
- Background diagnoses (ICD-10-CM): M17.11, N18.32
- Summary: 75-year-old man with stage 3b kidney disease who takes acetaminophen because NSAIDs are unsafe; KL grade 3.

## Request
- Received 09/24/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the right knee.
- Diagnoses: M17.11
- Requested side: right knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Wren Underhill
- Radiologist: Dr. Odile Kittredge
- Physical therapist: Nadir Iverholt
- Primary care physician: Dr. Rosalind Galbrecht
- Orthopedic clinic: Quilla Strathmore

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D05 | 06/02/2026 | office_visit_note | Primary care visit for knee pain | Dr. Rosalind Galbrecht |
| D03 | 08/15/2026 | mri_report | MRI right knee without contrast | Dr. Odile Kittredge |
| D02 | 08/27/2026 | radiograph_report | Right knee radiographs | Dr. Odile Kittredge |
| D04 | 08/31/2026 | physical_therapy_note | Physical therapy discharge summary | Nadir Iverholt |
| D01 | 09/10/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Wren Underhill |
| D06 | 09/10/2026 | medication_list | Current medication list | Quilla Strathmore |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. KL_GRADE: the only values allowed anywhere in the packet are 3.0.

## Forbidden phrases (whole packet)
none
