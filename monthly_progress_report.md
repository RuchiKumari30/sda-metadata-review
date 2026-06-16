# Monthly Progress Report – Metadata Registry
## State Data Authority, Uttar Pradesh
**Reporting Period:** 1–25 April 2026
**Prepared by:** Data Analyst, SDA-UP
**Addressed to:** Data Governance Lead, State Data Authority

---

## 1. Summary of Progress

As of 25 April 2026, the SDA has received **25 metadata submissions** from 21 government departments in response to the first intake cycle for the UP Metadata Platform. Of these, **14 submissions (56%) have been formally approved** and are now part of the registry catalogue. The remaining **11 submissions (44%) are pending correction** and are at various stages of follow-up.

| Status | Count | Share |
|--------|-------|-------|
| Approved | 14 | 56% |
| Pending – awaiting correction | 11 | 44% |
| **Total received** | **25** | **100%** |

---

## 2. Top Three Compliance Issues

**Issue 1 – Missing Data Owner Name (4 submissions)**
Submissions from the Energy Department, Home Department, Basic Education Department, and Labour Department were received without a data owner name. This is a mandatory field under SDA standards and is required for accountability and escalation. The pattern suggests that some departments are delegating the submission task to IT staff who do not have visibility of the responsible officer. A brief guidance note to department heads clarifying that the data owner must be a named individual — not just a designation — is recommended.

**Issue 2 – Invalid or Non-Standard Date Formats (2 submissions)**
Two submissions used non-standard date formats: META-010 (Energy Department) used DD-MM-YYYY in the `last_updated` field, and META-015 (Women & Child Development) used MM/DD/YYYY in the submission date. The SDA platform requires ISO 8601 format (YYYY-MM-DD) throughout. This is a straightforward technical fix, but the recurrence suggests that the submission template or form does not enforce date formatting. Introducing format validation at the point of submission would eliminate this class of error entirely.

**Issue 3 – DPDP Classification Mismatch (3 submissions)**
Three datasets containing personal data — META-005 (Patient Admission Records), META-007 (PM-KISAN Farmer Registration), and META-020 (PDS Beneficiary Records) — were either misclassified as Public or had a blank classification. Under the DPDP Act, datasets with personal data must be classified as Restricted or Confidential. This is the most consequential quality issue in this batch, as it has direct legal and privacy implications. The departments concerned have been sent follow-up notices; two (Agriculture and Food & Civil Supplies) have not yet responded.

---

## 3. Departments with Unresolved Pending Items

The following departments have pending submissions with no response to the SDA's follow-up notice:

| Department | Submission | Follow-up Sent | Days Without Response |
|---|---|---|---|
| Energy Department | META-010 | 13 April 2026 | 12 days |
| Basic Education | META-002 | 9 April 2026 | 16 days |
| Home Department | META-013 | 15 April 2026 | 10 days |
| Agriculture Department | META-007 | 11 April 2026 | 14 days |
| Food & Civil Supplies | META-020 | 18 April 2026 | 7 days |
| Health Department | META-005 | 10 April 2026 | 15 days |
| Labour Department | META-024 | 20 April 2026 | 5 days |

Energy and Basic Education have been waiting the longest — over two weeks — without a revised submission or acknowledgement.

---

## 4. Recommended Actions for the Next Two Weeks

**Action 1 – Escalate non-responding departments to nodal officer level**
For the five departments with follow-ups outstanding for more than 10 days (Energy, Basic Education, Home, Agriculture, Health), the SDA should send a second follow-up addressed directly to the department's nodal officer or Secretary-level contact, with a firm deadline of 5 May 2026. This is particularly urgent for META-005 and META-007, which have DPDP classification issues.

**Action 2 – Issue a clarification circular on date format and data owner fields**
A one-page guidance note should be circulated to all 21 departments clarifying the two most easily-avoidable errors: (a) the required ISO 8601 date format (YYYY-MM-DD), and (b) the requirement for a named individual in the data owner field. This will reduce formatting errors in the second intake cycle.

**Action 3 – Begin onboarding the 14 approved datasets into the catalogue**
With 14 submissions fully approved, the SDA technical team can now begin the next step: loading these records into the metadata catalogue and making them discoverable. Starting this process in parallel with the follow-up cycle will keep the platform on schedule.

---
*This report reflects data as of 25 April 2026. All figures are drawn from the SDA's compliance tracking records.*
