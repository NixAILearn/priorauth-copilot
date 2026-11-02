# Case brief: CASE-034-17

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Amara Northcote (synthetic ID SYN-0038)
- Date of birth: 05/16/1952; sex: male
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10, E78.5
- Summary: 74-year-old man whose current wound note carries a copied-forward line about purulent drainage.

## Request
- Received 11/08/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: left plantar first metatarsal head (L97.522), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Corinne Ardent
- Clinical laboratory: Wren Brightwater
- Vascular lab technologist and interpreting physician: Yusra Calloway-Reyes
- Wound care nurse practitioner: Soren Thackeray-Ng
- Wound clinic: Vesna Marchetti-Lowe

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 09/14/2026 | office_visit_note | Primary care visit | Dr. Corinne Ardent |
| D03 | 09/24/2026 | vascular_study_report | Noninvasive arterial study | Yusra Calloway-Reyes |
| D04 | 09/28/2026 | wound_care_note | Wound clinic visit (baseline) | Soren Thackeray-Ng |
| D02 | 09/29/2026 | lab_result | Hemoglobin A1c result | Wren Brightwater |
| D05 | 10/05/2026 | wound_care_note | Wound clinic visit | Soren Thackeray-Ng |
| D06 | 10/12/2026 | wound_care_note | Wound clinic visit | Soren Thackeray-Ng |
| D07 | 10/19/2026 | wound_care_note | Wound clinic visit | Soren Thackeray-Ng |
| D08 | 10/26/2026 | wound_care_note | Wound clinic visit | Soren Thackeray-Ng |
| D09 | 11/02/2026 | wound_care_note | Wound clinic visit (current) | Soren Thackeray-Ng |
| D10 | 11/02/2026 | wound_treatment_record | Wound treatment and procedure log | Vesna Marchetti-Lowe |
| D11 | 11/02/2026 | offloading_record | Offloading device record | Vesna Marchetti-Lowe |
| D12 | 11/02/2026 | allergy_list | Allergy list | Vesna Marchetti-Lowe |

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
