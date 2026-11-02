# Case brief: CASE-034-18

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Hollis Ostrander (synthetic ID SYN-0039)
- Date of birth: 08/08/1966; sex: female
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10
- Summary: 60-year-old woman on Medicare through disability; the request says left foot, every wound note says right.

## Request
- Received 08/16/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: left plantar first metatarsal head (L97.522), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Ines Lindqvist-Amari
- Clinical laboratory: Zeno Rasmussen-Vale
- Vascular lab technologist and interpreting physician: Kestrel Yardley
- Wound care nurse practitioner: Nadir Quarrington
- Wound clinic: Farrukh Whitlock-Abara

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 06/22/2026 | office_visit_note | Primary care visit | Dr. Ines Lindqvist-Amari |
| D04 | 07/06/2026 | wound_care_note | Wound clinic visit (baseline) | Nadir Quarrington |
| D02 | 07/07/2026 | lab_result | Hemoglobin A1c result | Zeno Rasmussen-Vale |
| D03 | 07/07/2026 | vascular_study_report | Noninvasive arterial study | Kestrel Yardley |
| D05 | 07/13/2026 | wound_care_note | Wound clinic visit | Nadir Quarrington |
| D06 | 07/20/2026 | wound_care_note | Wound clinic visit | Nadir Quarrington |
| D07 | 07/27/2026 | wound_care_note | Wound clinic visit | Nadir Quarrington |
| D08 | 08/03/2026 | wound_care_note | Wound clinic visit | Nadir Quarrington |
| D09 | 08/10/2026 | wound_care_note | Wound clinic visit (current) | Nadir Quarrington |
| D10 | 08/10/2026 | wound_treatment_record | Wound treatment and procedure log | Farrukh Whitlock-Abara |
| D11 | 08/10/2026 | offloading_record | Offloading device record | Farrukh Whitlock-Abara |
| D12 | 08/10/2026 | allergy_list | Allergy list | Farrukh Whitlock-Abara |

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
