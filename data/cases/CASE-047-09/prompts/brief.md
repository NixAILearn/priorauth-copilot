# Case brief: CASE-047-09

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Kestrel Underhill (synthetic ID SYN-0050)
- Date of birth: 10/30/1958; sex: male
- Background diagnoses (ICD-10-CM): M17.11, I10
- Summary: 68-year-old man whose MRI was ordered but not resulted when the request was sent.

## Request
- Received 09/17/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the right knee.
- Diagnoses: M17.11
- Requested side: right knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Farrukh Strathmore
- Radiologist: Dr. Corinne Holloway-Tan
- Physical therapist: Bastien Jessop
- Primary care physician: Dr. Hollis Valcourt
- Orthopedic clinic: Lucan Northcote

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D05 | 05/18/2026 | office_visit_note | Primary care visit for knee pain | Dr. Hollis Valcourt |
| D02 | 08/20/2026 | radiograph_report | Right knee radiographs | Dr. Corinne Holloway-Tan |
| D04 | 08/24/2026 | physical_therapy_note | Physical therapy discharge summary | Bastien Jessop |
| D01 | 09/03/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Farrukh Strathmore |
| D06 | 09/03/2026 | medication_list | Current medication list | Lucan Northcote |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. KL_GRADE: the only values allowed anywhere in the packet are 2.0.

## Forbidden phrases (whole packet)
"Scan date", "chondral flap", "loose body seen on MRI", "meniscal tear"
