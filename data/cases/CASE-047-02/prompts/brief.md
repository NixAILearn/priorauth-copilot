# Case brief: CASE-047-02

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Umberto Northcote (synthetic ID SYN-0043)
- Date of birth: 01/18/1959; sex: female
- Background diagnoses (ICD-10-CM): M17.12
- Summary: 67-year-old woman whose left knee locked two weeks ago; MRI shows a displaced bucket-handle tear.

## Request
- Received 08/20/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the left knee.
- Diagnoses: M17.12
- Requested side: left knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Corinne Jessop
- Radiologist: Dr. Hollis Ellery
- Primary care physician: Dr. Rosalind Calloway-Reyes
- Orthopedic clinic: Dashiell Lindqvist-Amari

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D03 | 07/11/2026 | mri_report | MRI left knee without contrast | Dr. Hollis Ellery |
| D02 | 07/23/2026 | radiograph_report | Left knee radiographs | Dr. Hollis Ellery |
| D04 | 07/31/2026 | office_visit_note | Primary care visit | Dr. Rosalind Calloway-Reyes |
| D01 | 08/06/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Corinne Jessop |
| D06 | 08/06/2026 | medication_list | Current medication list | Dashiell Lindqvist-Amari |

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
