# GTM Data Quality Review

## Audit summary

- Audit date: **2026-09-22** (`--as-of` date); stale threshold: **180 days**.
- **27 records reviewed**, **17 records with findings**, **19 total findings**.
- Issue counts: Missing 6, Invalid 2, Stale 3, Conflict 5, Review 1, Duplicate 2.
- Severity counts: High 2, Medium 14, Low 3.

This AI-assisted review interprets the existing audit findings and source records; it does not rerun checks or apply remediation.

## Priority findings

| Priority | Record IDs | Finding |
|---|---|---|
| First | R012, R021 | High: confirmed invalid email formats: R012 `lucas.suncrest.example`; R021 `masonfairwaymobility.example`. |
| Next | R015, R016 | Medium: both use `sophia@atlaseng.example`. The repeated email is confirmed; merging requires review. |
| Next | R001, R026 | Medium: Northstar Analytics has conflicting domains: R001 `northstar-analytics.example`; R026 `northstar.example`. Neither is proven incorrect. |
| Next | R009, R019 | Medium: missing `company_domain` on both records. |
| Next | R011, R019 | Medium: missing `employee_count` on both records. |
| Next | R010, R020 | Medium: missing `industry` on both records. |
| Next | R026 | Medium review item: `employee_count` is `0`, not a confirmed error. |
| Refresh | R013, R017, R022 | Medium: stale `last_updated` values: R013 `10/3/2025`; R017 `1/5/2026`; R022 `12/1/2025`. Age does not prove inaccuracy. |
| Verify | R014, R023, R027 | Low: external email-domain conflicts: R014 `james@partner-mail.example`; R023 `jack@personal-mail.example`; R027 `michelle@consulting-mail.example`. These may be legitimate. |

## GTM impact

- **Outreach:** R012 and R021 have unusable email formats. R015 and R016 could receive repeated outreach if both records enter a sequence.
- **Matching and routing:** Missing domains on R009 and R019 could impede account matching. Conflicting domains on R001 and R026 could split account activity or ownership if domain-based routing is used.
- **Segmentation:** Missing industries on R010 and R020 could affect campaign selection. Missing employee counts on R011 and R019, and the unverified zero on R026, could affect size-based qualification and routing.
- **Reporting:** R015 and R016 could inflate contact counts; R001 and R026 could fragment account reporting if they represent the same organization.
- **Account review:** R013, R017, and R022 warrant freshness checks. R014, R023, and R027 may need manual contact-to-account verification where workflows expect matching domains.

These are potential workflow effects, not observed business outcomes.

## Recommended actions

- **R012, R021:** Verify intended email addresses before outreach; do not guess corrections.
- **R015, R016:** Review whether both records are needed; approve any consolidation only after confirming redundancy.
- **R001, R026:** Confirm organizational identity and the relationship between the two domains before changing or consolidating records.
- **R009, R019:** Verify company domains before enrichment; do not automatically copy contact email domains.
- **R011, R019, R026:** Verify employee counts before size-based decisions; distinguish missing values from R026's `0`.
- **R010, R020:** Confirm industry using the approved taxonomy; do not infer it from account names.
- **R013, R017, R022:** Have the account owner review current account and contact details before recommending updates.
- **R014, R023, R027:** Confirm affiliation and the intended outreach address; retain legitimate values and document exceptions.

## Items needing verification

- **R014:** Confirm whether `james@partner-mail.example` legitimately serves the contact associated with company domain `redwoodrobotics.example`; do not assume a partner relationship.
- **R023:** Confirm whether `jack@personal-mail.example` is the intended business outreach address for the contact associated with `summithome.example`.
- **R027:** Confirm whether `michelle@consulting-mail.example` is appropriate for the contact associated with `blueridge.example`; do not assume consulting status.
- **R026:** Determine whether employee count `0` is intentional, a placeholder, or incorrect. R001's `420` is not an established replacement.
- **R001, R026:** Determine whether the domains reflect one organization, separate entities, or an error.
- **R015, R016:** Confirm whether the repeated contact records should be consolidated.
- **R013, R017, R022:** Verify whether the underlying details remain accurate despite their age.
