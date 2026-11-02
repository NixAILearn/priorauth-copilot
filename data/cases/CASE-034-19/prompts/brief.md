# Case brief: CASE-034-19

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Ines Galbrecht (synthetic ID SYN-0040)
- Date of birth: 01/03/1950; sex: male
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10
- Summary: 76-year-old man with osteomyelitis under the ulcer, shown only on an MRI report deep in the packet.

## Request
- Received 09/08/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: right plantar first metatarsal head (L97.512), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Dashiell Northcote
- Clinical laboratory: Rosalind Pemberly
- Vascular lab technologist and interpreting physician: Quilla Rasmussen-Vale
- Wound care nurse practitioner: Kestrel Ardent
- Wound clinic: Jory Calloway-Reyes
- Radiologist: Dr. Nadir Duvane

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 07/20/2026 | office_visit_note | Primary care visit | Dr. Dashiell Northcote |
| D03 | 07/25/2026 | vascular_study_report | Noninvasive arterial study | Quilla Rasmussen-Vale |
| D02 | 07/30/2026 | lab_result | Hemoglobin A1c result | Rosalind Pemberly |
| D04 | 08/03/2026 | wound_care_note | Wound clinic visit (baseline) | Kestrel Ardent |
| D05 | 08/10/2026 | wound_care_note | Wound clinic visit | Kestrel Ardent |
| D06 | 08/17/2026 | wound_care_note | Wound clinic visit | Kestrel Ardent |
| D12 | 08/21/2026 | mri_report | MRI right foot without and with contrast | Dr. Nadir Duvane |
| D07 | 08/24/2026 | wound_care_note | Wound clinic visit | Kestrel Ardent |
| D08 | 09/02/2026 | wound_care_note | Wound clinic visit (current) | Kestrel Ardent |
| D09 | 09/02/2026 | wound_treatment_record | Wound treatment and procedure log | Jory Calloway-Reyes |
| D10 | 09/02/2026 | offloading_record | Offloading device record | Jory Calloway-Reyes |
| D11 | 09/02/2026 | allergy_list | Allergy list | Jory Calloway-Reyes |

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
