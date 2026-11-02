# Case brief: CASE-034-11

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Pell Whitlock-Abara (synthetic ID SYN-0032)
- Date of birth: 01/05/1965; sex: male
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10
- Summary: 61-year-old man on Medicare through disability; never debrided, and two of his wound notes do not describe the bed.

## Request
- Received 08/23/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: left plantar heel (L97.422), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Quilla Marchetti-Lowe
- Clinical laboratory: Farrukh Holloway-Tan
- Vascular lab technologist and interpreting physician: Dashiell Rasmussen-Vale
- Wound care nurse practitioner: Corinne Valcourt
- Wound clinic: Lucan Lindqvist-Amari

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 06/29/2026 | office_visit_note | Primary care visit | Dr. Quilla Marchetti-Lowe |
| D04 | 07/13/2026 | wound_care_note | Wound clinic visit (baseline) | Corinne Valcourt |
| D02 | 07/14/2026 | lab_result | Hemoglobin A1c result | Farrukh Holloway-Tan |
| D03 | 07/14/2026 | vascular_study_report | Noninvasive arterial study | Dashiell Rasmussen-Vale |
| D05 | 07/20/2026 | wound_care_note | Wound clinic visit | Corinne Valcourt |
| D06 | 07/27/2026 | wound_care_note | Wound clinic visit | Corinne Valcourt |
| D07 | 08/03/2026 | wound_care_note | Wound clinic visit | Corinne Valcourt |
| D08 | 08/10/2026 | wound_care_note | Wound clinic visit | Corinne Valcourt |
| D09 | 08/17/2026 | wound_care_note | Wound clinic visit (current) | Corinne Valcourt |
| D10 | 08/17/2026 | wound_treatment_record | Wound treatment and procedure log | Lucan Lindqvist-Amari |
| D11 | 08/17/2026 | offloading_record | Offloading device record | Lucan Lindqvist-Amari |
| D12 | 08/17/2026 | allergy_list | Allergy list | Lucan Lindqvist-Amari |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. HBA1C: the only values allowed anywhere in the packet are 8.1.

## Forbidden phrases (whole packet)
"clean granular", "eschar", "granular base", "nonviable", "slough"
