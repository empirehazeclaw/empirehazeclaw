#!/usr/bin/env python3
"""
UX Researcher Agent
EmpireHazeClaw Creative Suite

Conducts UX research, generates personas, analyzes friction points.
Eigenverantwortung: honest findings, no sugar-coating bad news.
"""

import argparse
import json
import logging
import os
import random
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "creative"
LOG_DIR = BASE_DIR / "logs"
RESEARCH_FILE = DATA_DIR / "ux_research.json"
PERSONAS_FILE = DATA_DIR / "ux_personas.json"

LOG_FILE = LOG_DIR / "ux_researcher.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("UXResearcher")


def load_json(path: Path):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to load %s: %s", path, e)
    return []


def save_json(path: Path, data) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error("Failed to save %s: %s", path, e)
        return False


def load_research() -> list:
    data = load_json(RESEARCH_FILE)
    return data if isinstance(data, list) else []


def save_research(data: list) -> bool:
    return save_json(RESEARCH_FILE, data)


def load_personas() -> list:
    data = load_json(PERSONAS_FILE)
    return data if isinstance(data, list) else []


def save_personas(data: list) -> bool:
    return save_json(PERSONAS_FILE, data)


# ─── Heuristics Engine ────────────────────────────────────────────────────────
HEURISTICS = [
    {
        "id": "h01",
        "name": "Visibility of System Status",
        "description": "System should always keep users informed about what's going on",
        "severity": "medium",
        "question": "Does the system provide timely feedback for every action?",
    },
    {
        "id": "h02",
        "name": "Match Between System and Real World",
        "description": "System should speak the user's language, not system jargon",
        "severity": "low",
        "question": "Are all labels and terms familiar to the target users?",
    },
    {
        "id": "h03",
        "name": "User Control and Freedom",
        "description": "Users often choose system functions by mistake, need emergency exit",
        "severity": "high",
        "question": "Is there an easy way to undo, cancel, or go back?",
    },
    {
        "id": "h04",
        "name": "Consistency and Standards",
        "description": "Platform conventions and consistency between and within platforms",
        "severity": "medium",
        "question": "Is the interface consistent across all pages and flows?",
    },
    {
        "id": "h05",
        "name": "Error Prevention",
        "description": "Better to prevent errors than provide good error messages",
        "severity": "high",
        "question": "Can users easily make destructive mistakes?",
    },
    {
        "id": "h06",
        "name": "Recognition Rather Than Recall",
        "description": "Minimize user's memory load by making objects and actions visible",
        "severity": "low",
        "question": "Does the UI require users to remember information from elsewhere?",
    },
    {
        "id": "h07",
        "name": "Flexibility and Efficiency of Use",
        "description": "Shortcuts for experts, customization for frequent actions",
        "severity": "low",
        "question": "Are there shortcuts for power users while remaining usable for beginners?",
    },
    {
        "id": "h08",
        "name": "Aesthetic and Minimalist Design",
        "description": "Dialogues should not contain irrelevant or rarely needed information",
        "severity": "low",
        "question": "Is every UI element purposeful? Is there unnecessary clutter?",
    },
    {
        "id": "h09",
        "name": "Help Users Recognize Errors",
        "description": "Error messages should be in plain language, precise, constructive",
        "severity": "high",
        "question": "Do error messages explain the problem and suggest a solution?",
    },
    {
        "id": "h10",
        "name": "Help and Documentation",
        "description": "Even if not needed, best if system can be used without docs",
        "severity": "low",
        "question": "Is help easy to find, searchable, and actually helpful?",
    },
]


def generate_persona(
    name: str,
    age_range: str = "25-35",
    profession: str = "",
    tech_savvy: str = "medium",
    goals: list[str] = None,
    pain_points: list[str] = None,
    user_type: str = "primary",
) -> dict:
    """Generate a detailed user persona."""
    logger.info("Generating persona: %s", name)

    if not goals:
        goals = ["Complete tasks quickly", "Feel confident in decisions", "Avoid wasting time"]

    if not pain_points:
        pain_points = ["Complex interfaces", "Slow loading", "Unclear pricing"]

    persona = {
        "id": str(uuid.uuid4()),
        "name": name,
        "age_range": age_range,
        "profession": profession or random.choice(["Product Manager", "Marketer", "Developer", "Founder", "Designer"]),
        "tech_savvy": tech_savvy,
        "user_type": user_type,
        "goals": goals,
        "pain_points": pain_points,
        "behavioral_traits": {
            "primary_device": random.choice(["Desktop", "Mobile", "Tablet", "Desktop + Mobile"]),
            "time_per_session": random.choice(["<5 min", "5-15 min", "15-30 min", "30+ min"]),
            "frequency": random.choice(["Daily", "Weekly", "Monthly", "Occasionally"]),
            "research_depth": random.choice(["Quick scan", "Moderate", "Deep dive"]),
        },
        "motivation": random.choice([
            "Save time and money",
            "Get better results than the competition",
            "Reduce stress and complexity",
            "Build something meaningful",
            "Impress stakeholders",
        ]),
        "frustrations": random.choice([
            "Too many clicks to complete simple tasks",
            "Unclear what happens next",
            "Having to re-enter information",
            "Being locked into a specific workflow",
            "Hidden costs or surprises",
        ]),
        "preferred_support": random.choice(["Help docs", "Video tutorials", "Live chat", "Community forum", "Email"]),
        "quote": random.choice([
            "I just want it to work — and fast.",
            "If I have to read a manual, something is wrong.",
            "The cheaper option is usually fine for me.",
            "I'll pay more for something that saves me time.",
            "I trust what I can see and understand easily.",
            "I research for hours before spending $50.",
        ]),
        "journey_summary": generate_journey_summary(goals, pain_points),
        "created_at": datetime.utcnow().isoformat(),
    }

    personas = load_personas()
    personas.append(persona)
    save_personas(personas)
    return persona


def generate_journey_summary(goals: list[str], pain_points: list[str]) -> dict:
    """Generate a simplified user journey summary."""
    return {
        "awareness": f"Learns about product through {random.choice(['search', 'social media', 'friend recommendation', 'ads', 'blog post'])}",
        "consideration": f"Compares alternatives, reads reviews, checks {random.choice(['pricing', 'features', 'ease of use'])}",
        "decision": f"Signs up / purchases if {random.choice(['trial is easy', 'pricing is clear', 'onboarding is smooth'])}",
        "retention": f"Continues using if {random.choice(['value is clear', 'support is responsive', 'updates keep coming'])}",
        "advocacy": f"Recommends if {random.choice(['saved significant time', 'team is happy', 'results exceeded expectations'])}",
    }


def analyze_friction_points(
    flow_description: str,
    num_critical: int = 3,
) -> dict:
    """Analyze a user flow for friction points."""
    logger.info("Analyzing friction points for flow")

    # Heuristic mapping based on keywords
    keyword_triggers = {
        "h01": ["loading", "progress", "feedback", "status", "wait", "processing"],
        "h03": ["back", "undo", "cancel", "exit", "escape", "return"],
        "h04": ["different", "inconsistent", "layout", "style", "varies"],
        "h05": ["confirm", "delete", "warn", "caution", "danger", "irreversible"],
        "h06": ["remember", "recall", "previous", "prior", "history"],
        "h07": ["shortcut", "keyboard", "quick", "efficient", "advanced", "power"],
        "h08": ["clutter", "busy", "messy", "too much", "overwhelming", "distracting"],
        "h09": ["error", "wrong", "failed", "mistake", "problem", "issue"],
        "h10": ["help", "support", "guide", "tutorial", "docs", "explain"],
    }

    detected = {}
    flow_lower = flow_description.lower()

    for h in HEURISTICS:
        hid = h["id"]
        keywords = keyword_triggers.get(hid, [])
        matches = [kw for kw in keywords if kw in flow_lower]
        if matches:
            detected[hid] = {"matches": matches, "heuristic": h}

    # Build friction analysis
    friction_points = []
    for hid, data in detected.items():
        h = data["heuristic"]
        fp = {
            "id": str(uuid.uuid4()),
            "heuristic_id": hid,
            "heuristic_name": h["name"],
            "severity": h["severity"],
            "description": h["description"],
            "question": h["question"],
            "trigger_keywords": data["matches"],
            "recommendation": generate_fix_recommendation(hid, data["matches"]),
        }
        friction_points.append(fp)

    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    friction_points.sort(key=lambda x: severity_order.get(x["severity"], 3))

    analysis = {
        "id": str(uuid.uuid4()),
        "flow_description": flow_description,
        "heuristics_triggered": len(friction_points),
        "high_severity": len([f for f in friction_points if f["severity"] == "high"]),
        "medium_severity": len([f for f in friction_points if f["severity"] == "medium"]),
        "low_severity": len([f for f in friction_points if f["severity"] == "low"]),
        "friction_points": friction_points,
        "summary_score": max(0, 100 - len(friction_points) * 8 - len([f for f in friction_points if f["severity"] == "high"]) * 15),
        "created_at": datetime.utcnow().isoformat(),
    }

    research = load_research()
    research.append(analysis)
    save_research(research)
    return analysis


def generate_fix_recommendation(heuristic_id: str, keywords: list[str]) -> str:
    fixes = {
        "h01": "Add visible progress indicators and timely status updates for every async operation.",
        "h03": "Ensure every action has an undo/cancel path. Use breadcrumb navigation and confirmation dialogs sparingly.",
        "h04": "Establish and document UI patterns. Use a design system. Audit for consistency quarterly.",
        "h05": "Implement confirmation dialogs for destructive actions. Add preview modes before irreversible changes.",
        "h06": "Surface context within the UI rather than requiring recall. Use inline labels, visible history, and persistent state.",
        "h07": "Add keyboard shortcuts, recent items, saved preferences, and progressive disclosure for advanced features.",
        "h08": "Conduct a content audit. Remove every element that doesn't serve the user's current goal.",
        "h09": "Write error messages that: (1) describe the problem, (2) explain why, (3) suggest a specific fix.",
        "h10": "Make help contextual (linked to the feature being used), searchable, and updated with each major release.",
    }
    return fixes.get(heuristic_id, "Review this heuristic in the Nielsen Norman guidelines.")


def conduct_heuristic_audit(product_type: str = "web_app") -> dict:
    """Conduct a complete heuristic evaluation for a product type."""
    logger.info("Conducting heuristic audit for: %s", product_type)

    product_types = {
        "web_app": {
            "typical_flows": ["Onboarding", "Main dashboard", "Settings", "Checkout/payment", "Search and filter", "Account deletion"],
            "apply_heuristics": [h for h in HEURISTICS],
        },
        "mobile_app": {
            "typical_flows": ["First launch", "Sign up / login", "Core feature", "Settings", "Notifications", "Deep link handling"],
            "apply_heuristics": [h for h in HEURISTICS if h["id"] not in ["h07"]] + [HEURISTICS[4]],  # mobile: h07 less relevant
        },
        "ecommerce": {
            "typical_flows": ["Product browsing", "Search", "Add to cart", "Checkout", "Account creation", "Order tracking", "Returns"],
            "apply_heuristics": HEURISTICS + [HEURISTICS[4]],  # extra error prevention focus
        },
        "api": {
            "typical_flows": ["Authentication", "Request building", "Error handling", "Rate limiting", "Documentation lookup"],
            "apply_heuristics": [h for h in HEURISTICS if h["id"] in ["h04", "h06", "h07", "h09", "h10"]],
        },
    }

    config = product_types.get(product_type, product_types["web_app"])

    audit = {
        "id": str(uuid.uuid4()),
        "product_type": product_type,
        "typical_flows": config["typical_flows"],
        "heuristics": config["apply_heuristics"],
        "checklist": generate_audit_checklist(config["apply_heuristics"]),
        "created_at": datetime.utcnow().isoformat(),
    }

    research = load_research()
    research.append(audit)
    save_research(research)
    return audit


def generate_audit_checklist(heuristics: list) -> list[dict]:
    checklist = []
    for h in heuristics:
        checklist.append({
            "heuristic_id": h["id"],
            "name": h["name"],
            "description": h["description"],
            "check": h["question"],
            "passed": None,
            "notes": "",
            "severity": h["severity"],
        })
    return checklist


def format_analysis_report(analysis: dict) -> str:
    fps = analysis["friction_points"]
    high = [f for f in fps if f["severity"] == "high"]
    medium = [f for f in fps if f["severity"] == "medium"]
    low = [f for f in fps if f["severity"] == "low"]

    lines = [
        "=" * 65,
        "  UX FRICTION ANALYSIS REPORT",
        "=" * 65,
        f"  ID        : {analysis['id']}",
        f"  Timestamp : {analysis['created_at']}",
        f"  Score     : {analysis['summary_score']}/100",
        f"  Heuristics triggered: {analysis['heuristics_triggered']}",
        "",
        f"  🔴 High severity : {len(high)}",
        f"  🟡 Medium severity : {len(medium)}",
        f"  🟢 Low severity : {len(low)}",
        "",
        "  FLOW",
        f"  {analysis['flow_description']}",
        "",
    ]

    if fps:
        lines.append("  FRICTION POINTS")
        lines.append("  " + "-" * 60)
        for fp in fps:
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(fp["severity"], "⚪")
            lines.append(f"  {icon} [{fp['heuristic_id']}] {fp['heuristic_name']}")
            lines.append(f"     Problem : {fp['description']}")
            lines.append(f"     Check   : {fp['question']}")
            lines.append(f"     Found   : {', '.join(fp['trigger_keywords'])}")
            lines.append(f"     Fix     : {fp['recommendation']}")
            lines.append("")
    else:
        lines.append("  ✅ No major friction points detected.")

    lines.append("=" * 65)
    return "\n".join(lines)


def format_persona(persona: dict) -> str:
    j = persona["journey_summary"]
    bt = persona["behavioral_traits"]
    lines = [
        "=" * 65,
        f"  PERSONA: {persona['name']}",
        "=" * 65,
        f"  Type      : {persona['user_type'].upper()} | Age: {persona['age_range']}",
        f"  Profession: {persona['profession']}",
        f"  Tech Savvy: {persona['tech_savvy']}",
        "",
        "  Goals",
    ]
    for g in persona["goals"]:
        lines.append(f"    • {g}")
    lines.append("")
    lines.append("  Pain Points")
    for p in persona["pain_points"]:
        lines.append(f"    • {p}")
    lines.extend([
        "",
        "  Behavioral Traits",
        f"    Primary Device  : {bt['primary_device']}",
        f"    Session Length  : {bt['time_per_session']}",
        f"    Usage Frequency  : {bt['frequency']}",
        f"    Research Depth  : {bt['research_depth']}",
        "",
        f"  Motivation   : {persona['motivation']}",
        f"  Frustrations: {persona['frustrations']}",
        f"  Support Pref : {persona['preferred_support']}",
        "",
        "  Journey Summary",
        f"    Awareness    : {j['awareness']}",
        f"    Consideration: {j['consideration']}",
        f"    Decision     : {j['decision']}",
        f"    Retention    : {j['retention']}",
        f"    Advocacy     : {j['advocacy']}",
        "",
        f'  Quote: "{persona["quote"]}"',
        f"  [{persona['id']}]",
        "=" * 65,
    ])
    return "\n".join(lines)


# ─── CLI ───────────────────────────────────────────────────────────────────────
def cmd_generate_persona(args):
    persona = generate_persona(
        name=args.name,
        age_range=args.age_range or "25-35",
        profession=args.profession or "",
        tech_savvy=args.tech_savvy,
        goals=args.goals.split("|") if args.goals else None,
        pain_points=args.pain_points.split("|") if args.pain_points else None,
        user_type=args.user_type,
    )
    print(format_persona(persona))


def cmd_analyze(args):
    analysis = analyze_friction_points(
        flow_description=args.flow,
        num_critical=args.num_critical,
    )
    if args.format == "report":
        print(format_analysis_report(analysis))
    else:
        print(format_analysis_report(analysis))


def cmd_audit(args):
    audit = conduct_heuristic_audit(product_type=args.product_type)
    print(f"\n📋 Heuristic Audit: {args.product_type}")
    print("=" * 60)
    print(f"  ID: {audit['id']}")
    print(f"  Typical flows:")
    for flow in audit["typical_flows"]:
        print(f"    - {flow}")
    print(f"\n  Heuristics to evaluate ({len(audit['heuristics'])}):")
    for h in audit["heuristics"]:
        icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(h["severity"], "⚪")
        print(f"    {icon} [{h['id']}] {h['name']} — {h['question']}")


def cmd_list_personas(args):
    personas = load_personas()
    if not personas:
        print("No personas found.")
        return
    print(f"\n{'#':<4} {'Name':<25} {'Type':<10} {'Profession':<20} {'ID':<10}")
    print("-" * 75)
    for i, p in enumerate(personas, 1):
        print(f"{i:<4} {p.get('name',''):<25} {p.get('user_type',''):<10} {p.get('profession',''):<20} {p['id'][:10]}")
    print(f"\nTotal: {len(personas)} persona(s)")


def cmd_show_persona(args):
    personas = load_personas()
    persona = next((p for p in personas if p["id"] == args.persona_id), None)
    if not persona:
        raise ValueError(f"Persona not found: {args.persona_id}")
    print(format_persona(persona))


def cmd_list_research(args):
    research = load_research()
    if not research:
        print("No research found. Run 'analyze' or 'audit' first.")
        return
    print(f"\n{'#':<4} {'Type':<12} {'ID':<10} {'Timestamp':<25} {'Summary'}")
    print("-" * 75)
    for i, r in enumerate(research, 1):
        rtype = r.get("heuristic_id") and "friction" or r.get("product_type") and "audit" or "persona"
        summary = ""
        if "flow_description" in r:
            summary = r["flow_description"][:50]
        elif "product_type" in r:
            summary = f"audit: {r['product_type']}"
        elif "name" in r:
            summary = f"persona: {r['name']}"
        print(f"{i:<4} {rtype:<12} {r['id'][:10]:<10} {r.get('created_at','')[:25]:<25} {summary}")


def cmd_heuristics(args):
    print("\nNielsen's 10 Usability Heuristics:")
    print("=" * 60)
    for h in HEURISTICS:
        icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(h["severity"], "⚪")
        print(f"\n  {icon} [{h['id']}] {h['name']}")
        print(f"      {h['description']}")
        print(f"      Check: {h['question']}")


def main():
    parser = argparse.ArgumentParser(
        prog="ux-researcher",
        description="EmpireHazeClaw UX Researcher — personas, friction analysis, heuristic audits.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_persona = sub.add_parser("persona", help="Generate a user persona")
    p_persona.add_argument("--name", required=True, help="Persona name (e.g. 'Alex the Founder')")
    p_persona.add_argument("--age-range", help="Age range (e.g. '28-40')")
    p_persona.add_argument("--profession", help="Profession/role")
    p_persona.add_argument("--tech-savvy", default="medium", choices=["low", "medium", "high"])
    p_persona.add_argument("--goals", help="Goals (pipe-separated, e.g. 'Goal 1|Goal 2')")
    p_persona.add_argument("--pain-points", help="Pain points (pipe-separated)")
    p_persona.add_argument("--user-type", default="primary", choices=["primary", "secondary", "supplementary"])
    p_persona.set_defaults(fn=cmd_generate_persona)

    p_analyze = sub.add_parser("analyze", help="Analyze friction points in a user flow")
    p_analyze.add_argument("--flow", required=True, help="Describe the user flow to analyze")
    p_analyze.add_argument("--num-critical", type=int, default=3, help="Number of critical points (default: 3)")
    p_analyze.add_argument("--format", default="report", choices=["report", "json"])
    p_analyze.set_defaults(fn=cmd_analyze)

    p_audit = sub.add_parser("audit", help="Generate a heuristic audit checklist")
    p_audit.add_argument("--product-type", default="web_app", choices=["web_app", "mobile_app", "ecommerce", "api"])
    p_audit.set_defaults(fn=cmd_audit)

    p_ls_p = sub.add_parser("list-personas", help="List saved personas")
    p_ls_p.set_defaults(fn=cmd_list_personas)

    p_sh_p = sub.add_parser("show-persona", help="Show a specific persona")
    p_sh_p.add_argument("persona_id", help="Persona ID")
    p_sh_p.set_defaults(fn=cmd_show_persona)

    p_ls_r = sub.add_parser("list-research", help="List saved research items")
    p_ls_r.set_defaults(fn=cmd_list_research)

    p_heur = sub.add_parser("heuristics", help="List Nielsen's 10 usability heuristics")
    p_heur.set_defaults(fn=cmd_heuristics)

    args = parser.parse_args()
    try:
        args.fn(args)
    except Exception as e:
        logger.error("%s", e)
        sys.stderr.write(f"❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
