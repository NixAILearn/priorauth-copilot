# Case brief: CASE-034-16

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Umberto Fenwick-Osei (synthetic ID SYN-0037)
- Date of birth: 12/01/1961; sex: female
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10
- Summary: 64-year-old woman with an HbA1c of exactly 12.0% and a last measurement two weeks before the request.

## Request
- Received 10/19/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: right plantar first metatarsal head (L97.512), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Amara Ellery
- Clinical laboratory: Dashiell Kittredge
- Vascular lab technologist and interpreting physician: Zeno Lindqvist-Amari
- Wound care nurse practitioner: Quilla Quarrington
- Wound clinic: Nadir Valcourt

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 08/17/2026 | office_visit_note | Primary care visit | Dr. Amara Ellery |
| D03 | 08/20/2026 | vascular_study_report | Noninvasive arterial study | Zeno Lindqvist-Amari |
| D04 | 08/31/2026 | wound_care_note | Wound clinic visit (baseline) | Quilla Quarrington |
| D05 | 09/07/2026 | wound_care_note | Wound clinic visit | Quilla Quarrington |
| D06 | 09/14/2026 | wound_care_note | Wound clinic visit | Quilla Quarrington |
| D02 | 09/19/2026 | lab_result | Hemoglobin A1c result | Dashiell Kittredge |
| D07 | 09/21/2026 | wound_care_note | Wound clinic visit | Quilla Quarrington |
| D08 | 09/28/2026 | wound_care_note | Wound clinic visit | Quilla Quarrington |
| D09 | 10/05/2026 | wound_care_note | Wound clinic visit (current) | Quilla Quarrington |
| D10 | 10/05/2026 | wound_treatment_record | Wound treatment and procedure log | Nadir Valcourt |
| D11 | 10/05/2026 | offloading_record | Offloading device record | Nadir Valcourt |
| D12 | 10/05/2026 | allergy_list | Allergy list | Nadir Valcourt |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. HBA1C: the only values allowed anywhere in the packet are 12.0.

## Forbidden phrases (whole packet)
none
