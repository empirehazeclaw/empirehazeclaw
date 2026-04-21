#!/usr/bin/env python3
"""
SRE Culture — Phase 6
=====================
Implements SRE-inspired learning culture:
- Blameless post-mortems (automated)
- SLO-based learning triggers
- Incident = learning opportunity culture
- Pre-Mortem analysis

Usage:
    python3 sre_culture.py --pre-mortem <plan>   # Pre-mortem before action
    python3 sre_culture.py --post-mortem <id>    # Auto post-mortem from failure
    python3 sre_culture.py --incident <desc>     # Log incident as learning
    python3 sre_culture.py --slo-breach <type>   # Learning from SLO breach
    python3 sre_culture.py --blameless <incident> # Blameless analysis
    python3 sre_culture.py --report              # SRE Culture Report
"""

import json
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
SRE_DIR = WORKSPACE / "memory" / "evaluations" / "sre_culture"
SRE_FILE = SRE_DIR / "sre_culture.json"

def init_dirs():
    SRE_DIR.mkdir(parents=True, exist_ok=True)
    if not SRE_FILE.exists():
        SRE_FILE.write_text(json.dumps({
            "incidents": [],
            "pre_mortems": [],
            "post_mortems": [],
            "slo_breaches": [],
            " learnings": [],
            "version": "1.0"
        }))

def load_sre():
    init_dirs()
    return json.loads(SRE_FILE.read_text())

def save_sre(data):
    SRE_FILE.write_text(json.dumps(data, indent=2))

def run_pre_mortem(plan):
    """Run pre-mortem analysis before taking an action."""
    sre = load_sre()
    
    pm_id = f"PRE-{len(sre['pre_mortems']) + 1:04d}"
    now = datetime.now(timezone.utc).isoformat()
    
    # Standard pre-mortem questions
    questions = [
        "What could go wrong?",
        "What assumptions are we making?",
        "What could fail in the next 24h?",
        "What dependencies could break?",
        "What have similar systems done wrong?"
    ]
    
    analysis = {
        "id": pm_id,
        "plan": plan,
        "timestamp": now,
        "risks": [],
        "assumptions": [],
        "preparedness": "unknown"
    }
    
    # Generate risk categories
    risk_categories = [
        "Technical failure (timeout, crash, error)",
        "Data loss or corruption",
        "Security breach or permission issue",
        "Integration failure with external systems",
        "Resource exhaustion (memory, CPU, disk)",
        "User-facing impact",
        " cascading failures"
    ]
    
    analysis["risk_categories"] = risk_categories
    
    sre["pre_mortems"].append(analysis)
    save_sre(sre)
    
    print(f"\n🔍 Pre-Mortem: {pm_id}")
    print("=" * 50)
    print(f"Plan: {plan}")
    print(f"\nRisk Categories to Consider:")
    for risk in risk_categories:
        print(f"  ⚠️  {risk}")
    print(f"\nQuestions to Answer:")
    for q in questions:
        print(f"  ❓ {q}")
    print(f"\n✅ Pre-Mortem recorded: {pm_id}")
    
    return analysis

def run_post_mortem(failure_id=None, incident_desc=None):
    """Run automated post-mortem from failure or incident."""
    sre = load_sre()
    
    pm_id = f"POST-{len(sre['post_mortems']) + 1:04d}"
    now = datetime.now(timezone.utc).isoformat()
    
    postmortem = {
        "id": pm_id,
        "failure_id": failure_id,
        "incident_desc": incident_desc,
        "timestamp": now,
        "status": "blameless_analysis_complete",
        "root_cause": "TBD",
        "contributing_factors": [],
        "impact": "TBD",
        "action_items": [],
        "lessons": [],
        "what_went_well": [],
        "what_could_improve": []
    }
    
    # Standard post-mortem template
    template = {
        "timeline": "Document when failure started, when detected, when resolved",
        "impact_assessment": "What systems/users were affected? Duration?",
        "root_cause_analysis": "Why did this happen? Use 5 Whys.",
        "contributing_factors": "What conditions made this possible?",
        "action_items": [
            "Immediate fix:",
            "Short-term (1 week):",
            "Long-term (1 month):",
            "Prevention measures:"
        ],
        "detection": "How was this detected? Was it proactive?",
        "response": "How fast was response? What worked?",
        "sre_principles": [
            "Focus on systems, not individuals",
            "Blame is not the goal",
            "Every incident is a learning opportunity",
            "Automate recovery where possible",
            "Document for future reference"
        ]
    }
    
    postmortem["template"] = template
    
    sre["post_mortems"].append(postmortem)
    save_sre(sre)
    
    print(f"\n📋 Post-Mortem: {pm_id}")
    print("=" * 50)
    print(f"Failure ID: {failure_id}")
    print(f"Incident: {incident_desc}")
    print(f"\nSRE-Inspired Analysis:")
    print(f"\n  Blameless Culture Principles:")
    for principle in template["sre_principles"]:
        print(f"    ✓ {principle}")
    print(f"\n  Action Items Template:")
    for item in template["action_items"]:
        print(f"    → {item}")
    print(f"\n✅ Post-Mortem created: {pm_id}")
    
    return postmortem

def log_incident(description, severity="medium", category="unknown"):
    """Log an incident as a learning opportunity."""
    sre = load_sre()
    
    incident_id = f"INC-{len(sre['incidents']) + 1:04d}"
    now = datetime.now(timezone.utc).isoformat()
    
    incident = {
        "id": incident_id,
        "description": description,
        "severity": severity,
        "category": category,
        "timestamp": now,
        "status": "learning_captured",
        "learnings": [],
        "systems_affected": [],
        "duration_minutes": None,
        "detection_method": "unknown",
        "resolution": "TBD"
    }
    
    # Categorize incidents
    if "timeout" in description.lower():
        incident["category"] = "performance"
        incident["learnings"].append("Timeout handling could be improved")
    elif "error" in description.lower() or "fail" in description.lower():
        incident["category"] = "reliability"
        incident["learnings"].append("Error handling needs review")
    elif "memory" in description.lower() or "cpu" in description.lower():
        incident["category"] = "resource"
        incident["learnings"].append("Resource limits need monitoring")
    elif "permission" in description.lower() or "access" in description.lower():
        incident["category"] = "security"
        incident["learnings"].append("Permission model needs audit")
    
    # Severity to priority
    severity_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    priority = severity_map.get(severity, 2)
    
    incident["learnings"].extend([
        "Document incident for future reference",
        "Add monitoring/alerting if not present",
        "Review similar patterns in other systems"
    ])
    
    sre["incidents"].append(incident)
    save_sre(sre)
    
    print(f"\n🎯 Incident Logged: {incident_id}")
    print("=" * 50)
    print(f"Description: {description}")
    print(f"Severity: {severity}")
    print(f"Category: {incident['category']}")
    print(f"\n📚 Automated Learnings:")
    for learning in incident["learnings"]:
        print(f"  → {learning}")
    print(f"\n✅ Incident saved as learning opportunity")
    
    return incident

def slo_breach_learning(task_type, actual, target):
    """Capture learning from SLO breach."""
    sre = load_sre()
    
    breach_id = f"BREACH-{len(sre['slo_breaches']) + 1:04d}"
    now = datetime.now(timezone.utc).isoformat()
    
    breach = {
        "id": breach_id,
        "task_type": task_type,
        "actual": actual,
        "target": target,
        "delta": target - actual,
        "timestamp": now,
        "status": "action_required",
        "root_cause": "TBD",
        "corrective_actions": [],
        "preventive_actions": []
    }
    
    # Generate automatic corrective actions based on SLO gap
    delta_pct = (target - actual) / max(actual, 0.01)
    
    if delta_pct > 0.2:  # >20% below target
        breach["corrective_actions"] = [
            "IMMEDIATE: Review recent changes to this task type",
            "SHORT-TERM: Increase monitoring frequency",
            "SHORT-TERM: Check dependencies for degradation",
            "LONG-TERM: Review and optimize strategy"
        ]
        breach["preventive_actions"] = [
            "Add early warning based on trending",
            "Implement automatic rollback",
            "Review capacity planning"
        ]
    else:
        breach["corrective_actions"] = [
            "Review recent changes",
            "Monitor trend",
            "Consider optimization"
        ]
        breach["preventive_actions"] = [
            "Add monitoring",
            "Document known issues"
        ]
    
    sre["slo_breaches"].append(breach)
    save_sre(sre)
    
    print(f"\n⚠️  SLO Breach Learning: {breach_id}")
    print("=" * 50)
    print(f"Task Type: {task_type}")
    print(f"Actual: {actual:.1%} | Target: {target:.1%} | Delta: {breach['delta']:.1%}")
    print(f"\n🔧 Corrective Actions:")
    for action in breach["corrective_actions"]:
        print(f"  → {action}")
    print(f"\n🛡️  Preventive Actions:")
    for action in breach["preventive_actions"]:
        print(f"  → {action}")
    print(f"\n✅ SLO breach recorded for learning")
    
    return breach

def blameless_analysis(incident_id):
    """Run blameless analysis on an incident."""
    sre = load_sre()
    
    incident = None
    for inc in sre["incidents"]:
        if inc["id"] == incident_id:
            incident = inc
            break
    
    if not incident:
        print(f"[*] Incident {incident_id} not found.")
        return None
    
    print(f"\n🔬 Blameless Analysis: {incident_id}")
    print("=" * 50)
    print(f"Description: {incident['description']}")
    
    print(f"\n📋 Blameless Questions:")
    questions = [
        "What conditions led to this incident?",
        "Was information available that could have prevented it?",
        "Were there process gaps?",
        "What system design could be improved?",
        "How can we detect this faster next time?",
        "What would we do differently if we knew then what we know now?"
    ]
    
    for q in questions:
        print(f"  ❓ {q}")
    
    print(f"\n🔍 System Focus (not individual):")
    print(f"  ✓ Was the system designed to handle this?")
    print(f"  ✓ Were there hidden dependencies?")
    print(f"  ✓ Did monitoring/alerting work?")
    print(f"  ✓ Was there a cascade effect?")
    print(f"  ✓ What can we automate to prevent recurrence?")
    
    # Update incident
    incident["blameless_analysis"] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "questions_addressed": len(questions)
    }
    save_sre(sre)
    
    return incident

def generate_report():
    """Generate SRE Culture report."""
    sre = load_sre()
    
    total_incidents = len(sre["incidents"])
    total_pre_mortems = len(sre["pre_mortems"])
    total_post_mortems = len(sre["post_mortems"])
    total_breaches = len(sre["slo_breaches"])
    
    # By category
    by_category = defaultdict(int)
    for inc in sre["incidents"]:
        by_category[inc.get("category", "unknown")] += 1
    
    # By severity
    by_severity = defaultdict(int)
    for inc in sre["incidents"]:
        by_severity[inc.get("severity", "unknown")] += 1
    
    # Recent
    recent_incidents = sorted(sre["incidents"], key=lambda x: x["timestamp"], reverse=True)[:5]
    
    print(f"""
📊 SRE Culture Report
{'=' * 50}
Generated: {datetime.now(timezone.utc).isoformat()[:19]}

Culture Metrics:
  Incidents Logged:     {total_incidents}
  Pre-Mortems Run:     {total_pre_mortems}
  Post-Mortems Done:   {total_post_mortems}
  SLO Breaches:        {total_breaches}

By Category:
""")
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    
    print(f"\nBy Severity:")
    for sev, count in sorted(by_severity.items(), key=lambda x: -x[1]):
        print(f"  {sev}: {count}")
    
    print(f"\nRecent Incidents:")
    for inc in recent_incidents:
        print(f"  [{inc['id']}] {inc['timestamp'][:10]} | {inc['description'][:50]}")
    
    # SRE Score (0-100)
    sre_score = 0
    if total_incidents > 0:
        sre_score += 20
    if total_pre_mortems >= total_incidents / 2:
        sre_score += 30
    if total_post_mortems >= total_incidents / 2:
        sre_score += 30
    if total_breaches > 0:
        slo_compliance = (total_incidents - total_breaches) / max(total_incidents, 1)
        sre_score += 20 * slo_compliance
    
    print(f"\n🎯 SRE Culture Score: {sre_score}/100")
    if sre_score >= 80:
        print("  Status: Excellent - Learning culture established")
    elif sre_score >= 50:
        print("  Status: Good - Room for improvement")
    else:
        print("  Status: Needs Work - Focus on incident learning")
    
    # Save report
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_incidents": total_incidents,
        "total_pre_mortems": total_pre_mortems,
        "total_post_mortems": total_post_mortems,
        "total_slo_breaches": total_breaches,
        "sre_score": sre_score,
        "by_category": dict(by_category),
        "by_severity": dict(by_severity)
    }
    
    report_file = WORKSPACE / "docs" / "sre_culture_report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\n📄 Report saved: {report_file}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description="SRE Culture")
    parser.add_argument("--pre-mortem", metavar="PLAN", help="Run pre-mortem on a plan")
    parser.add_argument("--post-mortem", metavar="ID", help="Run post-mortem from failure ID")
    parser.add_argument("--incident", metavar="DESC", help="Log incident as learning")
    parser.add_argument("--severity", default="medium", help="Incident severity")
    parser.add_argument("--category", default="unknown", help="Incident category")
    parser.add_argument("--slo-breach", nargs=3, metavar=("TYPE", "ACTUAL", "TARGET"), help="Learning from SLO breach")
    parser.add_argument("--blameless", metavar="INCIDENT_ID", help="Blameless analysis")
    parser.add_argument("--report", action="store_true", help="Generate SRE report")
    
    args = parser.parse_args()
    
    init_dirs()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    if args.pre_mortem:
        run_pre_mortem(args.pre_mortem)
    
    if args.post_mortem:
        run_post_mortem(failure_id=args.post_mortem)
    
    if args.incident:
        log_incident(args.incident, args.severity, args.category)
    
    if args.slo_breach:
        try:
            task_type = args.slo_breach[0]
            actual = float(args.slo_breach[1])
            target = float(args.slo_breach[2])
            slo_breach_learning(task_type, actual, target)
        except ValueError:
            print("[!] Invalid values for --slo-breach")
    
    if args.blameless:
        blameless_analysis(args.blameless)
    
    if args.report:
        generate_report()

if __name__ == "__main__":
    main()
