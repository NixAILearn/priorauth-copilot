# Case brief: CASE-034-20

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Soren Calloway-Reyes (synthetic ID SYN-0041)
- Date of birth: 03/21/1958; sex: female
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10
- Summary: 68-year-old woman with two left-foot ulcers; the heel ulcer was found two weeks after the first.

## Request
- Received 10/18/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: left plantar first metatarsal head (L97.522), 4 applications
- Target ulcer U2: left plantar heel (L97.422), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Talia Fenwick-Osei
- Clinical laboratory: Kestrel Kittredge
- Vascular lab technologist and interpreting physician: Lucan Ardent
- Wound care nurse practitioner: Corinne Yardley
- Wound clinic: Rosalind Rasmussen-Vale

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 08/24/2026 | office_visit_note | Primary care visit | Dr. Talia Fenwick-Osei |
| D03 | 09/03/2026 | vascular_study_report | Noninvasive arterial study | Lucan Ardent |
| D04 | 09/07/2026 | wound_care_note | Wound clinic visit (baseline) | Corinne Yardley |
| D02 | 09/08/2026 | lab_result | Hemoglobin A1c result | Kestrel Kittredge |
| D05 | 09/14/2026 | wound_care_note | Wound clinic visit | Corinne Yardley |
| D06 | 09/21/2026 | wound_care_note | Wound clinic visit | Corinne Yardley |
| D07 | 09/28/2026 | wound_care_note | Wound clinic visit | Corinne Yardley |
| D08 | 10/05/2026 | wound_care_note | Wound clinic visit | Corinne Yardley |
| D09 | 10/12/2026 | wound_care_note | Wound clinic visit (current) | Corinne Yardley |
| D10 | 10/12/2026 | wound_treatment_record | Wound treatment and procedure log | Rosalind Rasmussen-Vale |
| D11 | 10/12/2026 | offloading_record | Offloading device record | Rosalind Rasmussen-Vale |
| D12 | 10/12/2026 | allergy_list | Allergy list | Rosalind Rasmussen-Vale |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. HBA1C: the only values allowed anywhere in the packet are 8.1.

## Forbidden phrases (whole packet)
none
