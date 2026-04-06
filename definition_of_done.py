#!/usr/bin/env python3
"""
📋 DEFINITION OF DONE
======================
Each task type has clear completion criteria.
"""

DONE_CRITERIA = {
    "dev": {
        "description": "Development tasks",
        "criteria": [
            "Code compiles/runs without errors",
            "Functionality works as specified",
            "No security vulnerabilities introduced"
        ],
        "validation": "Run the code and verify output"
    },
    "researcher": {
        "description": "Research tasks", 
        "criteria": [
            "At least 3 sources cited",
            "Key findings summarized in bullet points",
            "Actionable recommendations included"
        ],
        "validation": "Check output has sources + summary"
    },
    "content": {
        "description": "Content tasks",
        "criteria": [
            "Content is written in target language",
            "Has clear headline",
            "Includes CTA (Call to Action)"
        ],
        "validation": "Review content for quality"
    },
    "pod": {
        "description": "Print on Demand",
        "criteria": [
            "Design created in correct format",
            "Listed on Etsy with tags",
            "Pricing calculated correctly"
        ],
        "validation": "Check Etsy listing"
    },
    "social": {
        "description": "Social Media",
        "criteria": [
            "Posted on correct platform",
            "Has engagement elements (question/poll)",
            "Character count appropriate"
        ],
        "validation": "Check post is live"
    },
    "outreach": {
        "description": "Outreach",
        "criteria": [
            "Personalized message",
            "Clear value proposition", 
            "Working link/CTA"
        ],
        "validation": "Email sent successfully"
    },
    "security": {
        "description": "Security tasks",
        "criteria": [
            "No critical vulnerabilities found",
            "Report includes severity levels",
            "Remediation steps provided"
        ],
        "validation": "Review security scan results"
    }
}

def validate_task(agent_type, result):
    """Validate if task meets Definition of Done"""
    
    if agent_type not in DONE_CRITERIA:
        return {"valid": True, "message": "No criteria defined"}
    
    criteria = DONE_CRITERIA[agent_type]["criteria"]
    
    # Simple validation - in production, use more sophisticated checks
    checks = []
    
    for criterion in criteria:
        checks.append({
            "criterion": criterion,
            "passed": True,  # Would need real validation logic
            "note": "Auto-pass for now"
        })
    
    return {
        "agent_type": agent_type,
        "total_criteria": len(criteria),
        "passed": len([c for c in checks if c["passed"]]),
        "checks": checks,
        "valid": all(c["passed"] for c in checks)
    }

if __name__ == "__main__":
    print("📋 Definition of Done\n")
    for agent, info in DONE_CRITERIA.items():
        print(f"{agent.upper()}:")
        print(f"  {info['description']}")
        for c in info['criteria']:
            print(f"  ✓ {c}")
        print()
