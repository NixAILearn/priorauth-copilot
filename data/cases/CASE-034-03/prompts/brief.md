# Case brief: CASE-034-03

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Bastien Valcourt (synthetic ID SYN-0025)
- Date of birth: 12/09/1953; sex: male
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10, E78.5
- Summary: 72-year-old man with two neuropathic ulcers on the right foot, both treated for 5 weeks.

## Request
- Received 10/12/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: right plantar first metatarsal head (L97.512), 4 applications
- Target ulcer U2: right plantar heel (L97.412), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Talia Strathmore
- Clinical laboratory: Wren Ellery
- Vascular lab technologist and interpreting physician: Jory Lindqvist-Amari
- Wound care nurse practitioner: Kestrel Quarrington
- Wound clinic: Yusra Fenwick-Osei

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 08/18/2026 | office_visit_note | Primary care visit | Dr. Talia Strathmore |
| D03 | 08/23/2026 | vascular_study_report | Noninvasive arterial study | Jory Lindqvist-Amari |
| D04 | 09/01/2026 | wound_care_note | Wound clinic visit (baseline) | Kestrel Quarrington |
| D02 | 09/02/2026 | lab_result | Hemoglobin A1c result | Wren Ellery |
| D05 | 09/08/2026 | wound_care_note | Wound clinic visit | Kestrel Quarrington |
| D06 | 09/15/2026 | wound_care_note | Wound clinic visit | Kestrel Quarrington |
| D07 | 09/22/2026 | wound_care_note | Wound clinic visit | Kestrel Quarrington |
| D08 | 09/29/2026 | wound_care_note | Wound clinic visit | Kestrel Quarrington |
| D09 | 10/06/2026 | wound_care_note | Wound clinic visit (current) | Kestrel Quarrington |
| D10 | 10/06/2026 | wound_treatment_record | Wound treatment and procedure log | Yusra Fenwick-Osei |
| D11 | 10/06/2026 | offloading_record | Offloading device record | Yusra Fenwick-Osei |
| D12 | 10/06/2026 | allergy_list | Allergy list | Yusra Fenwick-Osei |

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
