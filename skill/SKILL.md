---
name: gtm-data-quality
description: Check GTM account and contact data for common quality issues and turn the findings into a reviewable cleanup list.
---

# GTM Data Quality

This skill helps review account and contact data before it is used by sales or revenue operations.

The goal is simple: find records that look incomplete, incorrect, outdated, or inconsistent and make it clear what should be reviewed.

## Input

The skill reads a CSV with account and contact information.

The current dataset includes:

- `record_id`
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

The available columns may change, so check the file before running the audit.

## What to check

### Missing fields

Look for important fields that are blank or missing.

Examples:

- account name
- company domain
- industry
- employee count
- contact name
- contact title
- contact email
- last updated date

Not every field needs to be present on every record, so the output should explain what is missing instead of treating every blank as a critical issue.

### Bad or unusual values

Look for values that clearly do not look right.

Examples:

- malformed email addresses
- negative employee counts
- employee count of zero that may need review
- invalid or badly formatted dates
- company domains that are blank or malformed

Only flag something when there is enough evidence in the record to support it.

### Possible duplicates and conflicts

Check for records that may represent the same person or company.

Examples:

- repeated contact information
- the same company domain appearing across duplicate-looking records
- different account names using the same domain
- contact email domains that don't match the company domain

A mismatch is not automatically an error. When it could be legitimate, mark it as a review item rather than a confirmed problem.

### Stale records

Use `last_updated` to find records that may be out of date.

Flag older records for review based on the date of the audit.

Do not make up dates or assume that an old record is definitely wrong.

## How to handle findings

For each issue, capture:

- `record_id`
- account name
- field
- issue type
- severity
- current value
- why it was flagged
- recommended action

Use these issue types:

- Missing
- Invalid
- Duplicate
- Conflict
- Stale

Use:

- High
- Medium
- Low

for severity.

Severity should reflect how much the issue could affect normal GTM work. For example, an unusable email is more important than a minor formatting issue.

## AI should help with interpretation

Use deterministic checks for things that can be checked reliably with code, such as:

- blank values
- email format
- duplicate records
- employee count
- date parsing

Use AI to help explain the findings and put them into a GTM context.

For example, AI can explain why a missing industry field may affect segmentation, but it should not guess what the industry should be.

When the data is ambiguous, say that the record needs review.

## Output

Start with a short summary:

- records reviewed
- records with issues
- number of findings
- findings by type
- findings by severity

Then provide the detailed findings:

| Record ID | Account | Field | Issue Type | Severity | Current Value | Why It Was Flagged | Recommended Action |
|---|---|---|---|---|---|---|---|

Recommended actions:

- Review
- Verify
- Enrich
- Correct
- Merge
- No action

## Important guardrails

- Use the CSV as the source for the audit.
- Do not invent missing company or contact information.
- Do not use web search to fill gaps during the audit.
- Keep the original CSV unchanged.
- Do not automatically overwrite CRM or source data.
- Clearly separate confirmed issues from items that just need verification.
- When the evidence is unclear, recommend review instead of guessing.

## Goal

The final result should be something a sales or RevOps user can actually work from: a short summary of the data quality problems, the records affected, and the next action for each one.
