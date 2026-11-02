# Case brief: CASE-047-19

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Rosalind Ardent (synthetic ID SYN-0059)
- Date of birth: 09/21/1951; sex: female
- Background diagnoses (ICD-10-CM): M17.11, I10
- Summary: 75-year-old woman whose right knee had a partial replacement years ago, listed in an old hospital surgical history and shown on the radiograph, but never mentioned in the surgeon's notes.

## Request
- Received 10/29/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the right knee.
- Diagnoses: M17.11
- Requested side: right knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Zeno Thackeray-Ng
- Radiologist: Dr. Dashiell Rasmussen-Vale
- Physical therapist: Umberto Brightwater
- Primary care physician: Dr. Bastien Quarrington
- Orthopedic clinic: Amara Ellery
- Hospitalist: Dr. Pell Iverholt

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D07 | 03/02/2026 | history_and_physical | Hospital history and physical (prior admission) | Dr. Pell Iverholt |
| D05 | 06/29/2026 | office_visit_note | Primary care visit for knee pain | Dr. Bastien Quarrington |
| D03 | 09/19/2026 | mri_report | MRI right knee without contrast | Dr. Dashiell Rasmussen-Vale |
| D02 | 10/01/2026 | radiograph_report | Right knee radiographs | Dr. Dashiell Rasmussen-Vale |
| D04 | 10/05/2026 | physical_therapy_note | Physical therapy discharge summary | Umberto Brightwater |
| D01 | 10/15/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Zeno Thackeray-Ng |
| D06 | 10/15/2026 | medication_list | Current medication list | Amara Ellery |

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
