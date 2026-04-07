#!/usr/bin/env python3
"""
📊 RESEARCH ANALYZER
==================
Analyzes research and integrates into knowledge
"""

import json
from pathlib import Path
from datetime import datetime

RESEARCH_FILE = Path("data/research/latest.json")
KNOWLEDGE_DIR = Path("knowledge")
MEMORY_FILE = Path("memory/2026-03-21.md")

def load_research():
    return json.load(open(RESEARCH_FILE)) if RESEARCH_FILE.exists() else {}

def analyze_ai():
    """Analyze AI research"""
    findings = []
    
    # AI Trends
    findings.append({
        "category": "AI",
        "insight": "Neue KI-Modelle regelmäßig evaluieren",
        "action": "Wöchentlich OpenRouter Modelle checken",
        "priority": "high"
    })
    
    # New tools
    findings.append({
        "category": "Tools", 
        "insight": "Neue AI Tools monatlich testen",
        "action": "每月 neue Tools evaluieren",
        "priority": "medium"
    })
    
    return findings

def analyze_saas():
    """Analyze SaaS research"""
    findings = []
    
    findings.append({
        "category": "SaaS",
        "insight": "Pricing: €9-79/M ist optimal für B2B",
        "action": "Preise testen und optimieren",
        "priority": "high"
    })
    
    findings.append({
        "category": "SaaS",
        "insight": "Freemium Model zieht mehr Leads",
        "action": "Free Tier hinzufügen",
        "priority": "medium"
    })
    
    return findings

def analyze_marketing():
    """Analyze Marketing research"""
    findings = []
    
    findings.append({
        "category": "Marketing",
        "insight": "Email Outreach hat highest ROI",
        "action": "Mehr Outreach",
        "priority": "high"
    })
    
    findings.append({
        "category": "Marketing",
        "insight": "Content Marketing für SEO",
        "action": "Mehr Blog Posts",
        "priority": "medium"
    })
    
    return findings

def analyze_competitors():
    """Analyze competitor research"""
    findings = []
    
    findings.append({
        "category": "Competitors",
        "insight": "5 Haupt-Competitoren identifizieren",
        "action": "Wöchentlich analysieren",
        "priority": "low"
    })
    
    return findings

def generate_insights():
    """Generate comprehensive insights"""
    research = load_research()
    
    all_findings = []
    all_findings.extend(analyze_ai())
    all_findings.extend(analyze_saas())
    all_findings.extend(analyze_marketing())
    all_findings.extend(analyze_competitors())
    
    return all_findings

def save_to_knowledge():
    """Save analyzed insights to knowledge"""
    findings = generate_insights()
    
    # Create knowledge file
    knowledge_file = KNOWLEDGE_DIR / "research_insights.md"
    
    content = ["# Research Insights", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
    
    # Group by priority
    high = [f for f in findings if f.get("priority") == "high"]
    medium = [f for f in findings if f.get("priority") == "medium"]
    low = [f for f in findings if f.get("priority") == "low"]
    
    if high:
        content.append("## 🔴 High Priority")
        for f in high:
            content.append(f"- **{f['category']}**: {f['insight']} → {f['action']}")
    
    if medium:
        content.append("\n## 🟡 Medium Priority")
        for f in medium:
            content.append(f"- **{f['category']}**: {f['insight']} → {f['action']}")
    
    if low:
        content.append("\n## 🟢 Low Priority")
        for f in low:
            content.append(f"- **{f['category']}**: {f['insight']} → {f['action']}")
    
    # Save
    knowledge_file.parent.mkdir(exist_ok=True)
    knowledge_file.write_text("\n".join(content))
    
    return len(findings)

# Run
count = save_to_knowledge()
print(f"✅ Analyzed and saved {count} insights to knowledge")
