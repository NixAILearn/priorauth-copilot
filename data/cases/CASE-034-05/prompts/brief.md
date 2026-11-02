# Case brief: CASE-034-05

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Amara Yardley (synthetic ID SYN-0027)
- Date of birth: 07/07/1958; sex: female
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10
- Summary: 68-year-old woman whose ulcer bed has stayed clean, so it was never debrided.

## Request
- Received 10/04/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: left plantar first metatarsal head (L97.522), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Rosalind Quarrington
- Clinical laboratory: Soren Strathmore
- Vascular lab technologist and interpreting physician: Quilla Valcourt
- Wound care nurse practitioner: Nadir Northcote
- Wound clinic: Zeno Iverholt

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 08/10/2026 | office_visit_note | Primary care visit | Dr. Rosalind Quarrington |
| D04 | 08/24/2026 | wound_care_note | Wound clinic visit (baseline) | Nadir Northcote |
| D02 | 08/25/2026 | lab_result | Hemoglobin A1c result | Soren Strathmore |
| D03 | 08/25/2026 | vascular_study_report | Noninvasive arterial study | Quilla Valcourt |
| D05 | 08/31/2026 | wound_care_note | Wound clinic visit | Nadir Northcote |
| D06 | 09/07/2026 | wound_care_note | Wound clinic visit | Nadir Northcote |
| D07 | 09/14/2026 | wound_care_note | Wound clinic visit | Nadir Northcote |
| D08 | 09/21/2026 | wound_care_note | Wound clinic visit | Nadir Northcote |
| D09 | 09/28/2026 | wound_care_note | Wound clinic visit (current) | Nadir Northcote |
| D10 | 09/28/2026 | wound_treatment_record | Wound treatment and procedure log | Zeno Iverholt |
| D11 | 09/28/2026 | offloading_record | Offloading device record | Zeno Iverholt |
| D12 | 09/28/2026 | allergy_list | Allergy list | Zeno Iverholt |

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
