# Case brief: CASE-047-04

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Dashiell Thackeray-Ng (synthetic ID SYN-0045)
- Date of birth: 09/09/1957; sex: female
- Background diagnoses (ICD-10-CM): M17.10, I10
- Summary: 69-year-old woman whose diagnosis code names no side; the request names the right knee.

## Request
- Received 07/23/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the right knee.
- Diagnoses: M17.10
- Requested side: right knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Odile Brightwater
- Radiologist: Dr. Greer Kittredge
- Physical therapist: Rosalind Fenwick-Osei
- Primary care physician: Dr. Umberto Ellery
- Orthopedic clinic: Ines Northcote

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D05 | 03/23/2026 | office_visit_note | Primary care visit for knee pain | Dr. Umberto Ellery |
| D03 | 06/13/2026 | mri_report | MRI right knee without contrast | Dr. Greer Kittredge |
| D02 | 06/25/2026 | radiograph_report | Right knee radiographs | Dr. Greer Kittredge |
| D04 | 06/29/2026 | physical_therapy_note | Physical therapy discharge summary | Rosalind Fenwick-Osei |
| D01 | 07/09/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Odile Brightwater |
| D06 | 07/09/2026 | medication_list | Current medication list | Ines Northcote |

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
