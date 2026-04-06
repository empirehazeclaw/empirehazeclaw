#!/usr/bin/env python3
"""
GDPR Auditor Agent
EmpireHazeClaw Compliance Suite

Audits data processing activities, checks for GDPR compliance gaps.
Integrität: honest assessment, Eigenverantwortung: fix what breaks.
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "compliance"
LOG_DIR = BASE_DIR / "logs"
REGISTERS_FILE = DATA_DIR / "gdpr_register.json"
AUDITS_FILE = DATA_DIR / "gdpr_audits.json"
ISSUES_FILE = DATA_DIR / "gdpr_issues.json"

LOG_FILE = LOG_DIR / "gdpr_auditor.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("GDPRAuditor")

GDPR_ARTICLES = {
    "5": "Principles of processing",
    "6": "Lawfulness of processing",
    "7": "Conditions for consent",
    "12": "Transparent information",
    "13": "Information for data collection",
    "14": "Information for third-party data",
    "15": "Right of access",
    "16": "Right to rectification",
    "17": "Right to erasure",
    "18": "Restriction of processing",
    "20": "Right to data portability",
    "21": "Right to object",
    "25": "Data protection by design",
    "28": "Processor agreements",
    "30": "Records of processing",
    "32": "Security of processing",
    "33": "Breach notification (72h)",
    "35": "Data Protection Impact Assessment",
}


def load_json(path: Path):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to load %s: %s", path, e)
    return {} if "register" in str(path) else []


def save_json(path: Path, data) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error("Failed to save %s: %s", path, e)
        return False


def load_register() -> dict:
    data = load_json(REGISTERS_FILE)
    return data if isinstance(data, dict) else {}


def save_register(data: dict) -> bool:
    return save_json(REGISTERS_FILE, data)


def load_audits() -> list:
    data = load_json(AUDITS_FILE)
    return data if isinstance(data, list) else []


def save_audits(data: list) -> bool:
    return save_json(AUDITS_FILE, data)


def load_issues() -> list:
    data = load_json(ISSUES_FILE)
    return data if isinstance(data, list) else []


def save_issues(data: list) -> bool:
    return save_json(ISSUES_FILE, data)


# ─── Core Logic ────────────────────────────────────────────────────────────────
def add_processing_activity(
    name: str,
    data_types: list[str],
    purpose: str,
    legal_basis: str,
    recipients: list[str],
    retention: str,
    country: str = "DE",
    notes: str = "",
) -> dict:
    """Register a data processing activity."""
    activity = {
        "id": str(uuid.uuid4()),
        "name": name,
        "data_types": data_types,
        "purpose": purpose,
        "legal_basis": legal_basis,
        "recipients": recipients,
        "retention": retention,
        "country": country,
        "notes": notes,
        "created_at": datetime.utcnow().isoformat(),
        "last_reviewed": datetime.utcnow().isoformat(),
    }
    register = load_register()
    register[activity["id"]] = activity
    save_register(register)
    logger.info("Processing activity added: %s", name)
    return activity


def update_activity(activity_id: str, **kwargs) -> dict:
    register = load_register()
    if activity_id not in register:
        raise ValueError(f"Activity not found: {activity_id}")
    register[activity_id].update(kwargs)
    register[activity_id]["last_reviewed"] = datetime.utcnow().isoformat()
    save_register(register)
    return register[activity_id]


def run_audit(activity_ids: Optional[list] = None) -> dict:
    """Run a GDPR compliance audit on registered activities."""
    register = load_register()
    activities = register.values() if not activity_ids else [register[a] for a in activity_ids if a in register]

    issues_found = []
    articles_checked = 0

    for act in activities:
        act_issues = []

        # Art. 30 — Records of processing
        if not act.get("data_types"):
            act_issues.append({"article": "30", "severity": "high", "message": "No data types specified"})
        if not act.get("legal_basis"):
            act_issues.append({"article": "12", "severity": "high", "message": "No legal basis defined"})
        if not act.get("retention"):
            act_issues.append({"article": "5", "severity": "medium", "message": "No retention period defined"})

        # Art. 32 — Security
        if not act.get("security_measures"):
            act_issues.append({"article": "32", "severity": "high", "message": "No security measures documented"})

        # Art. 33 — Breach notification (if processors involved)
        if act.get("recipients"):
            if not register.get(act["id"], {}).get("breach_contact"):
                act_issues.append({"article": "33", "severity": "medium", "message": "No breach contact for processors"})

        # Art. 35 — DPIA
        if any(dt in ["health", "biometric", "genetic", "location"] for dt in act.get("data_types", [])):
            act_issues.append({"article": "35", "severity": "high", "message": "DPIA required for special category data"})

        if act_issues:
            for issue in act_issues:
                issue["activity_id"] = act["id"]
                issue["activity_name"] = act["name"]
                issue["detected_at"] = datetime.utcnow().isoformat()
            issues_found.extend(act_issues)

    # Save audit
    audit = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "activities_checked": len(list(activities)),
        "issues_found": len(issues_found),
        "issues": issues_found,
    }
    audits = load_audits()
    audits.append(audit)
    save_audits(audits)
    save_issues(issues_found)

    logger.info("Audit completed: %d activities, %d issues", audit["activities_checked"], audit["issues_found"])
    return audit


def get_latest_audit() -> dict:
    audits = load_audits()
    if not audits:
        return {}
    audits.sort(key=lambda x: x["timestamp"], reverse=True)
    return audits[0]


def add_issue(
    activity_id: str,
    article: str,
    severity: str,
    message: str,
    remediation: str = "",
) -> dict:
    issue = {
        "id": str(uuid.uuid4()),
        "activity_id": activity_id,
        "article": article,
        "severity": severity,
        "message": message,
        "remediation": remediation,
        "status": "open",
        "created_at": datetime.utcnow().isoformat(),
        "resolved_at": None,
    }
    issues = load_issues()
    issues.append(issue)
    save_issues(issues)
    logger.info("Issue added: Art.%s (%s) — %s", article, severity, message)
    return issue


def resolve_issue(issue_id: str) -> dict:
    issues = load_issues()
    for issue in issues:
        if issue["id"] == issue_id:
            issue["status"] = "resolved"
            issue["resolved_at"] = datetime.utcnow().isoformat()
            save_issues(issues)
            logger.info("Issue resolved: %s", issue_id)
            return issue
    raise ValueError(f"Issue not found: {issue_id}")


def generate_report(audit_id: Optional[str] = None) -> str:
    """Generate a plain-text GDPR compliance report."""
    if audit_id:
        audits = load_audits()
        audit = next((a for a in audits if a["id"] == audit_id), None)
    else:
        audit = get_latest_audit()

    if not audit:
        return "No audits found. Run 'gdpr-auditor audit' first."

    register = load_register()
    issues = audit.get("issues", [])

    high = [i for i in issues if i["severity"] == "high"]
    medium = [i for i in issues if i["severity"] == "medium"]
    low = [i for i in issues if i["severity"] == "low"]

    lines = [
        "=" * 65,
        "  GDPR COMPLIANCE AUDIT REPORT",
        "=" * 65,
        f"  Audit ID    : {audit['id']}",
        f"  Timestamp   : {audit['timestamp']}",
        f"  Activities  : {audit['activities_checked']}",
        f"  Issues      : {audit['issues_found']}  (🔴{len(high)} high | 🟡{len(medium)} medium | 🟢{len(low)} low)",
        "",
        "  REGISTERED ACTIVITIES",
        "  " + "-" * 60,
    ]

    for act in register.values():
        lines.append(f"  [{act.get('country','?')}] {act['name']}")
        lines.append(f"    Purpose    : {act.get('purpose','?')}")
        lines.append(f"    Legal Basis: {act.get('legal_basis','?')}")
        lines.append(f"    Data Types : {', '.join(act.get('data_types',[])) or '?'}")
        lines.append(f"    Retention  : {act.get('retention','?')}")
        lines.append(f"    Recipients : {', '.join(act.get('recipients',[])) or 'none'}")
        lines.append("")

    if issues:
        lines.extend(["  GDPR GAPS DETECTED", "  " + "-" * 60])
        for issue in issues:
            art_name = GDPR_ARTICLES.get(issue["article"], "Unknown")
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue["severity"], "⚪")
            lines.append(f"  {icon} Art.{issue['article']} — {art_name}")
            lines.append(f"     Activity : {issue.get('activity_name','?')}")
            lines.append(f"     Issue    : {issue['message']}")
            lines.append("")

    lines.extend(
        [
            "  GDPR ARTICLES REFERENCE",
            "  " + "-" * 60,
        ]
    )
    for art_num, art_name in sorted(GDPR_ARTICLES.items()):
        lines.append(f"  Art.{art_num:<5} {art_name}")

    lines.append("=" * 65)
    return "\n".join(lines)


# ─── CLI ───────────────────────────────────────────────────────────────────────
def cmd_add_activity(args):
    data_types = args.data_type or []
    recipients = args.recipient or []
    act = add_processing_activity(
        name=args.name,
        data_types=data_types,
        purpose=args.purpose,
        legal_basis=args.legal_basis,
        recipients=recipients,
        retention=args.retention,
        country=args.country or "DE",
        notes=args.notes or "",
    )
    print(f"✅ Activity registered: {act['id']}")
    print(f"   {act['name']}")
    print(f"   Legal basis: {act['legal_basis']}")


def cmd_list(args):
    register = load_register()
    if not register:
        print("No processing activities registered. Add one with: gdpr-auditor add-activity ...")
        return
    print(f"\n{'#':<4} {'Name':<35} {'Legal Basis':<25} {'Country'}")
    print("-" * 90)
    for i, act in enumerate(register.values(), 1):
        print(f"{i:<4} {act['name']:<35} {act.get('legal_basis','?'):<25} {act.get('country','?')}")
    print(f"\nTotal: {len(register)} processing activity(activities)")


def cmd_audit(args):
    audit = run_audit(activity_ids=args.activity_id)
    issues = audit.get("issues", [])
    print(f"\n📊 Audit Complete")
    print("=" * 50)
    print(f"  Activities checked : {audit['activities_checked']}")
    print(f"  Total issues found : {len(issues)}")
    if issues:
        by_sev = {"high": 0, "medium": 0, "low": 0}
        for i in issues:
            by_sev[i["severity"]] = by_sev.get(i["severity"], 0) + 1
        for sev, label in [("high", "🔴 High"), ("medium", "🟡 Medium"), ("low", "🟢 Low")]:
            if by_sev.get(sev):
                print(f"    {label}: {by_sev[sev]}")
    print(f"\nRun 'gdpr-auditor report' to see full details.")
    print(f"Audit ID: {audit['id']}")


def cmd_report(args):
    report = generate_report(audit_id=args.audit_id)
    print(report)


def cmd_add_issue(args):
    issue = add_issue(
        activity_id=args.activity_id,
        article=args.article,
        severity=args.severity,
        message=args.message,
        remediation=args.remediation or "",
    )
    print(f"✅ Issue added: {issue['id']}")
    print(f"   Art.{issue['article']} | {issue['severity']} | {issue['message']}")


def cmd_list_issues(args):
    issues = load_issues()
    if args.status:
        issues = [i for i in issues if i["status"] == args.status]
    if not issues:
        print("No issues found.")
        return
    print(f"\n{'#':<4} {'Severity':<8} {'Article':<8} {'Activity':<25} {'Message':<30}")
    print("-" * 90)
    for i, issue in enumerate(issues, 1):
        print(f"{i:<4} {issue['severity']:<8} Art.{issue['article']:<7} {issue.get('activity_name',''):<25} {issue['message'][:30]}")
    print(f"\nTotal: {len(issues)} issue(s)")


def cmd_resolve(args):
    issue = resolve_issue(args.issue_id)
    print(f"✅ Issue resolved: {issue['id']}")
    print(f"   {issue['message']}")


def cmd_articles(args):
    print("\nKey GDPR Articles:")
    for art_num, art_name in sorted(GDPR_ARTICLES.items()):
        print(f"  Art.{art_num:<5} {art_name}")


def main():
    parser = argparse.ArgumentParser(
        prog="gdpr-auditor",
        description="EmpireHazeClaw GDPR Auditor — audit data processing for GDPR compliance.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add-activity", help="Register a data processing activity")
    p_add.add_argument("--name", required=True, help="Activity name")
    p_add.add_argument("--purpose", required=True, help="Processing purpose")
    p_add.add_argument("--legal-basis", required=True, help="Legal basis (e.g. consent, contract, legitimate interest)")
    p_add.add_argument("--data-type", action="append", help="Data type (can repeat)")
    p_add.add_argument("--recipient", action="append", help="Data recipient (can repeat)")
    p_add.add_argument("--retention", required=True, help="Retention period (e.g. '2 years')")
    p_add.add_argument("--country", default="DE", help="Country code (default: DE)")
    p_add.add_argument("--notes", help="Additional notes")
    p_add.set_defaults(fn=cmd_add_activity)

    p_list = sub.add_parser("list", help="List registered activities")
    p_list.set_defaults(fn=cmd_list)

    p_audit = sub.add_parser("audit", help="Run a GDPR compliance audit")
    p_audit.add_argument("--activity-id", action="append", help="Specific activity IDs to audit (optional)")
    p_audit.set_defaults(fn=cmd_audit)

    p_report = sub.add_parser("report", help="Generate a compliance report")
    p_report.add_argument("--audit-id", help="Specific audit ID (default: latest)")
    p_report.set_defaults(fn=cmd_report)

    p_issue = sub.add_parser("add-issue", help="Manually add an issue")
    p_issue.add_argument("--activity-id", required=True)
    p_issue.add_argument("--article", required=True, help="GDPR Article number")
    p_issue.add_argument("--severity", required=True, choices=["high", "medium", "low"])
    p_issue.add_argument("--message", required=True, help="Issue description")
    p_issue.add_argument("--remediation", help="How to fix this")
    p_issue.set_defaults(fn=cmd_add_issue)

    p_issues = sub.add_parser("issues", help="List all issues")
    p_issues.add_argument("--status", choices=["open", "resolved"], help="Filter by status")
    p_issues.set_defaults(fn=cmd_list_issues)

    p_resolve = sub.add_parser("resolve", help="Mark an issue as resolved")
    p_resolve.add_argument("issue_id", help="Issue ID")
    p_resolve.set_defaults(fn=cmd_resolve)

    p_arts = sub.add_parser("articles", help="List key GDPR articles")
    p_arts.set_defaults(fn=cmd_articles)

    args = parser.parse_args()
    try:
        args.fn(args)
    except Exception as e:
        logger.error("%s", e)
        sys.stderr.write(f"❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
