# Case brief: CASE-047-06

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Kestrel Ardent (synthetic ID SYN-0047)
- Date of birth: 03/04/1952; sex: female
- Background diagnoses (ICD-10-CM): M17.0, I50.32, I10
- Summary: 74-year-old woman with arthritis in both knees, asking for the right; anesthesia calls her high risk but clears her.

## Request
- Received 08/06/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the right knee.
- Diagnoses: M17.0
- Requested side: right knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Jory Fenwick-Osei
- Radiologist: Dr. Odile Duvane
- Physical therapist: Bastien Thackeray-Ng
- Primary care physician: Dr. Umberto Ostrander
- Orthopedic clinic: Rosalind Yardley
- Anesthesiologist: Dr. Zeno Underhill

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D05 | 04/06/2026 | office_visit_note | Primary care visit for knee pain | Dr. Umberto Ostrander |
| D03 | 06/27/2026 | mri_report | MRI right knee without contrast | Dr. Odile Duvane |
| D02 | 07/09/2026 | radiograph_report | Right knee radiographs | Dr. Odile Duvane |
| D04 | 07/13/2026 | physical_therapy_note | Physical therapy discharge summary | Bastien Thackeray-Ng |
| D01 | 07/23/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Jory Fenwick-Osei |
| D06 | 07/23/2026 | medication_list | Current medication list | Rosalind Yardley |
| D07 | 07/30/2026 | surgical_consult_note | Pre-anesthesia evaluation | Dr. Zeno Underhill |

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
