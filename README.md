# GTM Data Quality

## What this is

A CSV-based go-to-market (GTM) data-quality skill for account and contact records. The Python layer finds deterministic data-quality issues. The Agent Skill uses those findings to produce a GTM-oriented review with recommendations for human approval.

## Problem

GTM teams depend on account and contact data for outreach, segmentation, account matching, routing, and reporting.

This prototype surfaces issues that may affect those workflows:

- Missing account or contact attributes.
- Invalid email or company-domain formats.
- Stale records.
- Possible duplicate contacts.
- Account/domain conflicts.

The review explains potential workflow effects; it does not establish actual business outcomes.

For a GTM team, the workflow is intended to reduce manual review effort by turning individual data-quality problems into a consistent, record-level cleanup list that can be reviewed and acted on.

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

Docs/
  GTM_Data_Quality_Overview.pdf
  GTM_Data_Quality_Overview.pptx

README.md
.gitignore
```

- `data/` contains the sample CSV and a short description.
- `skill/SKILL.md` defines the agent workflow, review format, and guardrails.
- `skill/scripts/validate_data.py` checks the source records and writes findings.
- `skill/scripts/build_ai_context.py` combines source records and findings into structured review context.
- `examples/sample_review.md` shows an AI-assisted review of the sample data.
- `Docs/` contains the one-page/single-slide project overview.
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

The sample data is synthetic and is used only to demonstrate the workflow.

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

Once `ai_context.json` is created successfully, start the agent review:

```sh
codex
```

Then enter the following prompt in Codex:

```text
Review the GTM audit results and give me the final review.
```

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

## Finding types and severity

The validator uses these finding types:

- **Missing:** an expected value is absent.
- **Invalid:** a value violates a deterministic validation rule.
- **Duplicate:** records appear to represent the same contact based on the implemented duplicate logic.
- **Conflict:** related values disagree, such as an email/company-domain mismatch or account/domain conflict.
- **Stale:** `last_updated` is older than the configured stale-data threshold.
- **Review:** the value looks suspicious, but the available evidence is not enough to prove it is incorrect.

Severity is represented as:

- **High**
- **Medium**
- **Low**

Severity indicates how much attention an issue may deserve. It does not mean the system has proven that a record is wrong.

## AI-assisted review

Use `skill/SKILL.md` to guide the agent after the scripts succeed.

The agent reads the generated context and findings to:

- Group related findings and retain every affected record ID.
- Explain potential GTM impact.
- Identify items that need attention and explain their priority.
- Recommend practical next actions.
- Distinguish confirmed findings from items needing verification.

`build_ai_context.py` prepares structured context; it does not call an AI model or generate the narrative review.

The agent should preserve original values, avoid inventing missing information, and not use web search to fill gaps. It should not silently modify source data or automatically apply remediation. Recommendations require human review and approval.

## Example output

[View the sample review](examples/sample_review.md).

The sample review contains:

- an audit summary
- grouped priority findings
- potential GTM impact
- recommended actions
- items needing verification

Record IDs link the review back to the source data.

The sample review uses audit date **2026-09-22** and a **180-day** stale threshold:

- **27 records reviewed**
- **17 records with findings**
- **19 total findings**

| Issue type | Findings |
|---|---:|
| Missing | 6 |
| Invalid | 2 |
| Stale | 3 |
| Conflict | 5 |
| Review | 1 |
| Duplicate | 2 |

Severity totals for the sample are:

| Severity | Findings |
|---|---:|
| High | 2 |
| Medium | 14 |
| Low | 3 |

## Design decisions

### Why a Skill plus Python?

Python is responsible for deterministic checks that should be repeatable and auditable, such as missing values, format validation, freshness, duplicate signals, and conflicts.

The Agent Skill provides the instruction layer for interpreting those findings in a GTM context. It tells the agent how to group findings, explain potential impact, recommend next actions, and distinguish confirmed findings from items that need verification.

This separation keeps objective validation in code while using AI where interpretation adds value.

### Why not only use a Python script?

A Python script can identify data-quality issues, but the Agent Skill adds a reusable instruction layer for how those findings should be interpreted and communicated.

The goal is not only to produce a list of errors. The agent should turn that evidence into a useful GTM review while preserving traceability and human approval.

### Why not use a direct MCP call?

I intentionally did not add a direct MCP integration in this POC.

Apollo explicitly allows a structured CSV or spreadsheet as the external data source for the data-hygiene option. Using CSV kept the V1 focused on the data-quality workflow, deterministic validation, evidence traceability, and Agent Skill design rather than spending most of the implementation time on live-system connectivity.

A production version could replace the CSV with a CRM or API-backed source.

### How is the data structured for the agent?

`build_ai_context.py` combines the deterministic findings with the relevant source records and keeps the findings linked by `record_id`.

For account/domain conflicts, it also includes relevant account peers so the agent has the surrounding context needed to explain the conflict.

This creates a focused evidence package rather than asking the model to rediscover quality problems from the raw CSV.

### What was deliberately left out?

The POC intentionally does not include:

- Live CRM writes.
- Automatic enrichment.
- Automatic remediation.
- Fuzzy entity resolution.
- Email deliverability verification.
- Domain ownership verification.
- Production-scale processing.

These were left out to keep the prototype focused and to avoid making unsupported changes to source data.

## Assumptions

### Data source

I assumed a structured CSV was sufficient for the POC because the exercise explicitly allows CSV for the data-hygiene option.

### Freshness

I used **180 days** as the initial stale-data threshold. This is a configurable prototype assumption, not a universal business rule.

### Ambiguous values

I assumed that ambiguous cases, such as an email domain that differs from the company domain, should be surfaced for review rather than automatically treated as incorrect.

### Remediation

I assumed that a human should approve changes before any production write-back.

### Duplicate matching

I assumed that repeated normalized email addresses are a strong duplicate signal, while matching first and last names without an email is a weaker signal that should still require review.

## Where AI helped, and where I did not trust it

AI is used for interpretation rather than deterministic validation.

It helps with:

- Grouping related findings.
- Explaining potential GTM impact.
- Explaining why findings may deserve attention.
- Recommending practical next actions.
- Identifying cases that need verification.

I did not rely on the model to determine whether deterministic conditions were true. Those checks are produced by Python first.

I also did not trust the model to:

- Invent missing values.
- Decide that an ambiguous domain mismatch is definitely wrong.
- Automatically merge records.
- Automatically change source data.
- Claim business outcomes that are not supported by the data.

For the AI-assisted review, I checked that the recommendations remained grounded in the deterministic findings and the relevant source records, that affected `record_id` values were retained, and that the agent did not introduce unsupported values or silently modify the source data.

The intended boundary is:

```text
Python
Deterministic evidence
        ↓
Agent Skill
Interpretation and GTM context
        ↓
Human
Verification and approval
```

## Human-in-the-loop

The POC uses a human-review step before remediation.

The workflow is:

```text
System detects issue
        ↓
Agent explains the issue
        ↓
Agent recommends an action
        ↓
Human verifies
        ↓
Human decides what to change
```

This is intentional because a suspicious value is not always a wrong value.

For example:

- A different email domain may be a legitimate partner or consultant.
- An employee count of zero may need verification rather than automatic rejection.
- A matching name does not necessarily mean two records are the same person.
- A missing field does not tell the system what the correct replacement should be.

## Production hardening

This repository is a proof of concept. Before real GTM users depend on it, I would harden several areas.

### Reliability

- Add stronger automated test coverage.
- Add pipeline validation and failure handling.
- Add retries where external systems are involved.
- Add monitoring and alerting.
- Track successful and failed audit runs.

### Security

- Add authentication and authorization.
- Use least-privilege access.
- Protect production credentials and sensitive data.
- Add an audit trail for any write-back operation.

### Scale

- Replace the sample CSV workflow with a live CRM or API-backed source.
- Support larger datasets through controlled batch or incremental processing.
- Avoid unnecessary repeated processing of unchanged records.

### Accuracy

- Expand field-level validation.
- Add stronger entity resolution.
- Make quality rules and thresholds configurable.
- Measure false-positive and false-negative behavior on representative data.
- Improve handling of ambiguous records.

### Remediation

- Add an explicit approval workflow.
- Validate proposed changes before write-back.
- Keep before/after values and audit history.
- Prevent automatic changes when confidence or evidence is insufficient.

## Current limitations

- This is a proof of concept using CSV data; it does not integrate with a live CRM.
- Email and domain checks are basic format checks. They do not establish deliverability or ownership.
- Duplicate matching is heuristic, not fuzzy entity resolution. A match is a reason to review records, not permission to merge them.
- Account conflict checks detect one account name with multiple domains, not different account names sharing a domain.
- `city`, `country`, and `phone_number` are required headers but are not checked for completeness or validity.
- Stale records need verification; age does not prove inaccuracy.
- Future dates are not flagged as stale.
- The context builder checks record-ID links but does not prove that findings came from the current source file or audit settings. Use files from the same successful run and check their consistency.
- Remediation is intentionally human-reviewed. The workflow recommends changes rather than applying them.

## POC boundary

The core boundary is:

```text
Source data
    ↓
Deterministic validation
    ↓
Structured evidence
    ↓
AI interpretation
    ↓
Human approval
```

The source CSV is not silently modified.

The current POC does not perform live CRM writes or automatic remediation.

## Demo flow

The intended demo is:

1. Start with the one-pager and explain the GTM problem.
2. Run `validate_data.py`.
3. Show a few findings from `audit_findings.csv`.
4. Run `build_ai_context.py`.
5. Start Codex.
6. Ask:

```text
Review the GTM audit results and give me the final review.
```

7. Show the final GTM-oriented review.
8. Explain the AI boundary and human approval step.
9. Close with the production-hardening plan.

The demo is intentionally focused on showing the working flow rather than walking through every line of code.

## Summary

The main design principle of this project is:

**Deterministic evidence first. AI interpretation second. Human approval last.**

The POC is intentionally small, reproducible, and reviewable. It demonstrates how an Agent Skill can sit on top of structured GTM data, use deterministic checks for objective validation, and use AI to turn those findings into a practical review without silently changing the underlying records.
