# Case brief: CASE-034-04

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Zeno Strathmore (synthetic ID SYN-0026)
- Date of birth: 03/30/1951; sex: male
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I70.235, I10
- Summary: 75-year-old man whose leg was opened up by angioplasty; the ABI rose from 0.48 to 0.78 and the ulcer has had 44 days of care.

## Request
- Received 08/04/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: right plantar first metatarsal head (L97.512), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Wren Brightwater
- Clinical laboratory: Ines Rasmussen-Vale
- Vascular lab technologist and interpreting physician: Dashiell Whitlock-Abara
- Wound care nurse practitioner: Jory Valcourt
- Wound clinic: Yusra Underhill

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 06/01/2026 | office_visit_note | Primary care visit | Dr. Wren Brightwater |
| D03 | 06/10/2026 | vascular_study_report | Noninvasive arterial study | Dashiell Whitlock-Abara |
| D04 | 06/15/2026 | wound_care_note | Wound clinic visit (baseline) | Jory Valcourt |
| D02 | 06/25/2026 | lab_result | Hemoglobin A1c result | Ines Rasmussen-Vale |
| D05 | 06/26/2026 | wound_care_note | Wound clinic visit | Jory Valcourt |
| D06 | 07/07/2026 | wound_care_note | Wound clinic visit | Jory Valcourt |
| D07 | 07/18/2026 | wound_care_note | Wound clinic visit | Jory Valcourt |
| D08 | 07/29/2026 | wound_care_note | Wound clinic visit (current) | Jory Valcourt |
| D09 | 07/29/2026 | wound_treatment_record | Wound treatment and procedure log | Yusra Underhill |
| D10 | 07/29/2026 | offloading_record | Offloading device record | Yusra Underhill |
| D11 | 07/29/2026 | allergy_list | Allergy list | Yusra Underhill |

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
