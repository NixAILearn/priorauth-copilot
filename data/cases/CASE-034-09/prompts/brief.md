# Case brief: CASE-034-09

You are writing one document of a synthetic prior authorization packet for Northwind Health Plan, a fictional Medicare Advantage plan. Everything is invented: the patient, the clinicians, the clinics. The packet is test data for an AI review copilot; nothing in it may mention AI, testing or this brief.

## Patient
- Name: Nadir Yardley (synthetic ID SYN-0030)
- Date of birth: 08/31/1955; sex: female
- Background diagnoses (ICD-10-CM): E11.621, E11.42, I10, N18.31
- Summary: 71-year-old woman; the wound notes say the ABI was normal, but the vascular report is not in the packet.

## Request
- Received 09/13/2026 (standard review); service NHP-P-2017: Bilayer skin substitute graft (fictional product, no animal-derived components), weekly applications.
- Diagnoses: E11.621, E11.42
- Target ulcer U1: left plantar first metatarsal head (L97.522), 4 applications

## Clinicians (use these names and nobody else)
- Primary care physician: Dr. Kestrel Marchetti-Lowe
- Clinical laboratory: Wren Thackeray-Ng
- Wound care nurse practitioner: Zeno Strathmore
- Wound clinic: Yusra Fenwick-Osei

## Documents in this packet, by date

| ID | Date | Type | Title | Author |
| --- | --- | --- | --- | --- |
| D01 | 07/20/2026 | office_visit_note | Primary care visit | Dr. Kestrel Marchetti-Lowe |
| D04 | 08/03/2026 | wound_care_note | Wound clinic visit (baseline) | Zeno Strathmore |
| D02 | 08/04/2026 | lab_result | Hemoglobin A1c result | Wren Thackeray-Ng |
| D05 | 08/10/2026 | wound_care_note | Wound clinic visit | Zeno Strathmore |
| D06 | 08/17/2026 | wound_care_note | Wound clinic visit | Zeno Strathmore |
| D07 | 08/24/2026 | wound_care_note | Wound clinic visit | Zeno Strathmore |
| D08 | 08/31/2026 | wound_care_note | Wound clinic visit | Zeno Strathmore |
| D09 | 09/07/2026 | wound_care_note | Wound clinic visit (current) | Zeno Strathmore |
| D10 | 09/07/2026 | wound_treatment_record | Wound treatment and procedure log | Yusra Fenwick-Osei |
| D11 | 09/07/2026 | offloading_record | Offloading device record | Yusra Fenwick-Osei |
| D12 | 09/07/2026 | allergy_list | Allergy list | Yusra Fenwick-Osei |

## Rules for every document
1. Write in the voice of the stated author, as a real clinical record of that type would read.
2. Copy each anchor phrase exactly, character for character, inside a natural sentence or table row, and keep each anchor on one line.
3. Never write procedure billing codes of any kind. ICD-10-CM codes only where the brief gives them. No ZIP codes, phone numbers or other five-digit numbers.
4. No date later than the document's own date. Write dates as MM/DD/YYYY.
5. Never use any phrase in the forbidden list, in any form.
6. No clinical fact that would change a coverage criterion beyond what the prompt states: no extra diagnoses, procedures, devices, allergies or test results that touch the policy.
7. HBA1C: the only values allowed anywhere in the packet are 8.1.

## Forbidden phrases (whole packet)
"Left ABI:", "Right ABI:", "TcPO2:", "Toe pressure:"
