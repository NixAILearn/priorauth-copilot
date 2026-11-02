# Case brief: CASE-047-17

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Marisol Holloway-Tan (synthetic ID SYN-0057)
- Date of birth: 06/28/1962; sex: female
- Background diagnoses (ICD-10-CM): M17.11
- Summary: 64-year-old woman with a right-knee request whose MRI report is of the left knee.

## Request
- Received 07/30/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the right knee.
- Diagnoses: M17.11
- Requested side: right knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Kestrel Jessop
- Radiologist: Dr. Hollis Marchetti-Lowe
- Physical therapist: Dashiell Underhill
- Primary care physician: Dr. Bastien Thackeray-Ng
- Orthopedic clinic: Vesna Galbrecht

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D05 | 03/30/2026 | office_visit_note | Primary care visit for knee pain | Dr. Bastien Thackeray-Ng |
| D03 | 06/20/2026 | mri_report | MRI left knee without contrast | Dr. Hollis Marchetti-Lowe |
| D02 | 07/02/2026 | radiograph_report | Right knee radiographs | Dr. Hollis Marchetti-Lowe |
| D04 | 07/06/2026 | physical_therapy_note | Physical therapy discharge summary | Dashiell Underhill |
| D01 | 07/16/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Kestrel Jessop |
| D06 | 07/16/2026 | medication_list | Current medication list | Vesna Galbrecht |

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
