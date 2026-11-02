# Case brief: CASE-034-06

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Quilla Iverholt (synthetic ID SYN-0028)
- Date of birth: 02/14/1963; sex: female
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10
- Summary: 63-year-old woman on Medicare through disability with a small hallux ulcer measured in millimetres.

## Request
- Received 08/12/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: right plantar hallux (L97.512), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Amara Thackeray-Ng
- Clinical laboratory: Hollis Ostrander
- Vascular lab technologist and interpreting physician: Talia Holloway-Tan
- Wound care nurse practitioner: Rosalind Quarrington
- Wound clinic: Vesna Fenwick-Osei

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 06/22/2026 | office_visit_note | Primary care visit | Dr. Amara Thackeray-Ng |
| D04 | 07/06/2026 | wound_care_note | Wound clinic visit (baseline) | Rosalind Quarrington |
| D03 | 07/08/2026 | vascular_study_report | Noninvasive arterial study | Talia Holloway-Tan |
| D02 | 07/13/2026 | lab_result | Hemoglobin A1c result | Hollis Ostrander |
| D05 | 07/14/2026 | wound_care_note | Wound clinic visit | Rosalind Quarrington |
| D06 | 07/22/2026 | wound_care_note | Wound clinic visit | Rosalind Quarrington |
| D07 | 07/30/2026 | wound_care_note | Wound clinic visit | Rosalind Quarrington |
| D08 | 08/06/2026 | wound_care_note | Wound clinic visit (current) | Rosalind Quarrington |
| D09 | 08/06/2026 | wound_treatment_record | Wound treatment and procedure log | Vesna Fenwick-Osei |
| D10 | 08/06/2026 | offloading_record | Offloading device record | Vesna Fenwick-Osei |
| D11 | 08/06/2026 | allergy_list | Allergy list | Vesna Fenwick-Osei |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. HBA1C: the only values allowed anywhere in the packet are 9.8.

## Forbidden phrases (whole packet)
none
