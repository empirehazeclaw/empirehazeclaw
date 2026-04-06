#!/usr/bin/env python3
"""
AI Policy Writer Agent
EmpireHazeClaw Compliance Suite

Writes AI usage policies, acceptable use guidelines, and compliance documents.
Geschwindigkeit über Perfektion: produce actionable drafts quickly.
Integrität: no deceptive policies.
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "compliance"
LOG_DIR = BASE_DIR / "logs"
POLICIES_FILE = DATA_DIR / "ai_policies.json"

LOG_FILE = LOG_DIR / "ai_policy_writer.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("AIPolicyWriter")


def load_policies() -> dict:
    if POLICIES_FILE.exists():
        try:
            with open(POLICIES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to load %s: %s", POLICIES_FILE, e)
    return {}


def save_policies(data: dict) -> bool:
    try:
        with open(POLICIES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error("Failed to save %s: %s", POLICIES_FILE, e)
        return False


# ─── Policy Templates ─────────────────────────────────────────────────────────
TEMPLATES = {
    "ai_usage_policy": {
        "name": "AI Usage Policy",
        "description": "Defines acceptable use of AI tools by employees and contractors.",
        "sections": [
            "1. Purpose & Scope",
            "2. Approved AI Tools",
            "3. Permitted Use Cases",
            "4. Prohibited Use Cases",
            "5. Data Classification Rules",
            "6. Human Oversight Requirements",
            "7. Documentation & Audit",
            "8. Violations & Enforcement",
        ],
    },
    "ai_transparency_policy": {
        "name": "AI Transparency Policy",
        "description": "Ensures AI-generated content is properly disclosed to stakeholders.",
        "sections": [
            "1. Disclosure Requirements",
            "2. Customer Notification",
            "3. Marketing & Advertising Rules",
            "4. Documentation of AI Use",
            "5. Exceptions & Edge Cases",
        ],
    },
    "ai_risk_policy": {
        "name": "AI Risk & Safety Policy",
        "description": "Identifies and mitigates risks from AI system use.",
        "sections": [
            "1. Risk Categories",
            "2. Risk Assessment Process",
            "3. Mitigation Controls",
            "4. Incident Response",
            "5. Continuous Monitoring",
        ],
    },
    "ai_vendor_policy": {
        "name": "AI Vendor Assessment Policy",
        "description": "Criteria for evaluating and approving third-party AI vendors.",
        "sections": [
            "1. Evaluation Criteria",
            "2. Data Handling Requirements",
            "3. Security Standards",
            "4. Contract Requirements",
            "5. Ongoing Monitoring",
        ],
    },
}


def generate_policy(
    template_key: str,
    company_name: str = "EmpireHazeClaw",
    jurisdiction: str = "EU",
    contact_email: str = "privacy@empirehazeclaw.com",
    custom_sections: list[str] = None,
    tone: str = "professional",
) -> dict:
    """Generate a policy document from a template."""
    if template_key not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_key}. Available: {', '.join(TEMPLATES.keys())}")

    template = TEMPLATES[template_key]
    sections = custom_sections or template["sections"]

    tone_map = {
        "professional": ("This policy is designed to", "All employees must", "Violations may result in"),
        "friendly": ("We believe in using AI responsibly, which means", "Please do your best to", "If issues arise, let's talk"),
        "strict": ("Strict compliance with this policy is mandatory.", "Any deviation from these rules will be treated as a serious matter.", "Violations will result in immediate escalation."),
    }
    openers, requirements, consequences = tone_map.get(tone, tone_map["professional"])

    now = datetime.utcnow()
    year = now.year

    content_parts = [
        f"# {template['name']}",
        f"**Company:** {company_name}",
        f"**Effective Date:** {now.strftime('%Y-%m-%d')}",
        f"**Version:** 1.0",
        f"**Jurisdiction:** {jurisdiction}",
        "",
        "---",
        "",
        f"## Purpose",
        "",
        f"{openers} guide the responsible use of artificial intelligence systems within {company_name}. This policy applies to all employees, contractors, and third parties acting on behalf of the company.",
        "",
    ]

    for section in sections:
        content_parts.append(f"## {section}")
        content_parts.append("")

        if "Purpose" in section:
            content_parts.append(f"{openers} ensure AI is used in ways that are ethical, compliant, and aligned with our business values.")
        elif "Approved" in section or "Permitted" in section:
            content_parts.append(f"**{requirements} only use AI tools that have been pre-approved by the AI Governance team.**")
            content_parts.append("")
            content_parts.append("Current approved tools include:")
            content_parts.append("- Internal AI assistants (authorized LLMs)")
            content_parts.append("- Automated transcription and translation services")
            content_parts.append("- AI-powered analytics platforms with approved data handling agreements")
            content_parts.append("")
            content_parts.append("All other AI tools require written approval before use.")
        elif "Prohibited" in section:
            content_parts.append("The following uses of AI are strictly prohibited:")
            content_parts.append("")
            prohibited = [
                "Processing personal data of EU residents without a valid legal basis",
                "Generating content intended to deceive or manipulate",
                "Using AI to make automated decisions with significant legal impact without human review",
                "Sharing confidential company data with third-party AI services",
                "Bypassing or weakening AI safety controls",
            ]
            for item in prohibited:
                content_parts.append(f"- {item}")
            content_parts.append("")
        elif "Transparency" in section or "Disclosure" in section:
            content_parts.append("AI-generated or AI-assisted content must be clearly identified.")
            content_parts.append("")
            content_parts.append("Requirements:")
            content_parts.append("- Include 'AI-assisted' or 'AI-generated' labels where appropriate")
            content_parts.append("- Log all AI use cases in the AI register")
            content_parts.append("- Notify customers when AI is used in对他们服务")
            content_parts.append("")
        elif "Risk" in section:
            content_parts.append("AI risks are categorized as follows:")
            content_parts.append("")
            risk_cats = [
                ("Low", "Minor inefficiencies, non-critical errors", "Standard monitoring"),
                ("Medium", "Customer-facing errors, data handling concerns", "Manager review within 48h"),
                ("High", "Regulatory violations, security breaches, major factual errors", "Immediate escalation to AI Governance"),
            ]
            content_parts.append(f"| Severity | Description | Response |")
            content_parts.append("|---|---|---|")
            for sev, desc, resp in risk_cats:
                content_parts.append(f"| {sev} | {desc} | {resp} |")
            content_parts.append("")
        elif "Vendor" in section or "Assessment" in section:
            content_parts.append("Before engaging any third-party AI vendor, the following must be completed:")
            content_parts.append("")
            vendor_checks = [
                "Data Processing Agreement (DPA) signed",
                "Security questionnaire completed and reviewed",
                "Evidence of SOC2 / ISO 27001 or equivalent certification",
                "GDPR compliance confirmation for EU data",
                "Right to audit clause in contract",
            ]
            for check in vendor_checks:
                content_parts.append(f"- [ ] {check}")
            content_parts.append("")
        elif "Documentation" in section or "Audit" in section:
            content_parts.append("All AI use must be documented in the AI Activity Register, including:")
            content_parts.append("- Date and duration of use")
            content_parts.append("- Purpose and output description")
            content_parts.append("- Data categories processed")
            content_parts.append("- Whether output was reviewed by a human")
            content_parts.append("")
        elif "Human Oversight" in section or "Enforcement" in section or "Violations" in section:
            content_parts.append(f"{requirements} maintain appropriate human oversight of all AI outputs used in business decisions.")
            content_parts.append("")
            content_parts.append(f"{consequences} disciplinary action, up to and including termination of employment or contract.")
            content_parts.append("")

    content_parts.extend([
        "---",
        "",
        "## Contact",
        "",
        f"For questions about this policy, contact: **{contact_email}**",
        "",
        f"*Document generated by EmpireHazeClaw AI Policy Writer | {year}*",
    ])

    content = "\n".join(content_parts)

    policy = {
        "id": str(uuid.uuid4()),
        "template_key": template_key,
        "name": template["name"],
        "content": content,
        "company_name": company_name,
        "jurisdiction": jurisdiction,
        "contact_email": contact_email,
        "tone": tone,
        "version": "1.0",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    policies = load_policies()
    policies[policy["id"]] = policy
    save_policies(policies)
    logger.info("Policy generated: %s (%s)", template["name"], policy["id"])
    return policy


def list_policies() -> list[dict]:
    policies = load_policies()
    return sorted(policies.values(), key=lambda x: x.get("created_at", ""), reverse=True)


def get_policy(policy_id: str) -> dict:
    policies = load_policies()
    if policy_id not in policies:
        raise ValueError(f"Policy not found: {policy_id}")
    return policies[policy_id]


def update_policy(policy_id: str, content: str = None, version: str = None) -> dict:
    policies = load_policies()
    if policy_id not in policies:
        raise ValueError(f"Policy not found: {policy_id}")
    if content:
        policies[policy_id]["content"] = content
    if version:
        policies[policy_id]["version"] = version
    policies[policy_id]["updated_at"] = datetime.utcnow().isoformat()
    save_policies(policies)
    logger.info("Policy updated: %s", policy_id)
    return policies[policy_id]


# ─── CLI ───────────────────────────────────────────────────────────────────────
def cmd_generate(args):
    custom = args.custom_sections.split("|") if args.custom_sections else None
    policy = generate_policy(
        template_key=args.template,
        company_name=args.company or "EmpireHazeClaw",
        jurisdiction=args.jurisdiction or "EU",
        contact_email=args.contact or "privacy@empirehazeclaw.com",
        custom_sections=custom,
        tone=args.tone,
    )
    print(f"✅ Policy generated: {policy['id']}")
    print(f"   {policy['name']}")
    print(f"   Version {policy['version']} | {policy['jurisdiction']}")
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(policy["content"])
        print(f"   Saved to: {args.output}")
    else:
        print()
        print(policy["content"])


def cmd_list(args):
    policies = list_policies()
    if not policies:
        print("No policies found. Generate one with: ai-policy-writer generate --template ...")
        return
    print(f"\n{'#':<4} {'Name':<35} {'Template':<25} {'Jurisdiction':<12} {'Version':<8} {'Updated'}")
    print("-" * 110)
    for i, p in enumerate(policies, 1):
        print(f"{i:<4} {p.get('name',''):<35} {p.get('template_key',''):<25} {p.get('jurisdiction',''):<12} {p.get('version',''):<8} {p.get('updated_at','')[:10]}")
    print(f"\nTotal: {len(policies)} policy(policies)")


def cmd_show(args):
    policy = get_policy(args.policy_id)
    print(policy["content"])


def cmd_update(args):
    policy = update_policy(args.policy_id, content=args.content, version=args.version)
    print(f"✅ Policy updated: {policy['id']}")


def cmd_templates(args):
    print("\nAvailable Policy Templates:")
    print("=" * 60)
    for key, tmpl in TEMPLATES.items():
        print(f"\n  {key}")
        print(f"  {tmpl['description']}")
        print(f"  Sections:")
        for s in tmpl["sections"]:
            print(f"    - {s}")


def main():
    parser = argparse.ArgumentParser(
        prog="ai-policy-writer",
        description="EmpireHazeClaw AI Policy Writer — generate AI governance policies.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_gen = sub.add_parser("generate", help="Generate a new AI policy")
    p_gen.add_argument("--template", required=True, choices=list(TEMPLATES.keys()), help="Policy template")
    p_gen.add_argument("--company", help="Company name")
    p_gen.add_argument("--jurisdiction", default="EU", help="Jurisdiction (default: EU)")
    p_gen.add_argument("--contact", default="privacy@empirehazeclaw.com", help="Contact email")
    p_gen.add_argument("--tone", default="professional", choices=["professional", "friendly", "strict"], help="Writing tone")
    p_gen.add_argument("--custom-sections", help="Custom sections (pipe-separated, overrides template sections)")
    p_gen.add_argument("--output", help="Output file path (default: print to stdout)")
    p_gen.set_defaults(fn=cmd_generate)

    p_list = sub.add_parser("list", help="List all policies")
    p_list.set_defaults(fn=cmd_list)

    p_show = sub.add_parser("show", help="Show policy content")
    p_show.add_argument("policy_id", help="Policy ID")
    p_show.set_defaults(fn=cmd_show)

    p_upd = sub.add_parser("update", help="Update a policy")
    p_upd.add_argument("policy_id", help="Policy ID")
    p_upd.add_argument("--content", required=True, help="New policy content (full markdown)")
    p_upd.add_argument("--version", help="New version string")
    p_upd.set_defaults(fn=cmd_update)

    p_tmpl = sub.add_parser("templates", help="List available policy templates")
    p_tmpl.set_defaults(fn=cmd_templates)

    args = parser.parse_args()
    try:
        args.fn(args)
    except Exception as e:
        logger.error("%s", e)
        sys.stderr.write(f"❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
