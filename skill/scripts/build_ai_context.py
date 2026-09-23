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
    records_by_id = {
        row.get("record_id", "").strip(): row
        for row in records
        if row.get("record_id")
    }
    findings_by_id = {}
    for finding in findings:
        record_id = finding.get("record_id", "").strip()
        if not record_id:
            continue
        findings_by_id.setdefault(record_id, []).append(finding)
    reviewed_records = []
    for record_id, record_findings in findings_by_id.items():
        record = records_by_id.get(record_id)
        if not record:
            continue
        reviewed_records.append(
            {
                "record": record,
                "findings": record_findings,
            }
        )
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
        "records_with_findings": len(reviewed_records),
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
    context = build_context(records, findings)
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
