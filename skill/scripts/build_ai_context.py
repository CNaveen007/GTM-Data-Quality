import argparse
import csv
import json
from pathlib import Path

def load_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))
def load_findings(path):
    with path.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))
def build_context(records, findings):
    records_by_id = {}
    for row_number, row in enumerate(records, start=2):
        record_id = (row.get("record_id") or "").strip()
        if not record_id:
            raise ValueError(f"Source row {row_number}: record_id is required.")
        if record_id in records_by_id:
            raise ValueError(f"Source row {row_number}: duplicate record_id '{record_id}'.")
        records_by_id[record_id] = row
    findings_by_id = {}
    conflict_accounts = set()
    for row_number, finding in enumerate(findings, start=2):
        record_id = (finding.get("record_id") or "").strip()
        if not record_id:
            raise ValueError(f"Finding row {row_number}: record_id is required.")
        if record_id not in records_by_id:
            raise ValueError(
                f"Finding row {row_number}: record_id '{record_id}' "
                "does not exist in source records."
            )
        findings_by_id.setdefault(record_id, []).append(finding)
        if finding.get("issue_type") == "Conflict" and finding.get("field") == "company_domain":
            account = (records_by_id[record_id].get("account_name") or "").strip().lower()
            if account:
                conflict_accounts.add(account)
    reviewed_records = []
    for record_id, record_findings in findings_by_id.items():
        record = records_by_id[record_id]
        reviewed_records.append(
            {
                "record": record,
                "findings": record_findings,
            }
        )
    # Include account peers as evidence even when they have no findings themselves.
    for record_id, record in records_by_id.items():
        account = (record.get("account_name") or "").strip().lower()
        if account in conflict_accounts and record_id not in findings_by_id:
            reviewed_records.append({"record": record, "findings": []})
    issue_counts = {}
    for finding in findings:
        issue_type = finding.get("issue_type", "Unknown")
        issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
    severity_counts = {}
    for finding in findings:
        severity = finding.get("severity", "Unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    return {
        "purpose": (
            "Provide structured context for reviewing GTM data-quality "
            "findings and recommending practical next steps."
        ),
        "records_reviewed": len(records),
        "records_with_findings": len(findings_by_id),
        "total_findings": len(findings),
        "findings_by_type": issue_counts,
        "findings_by_severity": severity_counts,
        "records": reviewed_records,
    }
def main():
    parser = argparse.ArgumentParser(
        description="Build structured AI context from GTM audit findings."
    )
    parser.add_argument(
        "--records",
        default="data/gtm_accounts_contacts.csv",
        help="Path to the source GTM CSV.",
    )
    parser.add_argument(
        "--findings",
        default="output/audit_findings.csv",
        help="Path to the audit findings CSV.",
    )
    parser.add_argument(
        "--output",
        default="output/ai_context.json",
        help="Path for the generated context file.",
    )
    args = parser.parse_args()
    records_path = Path(args.records)
    findings_path = Path(args.findings)
    output_path = Path(args.output)
    if not records_path.exists():
        raise SystemExit(
            "Error: source records file not found: "
            + str(records_path)
        )
    if not findings_path.exists():
        raise SystemExit(
            "Error: audit findings file not found: "
            + str(findings_path)
        )
    records = load_csv(records_path)
    findings = load_findings(findings_path)
    try:
        context = build_context(records, findings)
    except ValueError as error:
        raise SystemExit(f"Error: {error}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(context, file, indent=2)
    print()
    print("AI context created")
    print("------------------")
    print(f"Records reviewed: {context['records_reviewed']}")
    print(f"Records with findings: {context['records_with_findings']}")
    print(f"Total findings: {context['total_findings']}")
    print()
    print(f"Context written to: {output_path}")
if __name__ == "__main__":
    main()
