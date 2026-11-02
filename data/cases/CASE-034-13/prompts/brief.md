# Case brief: CASE-034-13

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Pell Underhill (synthetic ID SYN-0034)
- Date of birth: 02/26/1948; sex: male
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I70.245, N18.4
- Summary: 78-year-old man with severe arterial disease: non-compressible ABI and a toe pressure of 22 mmHg.

## Request
- Received 08/18/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: left plantar first metatarsal head (L97.522), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Vesna Whitlock-Abara
- Clinical laboratory: Rosalind Pemberly
- Vascular lab technologist and interpreting physician: Ines Marchetti-Lowe
- Wound care nurse practitioner: Greer Yardley
- Wound clinic: Umberto Kittredge

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 06/15/2026 | office_visit_note | Primary care visit | Dr. Vesna Whitlock-Abara |
| D04 | 06/29/2026 | wound_care_note | Wound clinic visit (baseline) | Greer Yardley |
| D02 | 07/09/2026 | lab_result | Hemoglobin A1c result | Rosalind Pemberly |
| D03 | 07/09/2026 | vascular_study_report | Noninvasive arterial study | Ines Marchetti-Lowe |
| D05 | 07/10/2026 | wound_care_note | Wound clinic visit | Greer Yardley |
| D06 | 07/21/2026 | wound_care_note | Wound clinic visit | Greer Yardley |
| D07 | 08/01/2026 | wound_care_note | Wound clinic visit | Greer Yardley |
| D08 | 08/12/2026 | wound_care_note | Wound clinic visit (current) | Greer Yardley |
| D09 | 08/12/2026 | wound_treatment_record | Wound treatment and procedure log | Umberto Kittredge |
| D10 | 08/12/2026 | offloading_record | Offloading device record | Umberto Kittredge |
| D11 | 08/12/2026 | allergy_list | Allergy list | Umberto Kittredge |

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
