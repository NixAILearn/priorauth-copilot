# Case brief: CASE-034-12

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Corinne Kittredge (synthetic ID SYN-0033)
- Date of birth: 09/12/1959; sex: female
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10
- Summary: 67-year-old woman whose ulcer shrank by 65% in 4 weeks of standard care.

## Request
- Received 09/20/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: right plantar first metatarsal head (L97.512), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Jory Holloway-Tan
- Clinical laboratory: Pell Brightwater
- Vascular lab technologist and interpreting physician: Dashiell Galbrecht
- Wound care nurse practitioner: Farrukh Ostrander
- Wound clinic: Amara Thackeray-Ng

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 08/03/2026 | office_visit_note | Primary care visit | Dr. Jory Holloway-Tan |
| D02 | 08/11/2026 | lab_result | Hemoglobin A1c result | Pell Brightwater |
| D03 | 08/11/2026 | vascular_study_report | Noninvasive arterial study | Dashiell Galbrecht |
| D04 | 08/17/2026 | wound_care_note | Wound clinic visit (baseline) | Farrukh Ostrander |
| D05 | 08/24/2026 | wound_care_note | Wound clinic visit | Farrukh Ostrander |
| D06 | 08/31/2026 | wound_care_note | Wound clinic visit | Farrukh Ostrander |
| D07 | 09/07/2026 | wound_care_note | Wound clinic visit | Farrukh Ostrander |
| D08 | 09/14/2026 | wound_care_note | Wound clinic visit (current) | Farrukh Ostrander |
| D09 | 09/14/2026 | wound_treatment_record | Wound treatment and procedure log | Amara Thackeray-Ng |
| D10 | 09/14/2026 | offloading_record | Offloading device record | Amara Thackeray-Ng |
| D11 | 09/14/2026 | allergy_list | Allergy list | Amara Thackeray-Ng |

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
