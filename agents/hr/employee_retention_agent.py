#!/usr/bin/env python3
"""
👥 HR Employee Retention Agent v1.0
EmpireHazeClaw — Autonomous Business AI

Identifies retention risks and suggests interventions.
Features:
- Employee risk scoring (0-100)
- Flight risk analysis
- Engagement indicators
- Retention action plans
- Survey analysis
- Exit interview processing
- Compensation benchmarking

Usage:
  python3 hr/employee_retention_agent.py --help
  python3 hr/employee_retention_agent.py add_employee --name "Max" --dept "Engineering" --tenure 3 --risk low
  python3 hr/employee_retention_agent.py list_employees
  python3 hr/employee_retention_agent.py score --employee-id 0
  python3 hr/employee_retention_agent.py at_risk
  python3 hr/employee_retention_agent.py analyze --department Engineering
  python3 hr/employee_retention_agent.py action_plan --employee-id 0
  python3 hr/employee_retention_agent.py exit_process --name "Max" --reason "Career growth"
"""

import argparse
import json
import logging
import os
import random
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ─── PATHS ────────────────────────────────────────────────────────────────────
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR  = WORKSPACE / "data"
LOGS_DIR  = WORKSPACE / "logs"
HR_DIR    = DATA_DIR / "hr"

for d in [DATA_DIR, LOGS_DIR, HR_DIR]:
    d.mkdir(parents=True, exist_ok=True)

EMPLOYEES_FILE    = HR_DIR / "employees.json"
EXIT_FILE         = HR_DIR / "exit_interviews.json"
RETENTION_FILE    = HR_DIR / "retention_log.json"
SURVEYS_FILE      = HR_DIR / "surveys.json"

# ─── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [RETENTION] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "retention_agent.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("retention")

# ─── DATA MODELS ──────────────────────────────────────────────────────────────
def load_json(path, default):
    try: return json.loads(path.read_text())
    except: return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

# ─── RISK SCORING ─────────────────────────────────────────────────────────────
RISK_WEIGHTS = {
    "tenure":          20,  # Short tenure = higher risk
    "compensation":    15,  # Below-market = higher risk
    "performance":     15,  # Declining performance
    "engagement":     20,  # Survey scores
    "tenure_change":  10,  # Just had anniversary (risk up)
    "management":     10,  # Manager changes
    "workload":        5,  # Overworked
    "remote":          5,  # Remote work satisfaction
}

RISK_LEVELS = {
    (80, 100):  ("CRITICAL",  "🔴", "Immediate intervention required"),
    (60, 79):   ("HIGH",      "🟠", "Proactive retention measures needed"),
    (40, 59):   ("MEDIUM",    "🟡", "Monitor and address concerns"),
    (20, 39):   ("LOW",       "🟢", "Stable, occasional check-in"),
    (0, 19):    ("MINIMAL",   "⚪", "Low flight risk"),
}

COMPETITIVE_BENCHMARK = {
    "Software Engineer":    75000,
    "Senior Engineer":     100000,
    "Product Manager":      85000,
    "Designer":             70000,
    "Sales":                60000,
    "Marketing":            60000,
    "HR":                   55000,
    "Finance":              65000,
    "Operations":           55000,
}

# ─── LLM ──────────────────────────────────────────────────────────────────────
def call_llm(prompt: str, system: str = "Du bist ein HR-Experte für Mitarbeiterbindung.") -> str:
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        logger.warning(f"LLM unavailable: {e}")
        return None

# ─── SCORING ──────────────────────────────────────────────────────────────────
def calculate_risk_score(emp: dict) -> Dict:
    """Calculate retention risk score 0-100."""
    score = 0
    factors = {}

    # Tenure (shorter = higher risk)
    tenure_years = emp.get("tenure_years", 0)
    if tenure_years < 1:
        factors["tenure"] = 18
    elif tenure_years < 2:
        factors["tenure"] = 14
    elif tenure_years < 3:
        factors["tenure"] = 8
    else:
        factors["tenure"] = 3
    score += factors["tenure"]

    # Compensation
    title = emp.get("title", "")
    salary = emp.get("salary", 0)
    benchmark = COMPETITIVE_BENCHMARK.get(title, 60000)
    if salary < benchmark * 0.80:
        factors["compensation"] = 15
    elif salary < benchmark * 0.90:
        factors["compensation"] = 10
    elif salary < benchmark:
        factors["compensation"] = 5
    else:
        factors["compensation"] = 0
    score += factors["compensation"]

    # Performance trend
    perf_trend = emp.get("performance_trend", "stable")
    perf_map = {"declining": 15, "stable": 7, "improving": 2}
    factors["performance"] = perf_map.get(perf_trend, 7)
    score += factors["performance"]

    # Engagement score
    engagement = emp.get("engagement_score", 80)  # 0-100
    if engagement < 40:
        factors["engagement"] = 20
    elif engagement < 60:
        factors["engagement"] = 14
    elif engagement < 75:
        factors["engagement"] = 7
    else:
        factors["engagement"] = 2
    score += factors["engagement"]

    # Recent tenure change
    if emp.get("had_anniversary_this_year"):
        factors["tenure_change"] = 8
        score += 8
    else:
        factors["tenure_change"] = 3

    # Manager changes
    manager_changes = emp.get("manager_changes_12m", 0)
    factors["management"] = min(manager_changes * 3, 10)
    score += factors["management"]

    # Workload
    workload = emp.get("workload_level", "normal")
    workload_map = {"critical": 5, "high": 4, "normal": 2, "low": 1}
    factors["workload"] = workload_map.get(workload, 2)
    score += factors["workload"]

    # Remote satisfaction
    remote = emp.get("remote_satisfaction", 70)
    if remote < 40:
        factors["remote"] = 5
    elif remote < 60:
        factors["remote"] = 3
    else:
        factors["remote"] = 0
    score += factors["remote"]

    # Determine level
    risk_label, emoji, description = "UNKNOWN", "⚪", "Unable to assess"
    for (low, high), (label, em, desc) in RISK_LEVELS.items():
        if low <= score <= high:
            risk_label, emoji, description = label, em, desc
            break

    return {
        "score": min(score, 100),
        "level": risk_label,
        "emoji": emoji,
        "description": description,
        "factors": factors,
        "total_weight": sum(RISK_WEIGHTS.values()),
    }

# ─── COMMANDS ─────────────────────────────────────────────────────────────────
def cmd_add_employee(args) -> int:
    """Add a new employee record."""
    employees = load_json(EMPLOYEES_FILE, [])
    new_id = max([e.get("id", -1) for e in employees], default=-1) + 1

    emp = {
        "id": new_id,
        "name": args.name,
        "title": args.title,
        "department": args.department,
        "tenure_years": args.tenure,
        "salary": args.salary or 0,
        "performance_trend": args.performance_trend or "stable",
        "engagement_score": args.engagement or 75,
        "workload_level": args.workload or "normal",
        "remote_satisfaction": args.remote_satisfaction or 70,
        "had_anniversary_this_year": False,
        "manager_changes_12m": 0,
        "status": "active",
        "risk_score": None,
        "risk_level": None,
        "last_review": args.last_review or "",
        "added_at": datetime.now().isoformat(),
        "tags": args.tags.split(",") if args.tags else [],
    }

    # Calculate initial risk
    risk = calculate_risk_score(emp)
    emp["risk_score"] = risk["score"]
    emp["risk_level"] = risk["level"]

    employees.append(emp)
    save_json(EMPLOYEES_FILE, employees)
    logger.info(f"Added employee: {emp['name']} (ID: {new_id}) Risk: {risk['level']}")

    print(f"✅ Employee added (ID: {new_id}): {emp['name']}")
    print(f"   Department: {emp['department']} | Title: {emp['title']}")
    print(f"   Tenure: {emp['tenure_years']}y | Salary: €{emp['salary']}")
    print(f"   Engagement: {emp['engagement_score']}% | Risk: {risk['emoji']} {risk['level']} ({risk['score']}/100)")
    return 0


def cmd_list_employees(args) -> int:
    """List all employees."""
    employees = load_json(EMPLOYEES_FILE, [])
    if not employees:
        print("No employees in system. Add one with: add_employee")
        return 0

    dept_filter = args.department
    if dept_filter:
        employees = [e for e in employees if e.get("department") == dept_filter]

    risk_filter = args.risk
    if risk_filter:
        employees = [e for e in employees if e.get("risk_level", "").lower() == risk_filter.lower()]

    print(f"\n{'ID':>3} | {'Name':<22} | {'Dept':<15} | {'Tenure':>5} | {'Eng.':>4} | {'Risk':<10} | Score")
    print("-" * 100)
    for e in sorted(employees, key=lambda x: x.get("risk_score", 0) or 0, reverse=True):
        risk = calculate_risk_score(e)
        name = e["name"][:20] + ".." if len(e["name"]) > 22 else e["name"]
        risk_str = f"{risk['emoji']} {risk['level']}"
        print(f"{e['id']:>3} | {name:<22} | {e.get('department','?'):<15} | {e.get('tenure_years',0):>5}y | {e.get('engagement_score',0):>4}% | {risk_str:<10} | {risk['score']}")

    print(f"\nTotal: {len(employees)} employee(s)")
    return 0


def cmd_score(args) -> int:
    """Calculate/refresh risk score for an employee."""
    employees = load_json(EMPLOYEES_FILE, [])
    try:
        emp = next(e for e in employees if e["id"] == args.employee_id)
    except StopIteration:
        print(f"Error: Employee ID {args.employee_id} not found")
        return 1

    risk = calculate_risk_score(emp)
    emp["risk_score"] = risk["score"]
    emp["risk_level"] = risk["level"]
    emp["last_review"] = datetime.now().isoformat()
    save_json(EMPLOYEES_FILE, employees)

    print(f"\n👤 {emp['name']} — Retention Risk Assessment")
    print(f"{'='*55}")
    print(f"   Title: {emp['title']} | Dept: {emp['department']}")
    print(f"   Tenure: {emp['tenure_years']}y | Salary: €{emp.get('salary', 0):,}")
    print(f"\n   📊 OVERALL RISK: {risk['emoji']} {risk['level']} ({risk['score']}/100)")
    print(f"   {risk['description']}")
    print(f"\n   Factor Breakdown:")
    for factor, pts in sorted(risk["factors"].items(), key=lambda x: -x[1]):
        bar = "█" * pts + "░" * (20 - pts)
        print(f"     {factor:<20}: {pts:>2} pts  [{bar}]")
    return 0


def cmd_at_risk(args) -> int:
    """Show all at-risk employees."""
    employees = load_json(EMPLOYEES_FILE, [])
    at_risk = []
    for e in employees:
        risk = calculate_risk_score(e)
        e["risk_score"] = risk["score"]
        e["risk_level"] = risk["level"]
        if risk["score"] >= (args.threshold or 60):
            at_risk.append((risk, e))

    at_risk.sort(key=lambda x: -x[0]["score"])

    if not at_risk:
        print("✅ No employees above risk threshold!")
        return 0

    print(f"\n🚨 AT-RISK EMPLOYEES (threshold: {args.threshold or 60})")
    print(f"{'='*70}")
    for risk, e in at_risk:
        print(f"  {risk['emoji']} {e['name']} | {e.get('department','?')} | Score: {risk['score']}/100")
        print(f"     Key factors: {', '.join(sorted(risk['factors'].keys(), key=lambda x: -risk['factors'][x])[:3])}")
        print()
    return 0


def cmd_analyze(args) -> int:
    """Analyze department retention health."""
    employees = load_json(EMPLOYEES_FILE, [])
    dept_emps = [e for e in employees if e.get("department") == args.department]

    if not dept_emps:
        print(f"No employees found in department: {args.department}")
        return 1

    scores = [calculate_risk_score(e) for e in dept_emps]
    avg_score = sum(s["score"] for s in scores) / len(scores) if scores else 0
    avg_engagement = sum(e.get("engagement_score", 0) for e in dept_emps) / len(dept_emps)
    avg_tenure = sum(e.get("tenure_years", 0) for e in dept_emps) / len(dept_emps)

    at_risk_count = sum(1 for s in scores if s["score"] >= 60)
    high_risk = sum(1 for s in scores if s["score"] >= 80)

    print(f"\n📊 Retention Analysis: {args.department}")
    print(f"{'='*55}")
    print(f"   Employees: {len(dept_emps)}")
    print(f"   Avg Risk Score: {avg_score:.1f}/100")
    print(f"   Avg Engagement: {avg_engagement:.1f}%")
    print(f"   Avg Tenure: {avg_tenure:.1f} years")
    print(f"   At-Risk (≥60): {at_risk_count} ({at_risk_count/len(dept_emps)*100:.0f}%)")
    print(f"   Critical (≥80): {high_risk}")

    # Risk distribution
    dist = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "MINIMAL": 0}
    for s in scores:
        dist[s["level"]] = dist.get(s["level"], 0) + 1
    print(f"\n   Risk Distribution:")
    for level, count in dist.items():
        if count:
            bar = "█" * count
            print(f"     {level:<10}: {bar} ({count})")

    # Suggestions via LLM
    prompt = f"""Analysiere folgende HR-Daten für die Abteilung '{args.department}':
- Mitarbeiter: {len(dept_emps)}
- Durchschnittliches Risiko: {avg_score:.1f}/100
- Durchschnittliches Engagement: {avg_engagement:.1f}%
- Durchschnittliche Betriebszugehörigkeit: {avg_tenure:.1f} Jahre
- Kritische Risiken: {high_risk}

Gib konkrete, umsetzbare Handlungsempfehlungen in 3 Kategorien:
1. Sofortmaßnahmen (diese Woche)
2. Mittelfristig (nächste 30 Tage)
3. Strategisch (nächste 3 Monate)

Sei spezifisch und realistisch für ein kleines bis mittelständisches Unternehmen."""

    suggestion = call_llm(prompt)
    if suggestion:
        print(f"\n💡 Recommendations:\n{suggestion}")
    return 0


def cmd_action_plan(args) -> int:
    """Generate retention action plan for specific employee."""
    employees = load_json(EMPLOYEES_FILE, [])
    try:
        emp = next(e for e in employees if e["id"] == args.employee_id)
    except StopIteration:
        print(f"Error: Employee ID {args.employee_id} not found")
        return 1

    risk = calculate_risk_score(emp)
    factors_sorted = sorted(risk["factors"].items(), key=lambda x: -x[1])

    prompt = f"""Erstelle einen detaillierten Retention-Aktionsplan für:

Mitarbeiter: {emp['name']}
Position: {emp['title']} in {emp['department']}
Betriebszugehörigkeit: {emp['tenure_years']} Jahre
Aktuelles Risiko: {risk['level']} ({risk['score']}/100)
Engagement: {emp.get('engagement_score', 0)}%
Gehalt: €{emp.get('salary', 0)}

Top Risikofaktoren:
{chr(10).join(f'- {k}: {v} pts' for k, v in factors_sorted[:4])}

Gib aus:
1. Sofortmaßnahmen (1-2 Tage)
2. Kurzfristige Gespräche/Initiativen (1 Woche)
3. Konkrete Angebote (Gehalt, Bonus, Beförderung, Training)
4. Nachverfolgungstermin
5. Erfolgsmetriken

Sei pragmatisch und spezifisch."""

    plan = call_llm(prompt)
    print(f"\n📋 Retention Action Plan: {emp['name']}")
    print(f"{'='*55}")
    print(f"Risk: {risk['emoji']} {risk['level']} ({risk['score']}/100)")
    print(f"Top risk factors: {', '.join(k for k, v in factors_sorted[:3])}")
    print(f"\n{plan or 'Action plan generation failed.'}")

    # Save plan
    if plan:
        plan_file = HR_DIR / f"action_plan_{emp['id']}_{datetime.now().strftime('%Y%m%d')}.md"
        plan_file.write_text(f"# Retention Action Plan: {emp['name']}\n\n**Employee ID:** {emp['id']}\n**Date:** {datetime.now().isoformat()}\n**Risk:** {risk['level']} ({risk['score']}/100)\n\n{plan}", encoding="utf-8")
        print(f"\n✅ Plan saved: {plan_file}")
    return 0


def cmd_exit_process(args) -> int:
    """Process exit interview data."""
    exits = load_json(EXIT_FILE, [])
    new_id = max([e.get("id", -1) for e in exits], default=-1) + 1

    # LLM analysis of exit reason
    prompt = f"""Analysiere den Austrittsgrund dieses Mitarbeiters und gib:
1. Kategorie (z.B. Gehalt, Karriere, Kultur, Management, Work-Life)
2. Analyse der Kernursache
3. Retentionslesson für die Zukunft
4. Empfehlung für Nachfolge

Mitarbeiter: {args.name}
Austrittsgrund: {args.reason}
Abteilung: {args.department or 'Nicht angegeben'}
Betriebszugehörigkeit: {args.tenure or 'Nicht angegeben'}

Antworte auf Deutsch, strukturiert:"""

    analysis = call_llm(prompt) if args.reason else "No reason provided"

    record = {
        "id": new_id,
        "name": args.name,
        "department": args.department or "",
        "tenure": args.tenure or "",
        "reason": args.reason,
        "analysis": analysis,
        "processed_at": datetime.now().isoformat(),
    }

    exits.append(record)
    save_json(EXIT_FILE, exits)
    logger.info(f"Exit processed: {args.name}")

    print(f"\n✅ Exit interview recorded (ID: {new_id})")
    print(f"\n📋 Analysis:\n{analysis}")
    return 0


def cmd_survey(args) -> int:
    """Analyze engagement survey results."""
    employees = load_json(EMPLOYEES_FILE, [])
    survey_file = HR_DIR / f"survey_{datetime.now().strftime('%Y%m%d')}.md"

    if not employees:
        print("No employees to survey.")
        return 1

    prompt = f"""Erstelle einen umfassenden Engagement-Survey für Mitarbeiter.

Anzahl Mitarbeiter: {len(employees)}
Abteilungen: {', '.join(set(e.get('department','') for e in employees))}

Survey soll folgende Bereiche abdecken:
1. Arbeitszufriedenheit (Gehalt, Benefits, Work-Life-Balance)
2. Management & Führung
3. Wachstum & Karriere
4. Team-Kultur
5. Sinn & Purpose
6. Tools & Resources

Format: Google Forms / Typeform kompatibel.
40-50 Fragen, Mix aus Skala (1-5) und offenen Fragen.
Rubrik: Vertraulich — Ergebnisse werden anonym ausgewertet."""

    survey = call_llm(prompt)
    if survey:
        survey_file.write_text(f"# Engagement Survey\n\n**Erstellt:** {datetime.now().isoformat()}\n\n{survey}", encoding="utf-8")
        print(f"✅ Survey saved: {survey_file}")
    else:
        print("Failed to generate survey via LLM.")
    return 0

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="hr/employee_retention_agent.py",
        description="👥 HR Employee Retention Agent — Flight risk analysis & retention planning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 hr/employee_retention_agent.py add_employee --name "Max Mustermann" --title "Software Engineer" --department "Engineering" --tenure 2 --salary 72000 --engagement 65
  python3 hr/employee_retention_agent.py list_employees
  python3 hr/employee_retention_agent.py list_employees --department Engineering --risk high
  python3 hr/employee_retention_agent.py score --employee-id 0
  python3 hr/employee_retention_agent.py at_risk
  python3 hr/employee_retention_agent.py at_risk --threshold 50
  python3 hr/employee_retention_agent.py analyze --department Engineering
  python3 hr/employee_retention_agent.py action_plan --employee-id 0
  python3 hr/employee_retention_agent.py exit_process --name "Max" --reason "Zu wenig Karrieremöglichkeiten" --tenure 3
  python3 hr/employee_retention_agent.py survey
        """,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add_employee", help="Add employee record")
    p.add_argument("--name", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--department", required=True)
    p.add_argument("--tenure", type=float, default=1.0)
    p.add_argument("--salary", type=float, default=0)
    p.add_argument("--engagement", type=int, default=75)
    p.add_argument("--performance-trend", default="stable", choices=["declining", "stable", "improving"])
    p.add_argument("--workload", default="normal", choices=["critical", "high", "normal", "low"])
    p.add_argument("--remote-satisfaction", type=int, default=70)
    p.add_argument("--last-review", default="")
    p.add_argument("--tags", default="")

    p = sub.add_parser("list_employees", help="List employees")
    p.add_argument("--department", default="")
    p.add_argument("--risk", default="", help="Filter by risk level (critical/high/medium/low)")

    p = sub.add_parser("score", help="Calculate retention risk score")
    p.add_argument("--employee-id", required=True, type=int)

    p = sub.add_parser("at_risk", help="Show at-risk employees")
    p.add_argument("--threshold", type=int, default=60)

    p = sub.add_parser("analyze", help="Analyze department retention")
    p.add_argument("--department", required=True)

    p = sub.add_parser("action_plan", help="Generate retention action plan")
    p.add_argument("--employee-id", required=True, type=int)

    p = sub.add_parser("exit_process", help="Process exit interview")
    p.add_argument("--name", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--department", default="")
    p.add_argument("--tenure", default="")

    p = sub.add_parser("survey", help="Generate engagement survey")

    args = parser.parse_args()
    commands = {
        "add_employee": cmd_add_employee,
        "list_employees": cmd_list_employees,
        "score": cmd_score,
        "at_risk": cmd_at_risk,
        "analyze": cmd_analyze,
        "action_plan": cmd_action_plan,
        "exit_process": cmd_exit_process,
        "survey": cmd_survey,
    }
    fn = commands.get(args.cmd)
    if fn:
        return fn(args)
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
