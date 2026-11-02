# Case brief: CASE-047-10

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Ines Calloway-Reyes (synthetic ID SYN-0051)
- Date of birth: 12/22/1954; sex: female
- Background diagnoses (ICD-10-CM): M17.11
- Summary: 71-year-old woman; the surgeon's note says PT was completed but no therapy records were sent.

## Request
- Received 07/09/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the right knee.
- Diagnoses: M17.11
- Requested side: right knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Rosalind Strathmore
- Radiologist: Dr. Odile Marchetti-Lowe
- Primary care physician: Dr. Vesna Northcote
- Orthopedic clinic: Greer Jessop

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D05 | 03/07/2026 | office_visit_note | Primary care visit for knee pain | Dr. Vesna Northcote |
| D03 | 05/30/2026 | mri_report | MRI right knee without contrast | Dr. Odile Marchetti-Lowe |
| D02 | 06/11/2026 | radiograph_report | Right knee radiographs | Dr. Odile Marchetti-Lowe |
| D01 | 06/25/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Rosalind Strathmore |
| D06 | 06/25/2026 | medication_list | Current medication list | Greer Jessop |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. KL_GRADE: the only values allowed anywhere in the packet are 2.0.

## Forbidden phrases (whole packet)
"PT discharge", "home exercise program", "supervised physical therapy visits"
