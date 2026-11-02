# Case brief: CASE-034-10

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Hollis Northcote (synthetic ID SYN-0031)
- Date of birth: 04/18/1950; sex: female
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10, E78.5
- Summary: 76-year-old woman with a weekly wound series whose note from one visit was not sent.

## Request
- Received 10/25/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: right plantar first metatarsal head (L97.512), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Umberto Quarrington
- Clinical laboratory: Ines Ostrander
- Vascular lab technologist and interpreting physician: Pell Calloway-Reyes
- Wound care nurse practitioner: Jory Holloway-Tan
- Wound clinic: Lucan Ellery

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 08/31/2026 | office_visit_note | Primary care visit | Dr. Umberto Quarrington |
| D03 | 09/05/2026 | vascular_study_report | Noninvasive arterial study | Pell Calloway-Reyes |
| D04 | 09/14/2026 | wound_care_note | Wound clinic visit (baseline) | Jory Holloway-Tan |
| D02 | 09/15/2026 | lab_result | Hemoglobin A1c result | Ines Ostrander |
| D05 | 09/21/2026 | wound_care_note | Wound clinic visit | Jory Holloway-Tan |
| D07 | 10/12/2026 | wound_care_note | Wound clinic visit | Jory Holloway-Tan |
| D08 | 10/19/2026 | wound_care_note | Wound clinic visit (current) | Jory Holloway-Tan |
| D09 | 10/19/2026 | wound_treatment_record | Wound treatment and procedure log | Lucan Ellery |
| D10 | 10/19/2026 | offloading_record | Offloading device record | Lucan Ellery |
| D11 | 10/19/2026 | allergy_list | Allergy list | Lucan Ellery |

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
