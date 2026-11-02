# Case brief: CASE-034-15

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Lucan Jessop (synthetic ID SYN-0036)
- Date of birth: 10/29/1957; sex: male
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10
- Summary: 68-year-old man whose ulcer went from 10.0 to 5.0 cm2.

## Request
- Received 08/30/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: left plantar first metatarsal head (L97.522), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Rosalind Valcourt
- Clinical laboratory: Jory Holloway-Tan
- Vascular lab technologist and interpreting physician: Kestrel Galbrecht
- Wound care nurse practitioner: Zeno Kittredge
- Wound clinic: Wren Whitlock-Abara

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 07/06/2026 | office_visit_note | Primary care visit | Dr. Rosalind Valcourt |
| D03 | 07/11/2026 | vascular_study_report | Noninvasive arterial study | Kestrel Galbrecht |
| D04 | 07/20/2026 | wound_care_note | Wound clinic visit (baseline) | Zeno Kittredge |
| D02 | 07/21/2026 | lab_result | Hemoglobin A1c result | Jory Holloway-Tan |
| D05 | 07/27/2026 | wound_care_note | Wound clinic visit | Zeno Kittredge |
| D06 | 08/03/2026 | wound_care_note | Wound clinic visit | Zeno Kittredge |
| D07 | 08/10/2026 | wound_care_note | Wound clinic visit | Zeno Kittredge |
| D08 | 08/17/2026 | wound_care_note | Wound clinic visit | Zeno Kittredge |
| D09 | 08/24/2026 | wound_care_note | Wound clinic visit (current) | Zeno Kittredge |
| D10 | 08/24/2026 | wound_treatment_record | Wound treatment and procedure log | Wren Whitlock-Abara |
| D11 | 08/24/2026 | offloading_record | Offloading device record | Wren Whitlock-Abara |
| D12 | 08/24/2026 | allergy_list | Allergy list | Wren Whitlock-Abara |

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
