# GTM Data Quality

## What this is

A CSV-based go-to-market (GTM) data-quality skill for account and contact records. The Python layer finds deterministic data-quality issues. The Agent Skill uses those findings to produce a GTM-oriented review with recommendations for human approval.

## Problem

This prototype surfaces issues that may affect outreach, segmentation, and account review:

- Missing account or contact attributes.
- Invalid email or company-domain formats.
- Stale records.
- Possible duplicate contacts.
- Account/domain conflicts.

The review explains potential workflow effects; it does not establish actual business outcomes.

## Repository structure

```text
data/
  README.md
  gtm_accounts_contacts.csv
skill/
  SKILL.md
  scripts/
    validate_data.py
    build_ai_context.py
examples/
  sample_review.md
output/                     # Generated runtime output; Git-ignored
  audit_findings.csv
  ai_context.json
README.md
.gitignore
```

- `data/` contains the sample CSV and a short description.
- `skill/SKILL.md` defines the agent workflow, review format, and guardrails.
- `skill/scripts/validate_data.py` checks the source records and writes findings.
- `skill/scripts/build_ai_context.py` combines source records and findings into structured review context.
- `examples/sample_review.md` shows an AI-assisted review of the sample data.
- `output/` holds generated files. The scripts create it as needed; it is ignored by Git.

## Input data

The current sample, `data/gtm_accounts_contacts.csv`, contains 27 records and these 13 required columns:

```text
record_id
account_name
company_domain
industry
employee_count
city
country
contact_first_name
contact_last_name
contact_title
contact_email
phone_number
last_updated
```

Each `record_id` must be present and unique. Required column headers are separate from completeness checks on individual values; some sample values are intentionally blank.

The validator accepts `last_updated` dates in `YYYY-MM-DD`, `MM/DD/YYYY`, and `YYYY/MM/DD` formats. Slash-separated month/day dates are interpreted month first.

## How to run

Use Python 3 and run these commands from the repository root. Both scripts use only the Python standard library.

First, validate the sample with a fixed audit date:

```sh
python skill/scripts/validate_data.py data/gtm_accounts_contacts.csv --as-of 2026-09-22
```

After validation succeeds, build the review context using the same source CSV:

```sh
python skill/scripts/build_ai_context.py --records data/gtm_accounts_contacts.csv --findings output/audit_findings.csv
```

The generated files are:

- `output/audit_findings.csv`: one row per finding, including record ID, account, field, issue type, severity, original value, reason, and recommended action.
- `output/ai_context.json`: summary counts and source records linked to their findings, plus relevant account peers for account-domain conflicts. It is not a copy of every source record.

The stale threshold defaults to 180 days and can be changed with `--stale-days`. Without `--as-of`, validation uses the current date. Both scripts support `--output` for a custom output path.

Stop if either command fails. Resolve the error before continuing, and do not use output left over from an earlier run as evidence for a new audit.

## What the validator checks

- **Required schema:** all 13 column headers must exist.
- **Missing values:** checks account name, company domain, industry, employee count, contact first and last names, contact title, contact email, and last-updated date.
- **Email/domain format:** flags malformed email addresses and basic company-domain format problems. Email/company-domain mismatches are flagged for verification.
- **Employee counts:** flags non-integer and negative values; zero is a review item.
- **Freshness:** flags parsed `last_updated` dates older than the stale threshold. Age greater than twice the threshold receives High severity.
- **Duplicate contacts:** matches trimmed, case-normalized email addresses, or matching first/last names among records without email.
- **Account-name/domain conflicts:** flags an account name associated with multiple company domains after trimming and case normalization.
- **Record ID integrity:** rejects missing or duplicate IDs.
- **Malformed CSV rows:** rejects rows whose cell count does not match the header.
- **Output/input path protection:** the validator rejects an output path that refers to its source CSV. This protection is not implemented in the context builder, so use a separate output path there.

These checks produce findings with issue types and severities. The agent interprets the evidence rather than replacing or unnecessarily repeating the deterministic checks.

## AI-assisted review

Use `skill/SKILL.md` to guide the agent after the scripts succeed. The agent reads the generated context and findings to:

- Group related findings and retain every affected record ID.
- Explain potential GTM impact.
- Identify items that need attention and explain their priority.
- Recommend practical next actions.
- Distinguish confirmed findings from items needing verification.

`build_ai_context.py` prepares structured context; it does not call an AI model or generate the narrative review.

The agent should preserve original values, avoid inventing missing information, and not use web search to fill gaps. It should not silently modify source data or automatically apply remediation. Recommendations require human review and approval.

## Example output

[View the sample review](examples/sample_review.md). It contains an audit summary, grouped priority findings, potential GTM impact, recommended actions, and items needing verification, with record IDs linking the review to the source data.

The sample review uses audit date **2026-09-22** and a **180-day** stale threshold: **27 records**, **17 records with findings**, and **19 total findings**.

| Issue type | Findings |
|---|---:|
| Missing | 6 |
| Invalid | 2 |
| Stale | 3 |
| Conflict | 5 |
| Review | 1 |
| Duplicate | 2 |

## Design notes

Python handles repeatable checks and preserves the evidence in structured files. The Agent Skill handles explanation, prioritization, and GTM recommendations. Separating these responsibilities lets a reviewer trace recommendations back to specific records and rules while keeping ambiguous decisions subject to human review.

## Assumptions and limitations

- This is a proof of concept using CSV data; it does not integrate with a live CRM.
- Email and domain checks are basic format checks. They do not establish deliverability or ownership.
- Duplicate matching is heuristic, not fuzzy entity resolution. A match is a reason to review records, not permission to merge them.
- Account conflict checks detect one account name with multiple domains, not different account names sharing a domain.
- `city`, `country`, and `phone_number` are required headers but are not checked for completeness or validity.
- Stale records need verification; age does not prove inaccuracy. Future dates are not flagged.
- The context builder checks record-ID links but does not prove that findings came from the current source file or audit settings. Use files from the same successful run and check their consistency.
- Remediation is intentionally human-reviewed. The workflow recommends changes rather than applying them.
