# Case brief: CASE-034-08

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Nadir Brightwater (synthetic ID SYN-0029)
- Date of birth: 11/23/1960; sex: male
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10
- Summary: 65-year-old man whose last HbA1c was drawn 5 months before the request.

## Request
- Received 10/18/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: right plantar first metatarsal head (L97.512), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Lucan Yardley
- Clinical laboratory: Zeno Galbrecht
- Vascular lab technologist and interpreting physician: Amara Valcourt
- Wound care nurse practitioner: Kestrel Ardent
- Wound clinic: Pell Rasmussen-Vale

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D02 | 05/21/2026 | lab_result | Hemoglobin A1c result | Zeno Galbrecht |
| D01 | 08/24/2026 | office_visit_note | Primary care visit | Dr. Lucan Yardley |
| D03 | 09/03/2026 | vascular_study_report | Noninvasive arterial study | Amara Valcourt |
| D04 | 09/07/2026 | wound_care_note | Wound clinic visit (baseline) | Kestrel Ardent |
| D05 | 09/14/2026 | wound_care_note | Wound clinic visit | Kestrel Ardent |
| D06 | 09/21/2026 | wound_care_note | Wound clinic visit | Kestrel Ardent |
| D07 | 09/28/2026 | wound_care_note | Wound clinic visit | Kestrel Ardent |
| D08 | 10/05/2026 | wound_care_note | Wound clinic visit | Kestrel Ardent |
| D09 | 10/12/2026 | wound_care_note | Wound clinic visit (current) | Kestrel Ardent |
| D10 | 10/12/2026 | wound_treatment_record | Wound treatment and procedure log | Pell Rasmussen-Vale |
| D11 | 10/12/2026 | offloading_record | Offloading device record | Pell Rasmussen-Vale |
| D12 | 10/12/2026 | allergy_list | Allergy list | Pell Rasmussen-Vale |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. HBA1C: the only values allowed anywhere in the packet are 7.9.

## Forbidden phrases (whole packet)
none
