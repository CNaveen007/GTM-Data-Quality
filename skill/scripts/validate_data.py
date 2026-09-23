import argparse
import csv
import re
from collections import Counter
from datetime import datetime, date
from pathlib import Path


REQUIRED_COLUMNS = {
    "record_id",
    "account_name",
    "company_domain",
    "industry",
    "employee_count",
    "city",
    "country",
    "contact_first_name",
    "contact_last_name",
    "contact_title",
    "contact_email",
    "phone_number",
    "last_updated",
}
def is_blank(value):
    return value is None or not str(value).strip()
def normalize(value):
    if value is None:
        return ""
    return str(value).strip().lower()
def valid_email(email):
    if is_blank(email):
        return False
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email.strip()) is not None
def parse_date(value):
    if is_blank(value):
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None
def add_finding(findings, row, field, issue_type, severity, reason, action):
    findings.append(
        {
            "record_id": row.get("record_id", ""),
            "account_name": row.get("account_name", ""),
            "field": field,
            "issue_type": issue_type,
            "severity": severity,
            "current_value": row.get(field, ""),
            "reason": reason,
            "recommended_action": action,
        }
    )
def validate_rows(rows, as_of, stale_days):
    findings = []
    for row in rows:
        account = row.get("account_name", "").strip()
        company_domain = normalize(row.get("company_domain"))
        email = normalize(row.get("contact_email"))
        # Completeness checks
        completeness_fields = [
            "account_name",
            "company_domain",
            "industry",
            "employee_count",
            "contact_first_name",
            "contact_last_name",
            "contact_title",
            "contact_email",
            "last_updated",
        ]
        for field in completeness_fields:
            if is_blank(row.get(field)):
                add_finding(
                    findings,
                    row,
                    field,
                    "Missing",
                    "Medium",
                    f"{field} is blank for this record.",
                    "Review or enrich the field.",
                )
        # Email validity
        if not is_blank(row.get("contact_email")) and not valid_email(
            row.get("contact_email")
        ):
            add_finding(
                findings,
                row,
                "contact_email",
                "Invalid",
                "High",
                "The contact email does not match a usable email format.",
                "Verify the contact email before outreach.",
            )
        # Employee count
        employee_value = row.get("employee_count", "").strip()
        if employee_value:
            try:
                employee_count = int(employee_value)

                if employee_count < 0:
                    add_finding(
                        findings,
                        row,
                        "employee_count",
                        "Invalid",
                        "High",
                        "Employee count is negative.",
                        "Correct or verify the employee count.",
                    )
                elif employee_count == 0:
                    add_finding(
                        findings,
                        row,
                        "employee_count",
                        "Review",
                        "Medium",
                        "Employee count is zero and may require verification.",
                        "Verify the employee count.",
                    )
            except ValueError:
                add_finding(
                    findings,
                    row,
                    "employee_count",
                    "Invalid",
                    "Medium",
                    "Employee count is not stored as a valid whole number.",
                    "Correct or verify the employee count.",
                )
        # Domain validity
        if company_domain and (
            " " in company_domain or "." not in company_domain
        ):
            add_finding(
                findings,
                row,
                "company_domain",
                "Invalid",
                "Medium",
                "Company domain does not look like a valid domain.",
                "Verify the company domain.",
            )
        # Contact email vs company domain
        if email and company_domain and valid_email(email):
            email_domain = email.split("@", 1)[1]
            if email_domain != company_domain:
                add_finding(
                    findings,
                    row,
                    "contact_email",
                    "Conflict",
                    "Low",
                    (
                        f"Contact email domain '{email_domain}' does not match "
                        f"company domain '{company_domain}'. This may be legitimate "
                        "but should be verified."
                    ),
                    "Verify the contact's email domain.",
                )
        # Freshness
        last_updated = parse_date(row.get("last_updated"))
        if row.get("last_updated") and last_updated is None:
            add_finding(
                findings,
                row,
                "last_updated",
                "Invalid",
                "Medium",
                "Last updated value could not be parsed as a date.",
                "Correct or verify the date.",
            )
        elif last_updated:
            age_days = (as_of - last_updated).days
            if age_days > stale_days:
                severity = "Medium"
                if age_days > stale_days * 2:
                    severity = "High"
                add_finding(
                    findings,
                    row,
                    "last_updated",
                    "Stale",
                    severity,
                    (
                        f"Record was last updated {age_days} days ago, "
                        f"which is older than the {stale_days}-day review threshold."
                    ),
                    "Review and refresh the record.",
                )
    return findings
def find_duplicates(rows):
    findings = []
    seen_contacts = Counter()
    seen_domains = Counter()
    for row in rows:
        contact_key = (
            normalize(row.get("contact_first_name")),
            normalize(row.get("contact_last_name")),
            normalize(row.get("contact_email")),
        )
        domain_key = normalize(row.get("company_domain"))
        if all(contact_key):
            seen_contacts[contact_key] += 1
        if domain_key:
            seen_domains[domain_key] += 1
    duplicate_contact_keys = {
        key for key, count in seen_contacts.items() if count > 1
    }
    duplicate_domain_keys = {
        key for key, count in seen_domains.items() if count > 1
    }
    for row in rows:
        contact_key = (
            normalize(row.get("contact_first_name")),
            normalize(row.get("contact_last_name")),
            normalize(row.get("contact_email")),
        )
        domain_key = normalize(row.get("company_domain"))
        if contact_key in duplicate_contact_keys:
            findings.append(
                {
                    "record_id": row.get("record_id", ""),
                    "account_name": row.get("account_name", ""),
                    "field": "contact_email",
                    "issue_type": "Duplicate",
                    "severity": "Medium",
                    "current_value": row.get("contact_email", ""),
                    "reason": "The same contact information appears on multiple records.",
                    "recommended_action": "Review the records for duplication.",
                }
            )
        elif domain_key in duplicate_domain_keys:
            findings.append(
                {
                    "record_id": row.get("record_id", ""),
                    "account_name": row.get("account_name", ""),
                    "field": "company_domain",
                    "issue_type": "Duplicate",
                    "severity": "Low",
                    "current_value": row.get("company_domain", ""),
                    "reason": "The company domain appears on multiple records.",
                    "recommended_action": "Review related records to confirm they are expected.",
                }
            )
    return findings
def write_findings(findings, output_path):
    fieldnames = [
        "record_id",
        "account_name",
        "field",
        "issue_type",
        "severity",
        "current_value",
        "reason",
        "recommended_action",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(findings)
def main():
    parser = argparse.ArgumentParser(
        description="Audit GTM account and contact data quality."
    )
    parser.add_argument(
        "input",
        help="Path to the GTM CSV file."
    )
    parser.add_argument(
        "--output",
        default="output/audit_findings.csv",
        help="Path for the findings CSV.",
    )
    parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Audit date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=180,
        help="Number of days after which a record is considered stale.",
    )
    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    try:
        as_of = datetime.strptime(args.as_of, "%Y-%m-%d").date()
    except ValueError:
        raise SystemExit("Error: --as-of must use YYYY-MM-DD format.")
    if not input_path.exists():
        raise SystemExit(f"Error: input file not found: {input_path}")
    with input_path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing_columns:
            raise SystemExit(
                "Error: missing expected columns: "
                + ", ".join(sorted(missing_columns))
            )
    findings = validate_rows(rows, as_of, args.stale_days)
    findings.extend(find_duplicates(rows))
    write_findings(findings, output_path)
    category_counts = Counter(item["issue_type"] for item in findings)
    severity_counts = Counter(item["severity"] for item in findings)
    affected_records = len(
        {item["record_id"] for item in findings if item["record_id"]}
    )
    print()
    print("GTM Data Quality Audit")
    print("-" * 24)
    print(f"Records reviewed: {len(rows)}")
    print(f"Records with issues: {affected_records}")
    print(f"Total findings: {len(findings)}")
    print()
    print("Findings by type:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")
    print()
    print("Findings by severity:")
    for severity, count in sorted(severity_counts.items()):
        print(f"  {severity}: {count}")
    print()
    print(f"Detailed findings written to: {output_path}")
if __name__ == "__main__":
    main()
