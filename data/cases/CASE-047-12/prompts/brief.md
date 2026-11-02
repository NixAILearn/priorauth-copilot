# Case brief: CASE-047-12

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Talia Yardley (synthetic ID SYN-0003)
- Date of birth: 05/03/1961; sex: female
- Background diagnoses (ICD-10-CM): M17.11, I10, E78.5
- Summary: 65-year-old woman with right knee osteoarthritis and two years of pain despite 12 weeks of PT and naproxen; no locking or catching.

## Request
- Received 10/28/2026 (standard review); service NHP-P-3005: Arthroscopic debridement of the right knee.
- Diagnoses: M17.11
- Requested side: right knee

## Clinicians (use these names and nobody else)
- Orthopedic surgeon: Dr. Jory Lindqvist-Amari
- Radiologist: Dr. Odile Thackeray-Ng
- Physical therapist: Amara Rasmussen-Vale
- Orthopedic clinic: Lucan Jessop
- Primary care physician: Dr. Elowen Kittredge

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D05 | 05/20/2026 | office_visit_note | Primary care visit for knee pain | Dr. Elowen Kittredge |
| D03 | 08/19/2026 | physical_therapy_note | Physical therapy discharge summary | Amara Rasmussen-Vale |
| D02 | 09/30/2026 | radiograph_report | Right knee radiographs, standing | Dr. Odile Thackeray-Ng |
| D01 | 10/14/2026 | orthopedic_note | Orthopedic surgery office visit | Dr. Jory Lindqvist-Amari |
| D04 | 10/14/2026 | medication_list | Current medication list | Lucan Jessop |

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
