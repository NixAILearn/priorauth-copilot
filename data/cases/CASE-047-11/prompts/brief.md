# Case brief: CASE-047-11

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Elowen Lindqvist-Amari (synthetic ID SYN-0052)
- Date of birth: 05/06/1963; sex: male
- Background diagnoses (ICD-10-CM): M17.12
- Summary: 63-year-old man whose notes say only that the knee 'locks up'.

## Request
- Received 10/22/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the left knee.
- Diagnoses: M17.12
- Requested side: left knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Talia Yardley
- Radiologist: Dr. Vesna Underhill
- Physical therapist: Wren Duvane
- Primary care physician: Dr. Amara Brightwater
- Orthopedic clinic: Greer Iverholt

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D05 | 06/22/2026 | office_visit_note | Primary care visit for knee pain | Dr. Amara Brightwater |
| D03 | 09/12/2026 | mri_report | MRI left knee without contrast | Dr. Vesna Underhill |
| D02 | 09/24/2026 | radiograph_report | Left knee radiographs | Dr. Vesna Underhill |
| D04 | 09/28/2026 | physical_therapy_note | Physical therapy discharge summary | Wren Duvane |
| D01 | 10/08/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Talia Yardley |
| D06 | 10/08/2026 | medication_list | Current medication list | Greer Iverholt |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. KL_GRADE: the only values allowed anywhere in the packet are 2.0.

## Forbidden phrases (whole packet)
"block", "cannot straighten", "catches", "catching", "gets stuck"
