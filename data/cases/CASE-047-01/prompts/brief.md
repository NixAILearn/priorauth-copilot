# Case brief: CASE-047-01

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Corinne Iverholt (synthetic ID SYN-0042)
- Date of birth: 04/02/1964; sex: male
- Background diagnoses (ICD-10-CM): M17.11, I10
- Summary: 62-year-old man on Medicare through disability with right knee catching and an unstable cartilage flap on MRI after 14 weeks of PT and naproxen.

## Request
- Received 09/10/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the right knee.
- Diagnoses: M17.11
- Requested side: right knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Vesna Holloway-Tan
- Radiologist: Dr. Pell Rasmussen-Vale
- Physical therapist: Greer Whitlock-Abara
- Primary care physician: Dr. Farrukh Pemberly
- Orthopedic clinic: Hollis Brightwater

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D05 | 05/11/2026 | office_visit_note | Primary care visit for knee pain | Dr. Farrukh Pemberly |
| D03 | 08/01/2026 | mri_report | MRI right knee without contrast | Dr. Pell Rasmussen-Vale |
| D02 | 08/13/2026 | radiograph_report | Right knee radiographs | Dr. Pell Rasmussen-Vale |
| D04 | 08/17/2026 | physical_therapy_note | Physical therapy discharge summary | Greer Whitlock-Abara |
| D01 | 08/27/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Vesna Holloway-Tan |
| D06 | 08/27/2026 | medication_list | Current medication list | Hollis Brightwater |

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
