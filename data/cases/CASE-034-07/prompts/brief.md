# Case brief: CASE-034-07

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Soren Ostrander (synthetic ID SYN-0002)
- Date of birth: 02/11/1952; sex: female
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10, N18.31
- Summary: 74-year-old woman with type 2 diabetes, peripheral neuropathy and stage 3a kidney disease; neuropathic ulcer under the right first metatarsal head treated weekly in a wound clinic for five weeks.

## Request
- Received 10/20/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: right plantar first metatarsal head (L97.512), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Amara Duvane
- Clinical laboratory: Corinne Calloway-Reyes
- Vascular lab technologist and interpreting physician: Pell Brightwater
- Wound care nurse practitioner: Jory Galbrecht
- Wound clinic: Vesna Lindqvist-Amari

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 08/25/2026 | office_visit_note | Primary care visit | Dr. Amara Duvane |
| D02 | 08/25/2026 | lab_result | Hemoglobin A1c result | Corinne Calloway-Reyes |
| D03 | 09/02/2026 | vascular_study_report | Ankle-brachial index study | Pell Brightwater |
| D04 | 09/08/2026 | wound_care_note | Wound clinic visit (baseline) | Jory Galbrecht |
| D05 | 09/15/2026 | wound_care_note | Wound clinic visit | Jory Galbrecht |
| D06 | 09/22/2026 | wound_care_note | Wound clinic visit | Jory Galbrecht |
| D07 | 09/29/2026 | wound_care_note | Wound clinic visit | Jory Galbrecht |
| D08 | 10/06/2026 | wound_care_note | Wound clinic visit | Jory Galbrecht |
| D09 | 10/13/2026 | wound_care_note | Wound clinic visit (current) | Jory Galbrecht |
| D10 | 10/13/2026 | wound_treatment_record | Wound treatment and procedure log | Vesna Lindqvist-Amari |
| D11 | 10/13/2026 | allergy_list | Allergy list | Vesna Lindqvist-Amari |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. HBA1C: the only values allowed anywhere in the packet are 8.4.

## Forbidden phrases (whole packet)
"boot", "felted foam", "off-load", "offload", "post-op shoe", "surgical shoe", "total contact cast", "walker"
