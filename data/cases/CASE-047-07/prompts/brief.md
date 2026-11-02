# Case brief: CASE-047-07

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Yusra Holloway-Tan (synthetic ID SYN-0048)
- Date of birth: 07/27/1961; sex: male
- Background diagnoses (ICD-10-CM): M17.11
- Summary: 65-year-old man; the request has an MRI and therapy records but no radiograph report.

## Request
- Received 10/15/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the right knee.
- Diagnoses: M17.11
- Requested side: right knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Ines Fenwick-Osei
- Radiologist: Dr. Soren Underhill
- Physical therapist: Wren Yardley
- Primary care physician: Dr. Quilla Pemberly
- Orthopedic clinic: Farrukh Ostrander

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D05 | 06/15/2026 | office_visit_note | Primary care visit for knee pain | Dr. Quilla Pemberly |
| D03 | 09/05/2026 | mri_report | MRI right knee without contrast | Dr. Soren Underhill |
| D04 | 09/21/2026 | physical_therapy_note | Physical therapy discharge summary | Wren Yardley |
| D01 | 10/01/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Ines Fenwick-Osei |
| D06 | 10/01/2026 | medication_list | Current medication list | Farrukh Ostrander |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.

## Forbidden phrases (whole packet)
"Kellgren", "radiograph", "standing views", "x-ray"
