---
name: gtm-data-quality
description: Audit GTM account and contact records for missing, invalid, stale, or conflicting information and recommend practical fixes for review.
---

# GTM Data Quality

## Purpose

Audit go-to-market account and contact records for data quality issues that could affect sales outreach, segmentation, routing, reporting, and account management.

The skill is designed to work with the supplied structured GTM dataset and produce findings that are easy for a sales or revenue operations user to review.

## Data Source

The source is a structured CSV containing account and contact records.

The current dataset contains these fields:

### Account fields

- `record_id`
- `account_name`
- `company_domain`
- `industry`
- `employee_count`
- `city`
- `country`
- `last_updated`

### Contact fields

- `contact_first_name`
- `contact_last_name`
- `contact_title`
- `contact_email`
- `phone_number`

Do not assume fields exist beyond those provided in the input file.

## Workflow

### 1. Inspect the source data

Before analyzing records:

- Read the CSV.
- Identify the available columns.
- Count the records.
- Check for blank or null values.
- Check basic data types and formatting.
- Preserve the original values for audit purposes.

Use the supplied dataset as the source of truth for the audit.

### 2. Check completeness

Identify important fields that are missing or blank.

Check, where present:

- `account_name`
- `company_domain`
- `industry`
- `employee_count`
- `city`
- `country`
- `contact_first_name`
- `contact_last_name`
- `contact_title`
- `contact_email`
- `phone_number`
- `last_updated`

A missing value should be reported as a data-quality issue, but do not invent a replacement value.

### 3. Check validity

Review values for obvious formatting or business-rule problems.

Examples:

#### Email

Check whether `contact_email` appears to have a valid email structure.

Flag values that clearly do not contain a usable email format.

#### Employee count

Check `employee_count` for:

- negative values
- impossible values
- zero values that may require review

Do not automatically assume that every unusual company size is incorrect.

#### Domain

Check whether `company_domain` is populated and appears to be consistently formatted.

#### Dates

Check whether `last_updated` contains a usable date.

### 4. Check consistency

Look for conflicts or duplicate-looking records across the available fields.

Examples:

- multiple records with the same `company_domain` and contact information
- the same contact appearing more than once
- inconsistent account names associated with the same company domain
- contact email domains that differ from the company domain
- conflicting values across otherwise related records

Do not automatically classify a difference as an error.

For example, a contact email using a different domain may be a legitimate situation. Mark it as something to verify when the available data is insufficient to confirm the issue.

### 5. Check freshness

Use `last_updated` to identify records that may need review because they have not been updated recently.

Compare dates using the current execution date when available.

Classify freshness carefully:

- recently updated: no freshness issue
- older record: review
- significantly stale record: higher-priority review

Do not create or modify dates that are not present in the source data.

### 6. Classify findings

For each issue, capture:

- `record_id`
- `account_name`
- affected field
- issue category
- severity
- current value
- reason
- recommended action

Use these issue categories:

- Completeness
- Validity
- Consistency
- Freshness
- Duplicate

Use these severity levels:

- High
- Medium
- Low

Severity guidance:

**High**
A confirmed issue that could materially interfere with GTM execution, such as unusable contact information or a serious record conflict.

**Medium**
An issue that reduces the usefulness or reliability of the record but does not necessarily block normal activity.

**Low**
A minor cleanup item or a possible issue that should be reviewed.

### 7. Separate confirmed issues from review items

Do not treat every anomaly as a confirmed error.

Use language such as:

- Confirmed issue
- Potential issue
- Needs verification

Examples:

- A clearly malformed email can be treated as a confirmed validity issue.
- A missing industry can be treated as a confirmed completeness issue.
- A non-company email domain should generally be treated as a potential consistency issue unless the data provides stronger evidence.

### 8. Recommend remediation

For every finding, provide a practical next step.

Allowed actions include:

- Enrich
- Verify
- Correct
- Review
- Merge
- No action

Do not guess missing information.

For example:

If `industry` is blank:

> Recommended action: Enrich or verify the account industry.

Do not provide a fabricated industry value.

If `contact_email` is malformed:

> Recommended action: Verify the contact email before outreach.

### 9. Produce the audit output

Return a summary followed by detailed findings.

## Summary

Include:

- total records reviewed
- records with issues
- total findings
- findings by category
- findings by severity
- common patterns observed

## Findings

Use a table with:

| Record ID | Account | Field | Category | Severity | Current Value | Reason | Recommended Action |
|---|---|---|---|---|---|---|---|

Keep the explanation concise enough for a GTM user to act on.

### 10. Preserve the source data

Treat the input CSV as read-only.

Do not:

- overwrite the source file
- delete records
- silently modify values
- apply corrections without review

The skill should produce recommendations rather than silently changing GTM records.

## AI Usage

Use AI reasoning for:

- interpreting the business context of a finding
- explaining why an issue matters to a GTM workflow
- distinguishing likely issues from cases that need human verification
- summarizing patterns across multiple records
- turning technical findings into practical GTM actions

Use deterministic validation for straightforward checks such as:

- required fields
- email formatting
- negative employee counts
- date parsing
- duplicate detection

AI should not invent missing values or override deterministic evidence without explaining the reason.

## Guardrails

- Use the supplied CSV as the primary data source.
- Do not use web search as a substitute for the source data.
- Do not fabricate company or contact information.
- Do not silently modify source records.
- Preserve original field values in findings.
- Distinguish confirmed problems from potential problems.
- Explain the evidence behind each finding.
- Recommend verification when confidence is low.
- Keep human review in the loop before any CRM update.

## Expected Result

The result should give a GTM user a practical view of which account and contact records need attention, what is wrong or potentially wrong, why it matters, and what action should be taken next.

The objective is actionable data-quality cleanup rather than a generic data-quality score.
