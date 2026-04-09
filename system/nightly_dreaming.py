#!/usr/bin/env python3
"""
Nightly Dreaming Script — CEO Autonomous System
Läuft: Täglich 02:00 UTC
Analysiert: Memory, Knowledge Graph, Task History
Generiert: Insights, neue Connections, Opportunities
"""

import json
import os
from datetime import datetime, timedelta

WORKSPACE = "/home/clawbot/.openclaw/workspace"
KG_FILE = f"{WORKSPACE}/memory/knowledge_graph.json"
INSIGHTS_DIR = f"{WORKSPACE}/memory/shared/insights"
IDLE_QUEUE = f"{WORKSPACE}/shared/IDLE_QUEUE.md"

def analyze_memory():
    """Analysiert Memory für neue Insights."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    insights = []
    
    # 1. Knowledge Graph analysieren
    if os.path.exists(KG_FILE):
        try:
            with open(KG_FILE, "r") as f:
                kg = json.load(f)
            
            entities = kg.get("entities", [])
            relations = kg.get("relations", [])
            
            # Finde orphan entities (keine relations)
            orphan_count = 0
            for e in entities:
                has_relation = False
                for r in relations:
                    if r.get("from") == e.get("id") or r.get("to") == e.get("id"):
                        has_relation = True
                        break
                if not has_relation:
                    orphan_count += 1
            
            insights.append({
                "type": "knowledge_graph",
                "entities": len(entities),
                "relations": len(relations),
                "orphans": orphan_count,
                "recommendation": "Connect orphan entities" if orphan_count > 5 else "KG looks healthy"
            })
        except Exception as e:
            insights.append({"type": "error", "message": str(e)})
    
    # 2. Recent memory files check
    memory_dir = f"{WORKSPACE}/memory"
    recent_files = []
    if os.path.exists(memory_dir):
        for root, dirs, files in os.walk(memory_dir):
            for f in files:
                if f.endswith(".md"):
                    path = os.path.join(root, f)
                    mtime = os.path.getmtime(path)
                    age_days = (datetime.utcnow().timestamp() - mtime) / 86400
                    if age_days <= 7:
                        recent_files.append({"file": f, "age_days": round(age_days, 1)})
    
    insights.append({
        "type": "recent_memory",
        "files_count": len(recent_files),
        "files": recent_files[:10]  # top 10
    })
    
    return insights, timestamp

def generate_insight_report(insights, timestamp):
    """Generiert den Nacht-Bericht."""
    
    report = f"""# 🌙 Nightly Dreaming Report — {timestamp}

## Analysis Results

"""
    
    for insight in insights:
        report += f"### {insight['type'].replace('_', ' ').title()}\n"
        for key, value in insight.items():
            if key != "type":
                report += f"- **{key}:** {value}\n"
        report += "\n"
    
    return report

def create_opportunities(insights):
    """Erstellt Opportunities basierend auf Insights."""
    opportunities = []
    
    for insight in insights:
        if insight.get("type") == "knowledge_graph":
            if insight.get("orphans", 0) > 5:
                opportunities.append({
                    "type": "kg_cleanup",
                    "description": f"Connect {insight['orphans']} orphan entities in KG",
                    "priority": "medium"
                })
        
        if insight.get("type") == "recent_memory":
            if insight.get("files_count", 0) < 3:
                opportunities.append({
                    "type": "memory_gap",
                    "description": "Few recent memory files - agents may be idle",
                    "priority": "low"
                })
    
    return opportunities

def save_insight(content, timestamp):
    """Speichert Insight in shared/insights."""
    os.makedirs(INSIGHTS_DIR, exist_ok=True)
    
    filename = f"nightly_dreaming_{datetime.utcnow().strftime('%Y-%m-%d')}.md"
    filepath = f"{INSIGHTS_DIR}/{filename}"
    
    with open(filepath, "w") as f:
        f.write(content)
    
    return filepath

def update_idle_queue(opportunities):
    """Updated die IDLE_QUEUE mit neuen Opportunities."""
    if not opportunities:
        return
    
    queue_content = f"# IDLE QUEUE — Auto-generated {datetime.utcnow().isoformat()}Z\n\n"
    queue_content += "## Nightly Dreaming Opportunities\n\n"
    
    for i, opp in enumerate(opportunities, 1):
        queue_content += f"### {i}. [{opp['type']}]\n"
        queue_content += f"- **Priority:** {opp['priority']}\n"
        queue_content += f"- **Description:** {opp['description']}\n\n"
    
    with open(IDLE_QUEUE, "w") as f:
        f.write(queue_content)

def run():
    print("🌙 Starting Nightly Dreaming...")
    
    insights, timestamp = analyze_memory()
    report = generate_insight_report(insights, timestamp)
    opportunities = create_opportunities(insights)
    
    # Save insight
    filepath = save_insight(report, timestamp)
    print(f"✅ Insight saved: {filepath}")
    
    # Update idle queue
    update_idle_queue(opportunities)
    print(f"✅ {len(opportunities)} opportunities added to queue")
    
    print(f"🌙 Nightly Dreaming complete: {len(insights)} insights, {len(opportunities)} opportunities")
    
    return report

if __name__ == "__main__":
    run()