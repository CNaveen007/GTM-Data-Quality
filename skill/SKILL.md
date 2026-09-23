---
name: gtm-data-quality
description: Check GTM account and contact data for common quality issues and turn the findings into a reviewable cleanup list.
---

# GTM Data Quality

This skill helps review account and contact data before it is used by sales or revenue operations.

The goal is simple: find records that look incomplete, incorrect, outdated, or inconsistent and make it clear what should be reviewed.

## When to use this skill

Use this skill to audit a GTM account and contact CSV and recommend a reviewable cleanup plan.

Example request:

"Audit data/gtm_accounts_contacts.csv for GTM data-quality issues."

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

These columns are required by the current validator. Check the file before running the audit.

## How to run it

Run the commands from the repository root. Replace `<input_csv>` with the source CSV path and `YYYY-MM-DD` with the audit date. Use the same input file in both commands.

First, run the deterministic checks:

```text
python skill/scripts/validate_data.py <input_csv> --as-of YYYY-MM-DD
```

The default stale threshold is 180 days. Findings are written to `output/audit_findings.csv`.

After validation succeeds, build the review context:

```text
python skill/scripts/build_ai_context.py --records <input_csv> --findings output/audit_findings.csv
```

Then read `output/ai_context.json` before producing the final review. Use the context and findings from this run as evidence for the review.

## Failure behavior

Stop the workflow if either script fails, or if:

- the input file is missing
- required columns are missing
- record IDs are missing or duplicated in the source data
- findings have missing record IDs or refer to unknown record IDs
- the generated context is inconsistent with the source records or findings

Check that context counts and record-to-finding links agree with the generated findings. The context includes records with findings and may include account peers without findings; it is not a copy of every source record.

Explain the failure and what needs to be resolved before rerunning. Do not produce a final audit from partial output or files left over from an earlier run.

## What to check

Use the script findings to review the categories below. Do not redo deterministic validation unnecessarily.

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
- Review

Use `Review` when the value is unusual or potentially incorrect but the available data is not enough to confirm that it is actually wrong.

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

After the scripts run:

- Use the generated findings as evidence and preserve original values when describing them.
- Group related issues, including issues across records, and include every affected `record_id`.
- Identify which issues need attention first and explain the priority.
- Explain the likely business impact on GTM work, such as outreach, segmentation, or account review.
- Recommend a practical next action for each issue.
- Distinguish confirmed issues from items needing verification.

For example, AI can explain why a missing industry field may affect segmentation, but it should not guess what the industry should be.

When the data is ambiguous, say that the record needs review.

## Output

Use these sections in the final response, in this order:

```markdown
## Audit summary
## Priority findings
## GTM impact
## Recommended actions
## Items needing verification
```

In `Audit summary`, include the audit date, stale threshold, and a short summary:

- records reviewed
- records with issues
- number of findings
- findings by type
- findings by severity

In `Priority findings`, group and order the detailed findings by what needs attention first. Every finding must include its `record_id`; grouped findings must list all affected record IDs. Preserve original values in the details:

| Record ID | Account | Field | Issue Type | Severity | Current Value | Reason | Recommended Action |
|---|---|---|---|---|---|---|---|

In `GTM impact`, explain how the findings could affect GTM work and link the impact to the relevant record IDs. Do not claim an actual business outcome without evidence.

In `Recommended actions`, give practical next steps tied to record IDs. Suggested actions include:

- Review
- Verify
- Enrich
- Correct
- Merge
- No action

In `Items needing verification`, list ambiguous findings with their record IDs, what remains uncertain, and what a person should verify. If there are none, say so.

## Important guardrails

- Use the CSV as the source for the audit.
- Do not redo deterministic validation unnecessarily.
- Do not invent missing company or contact information.
- Do not use web search to replace the supplied data or fill gaps during the audit.
- Keep the original CSV unchanged; do not silently modify it.
- Do not apply remediation automatically or overwrite CRM or source data.
- Clearly separate confirmed issues from items that just need verification.
- When the evidence is unclear, recommend review instead of guessing.

## Design notes

Python handles deterministic checks. The skill handles interpretation and GTM recommendations.

CSV is the external structured data source for this POC. Source data is read-only, and recommended fixes require human review.

## Goal

The final result should be something a sales or RevOps user can actually work from: a short summary of the data quality problems, the records affected, and the next action for each one.
