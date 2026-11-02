# Case brief: CASE-034-01

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Elowen Holloway-Tan (synthetic ID SYN-0023)
- Date of birth: 05/20/1956; sex: male
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10
- Summary: 70-year-old man with a neuropathic ulcer under the right first metatarsal head after 5 weeks of good standard care.

## Request
- Received 09/20/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: right plantar first metatarsal head (L97.512), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Umberto Thackeray-Ng
- Clinical laboratory: Greer Kittredge
- Vascular lab technologist and interpreting physician: Marisol Duvane
- Wound care nurse practitioner: Hollis Galbrecht
- Wound clinic: Soren Lindqvist-Amari

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D03 | 07/22/2026 | vascular_study_report | Noninvasive arterial study | Marisol Duvane |
| D01 | 07/27/2026 | office_visit_note | Primary care visit | Dr. Umberto Thackeray-Ng |
| D04 | 08/10/2026 | wound_care_note | Wound clinic visit (baseline) | Hollis Galbrecht |
| D02 | 08/11/2026 | lab_result | Hemoglobin A1c result | Greer Kittredge |
| D05 | 08/17/2026 | wound_care_note | Wound clinic visit | Hollis Galbrecht |
| D06 | 08/24/2026 | wound_care_note | Wound clinic visit | Hollis Galbrecht |
| D07 | 08/31/2026 | wound_care_note | Wound clinic visit | Hollis Galbrecht |
| D08 | 09/07/2026 | wound_care_note | Wound clinic visit | Hollis Galbrecht |
| D09 | 09/14/2026 | wound_care_note | Wound clinic visit (current) | Hollis Galbrecht |
| D10 | 09/14/2026 | wound_treatment_record | Wound treatment and procedure log | Soren Lindqvist-Amari |
| D11 | 09/14/2026 | offloading_record | Offloading device record | Soren Lindqvist-Amari |
| D12 | 09/14/2026 | allergy_list | Allergy list | Soren Lindqvist-Amari |

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
