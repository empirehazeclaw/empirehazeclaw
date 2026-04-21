#!/usr/bin/env python3
"""
innovation_trend_detector.py — Trend Detection for Innovation Research
======================================================================
Detects emerging patterns in the KG by analyzing:
- Entity growth rate vs 7-day average
- "Rising topics" (recent entities with many relations)
- Alerts when growth rate exceeds threshold

Usage:
    python3 innovation_trend_detector.py --check       # Quick trend check
    python3 innovation_trend_detector.py --full        # Full analysis with alerts
    python3 innovation_trend_detector.py --test        # Test mode

Output: /home/clawbot/.openclaw/workspace/data/innovation_trends.json
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
TRENDS_FILE = WORKSPACE / "data/innovation_trends.json"
HISTORY_FILE = WORKSPACE / "data/innovation_trend_history.json"

# Thresholds
GROWTH_RATE_THRESHOLD = 0.15  # 15% growth = rising trend
RELATIONS_FOR_RISING = 3  # Min relations for "rising topic"
RECENT_DAYS = 7  # Look back period for "recent"

def load_kg():
    """Load KG."""
    if not KG_PATH.exists():
        return None
    with open(KG_PATH) as f:
        return json.load(f)

def compute_entity_growth(kg, days=7):
    """Compute entity growth rate over time window."""
    since = datetime.now() - timedelta(days=days)
    entities = kg.get("entities", {})
    
    recent_count = 0
    total_count = len(entities)
    
    for entity in entities.values():
        created = entity.get("created", "")
        if created:
            try:
                created_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if created_date > since:
                    recent_count += 1
            except:
                pass
    
    growth_rate = recent_count / total_count if total_count > 0 else 0
    return {
        "recent_new": recent_count,
        "total": total_count,
        "growth_rate": growth_rate,
        "period_days": days,
    }

def find_rising_topics(kg, min_relations=RELATIONS_FOR_RISING):
    """Find entities with recent creation + many relations (rising topics)."""
    entities = kg.get("entities", {})
    relations = kg.get("relations", {})
    
    # Count relations per entity
    relation_count = defaultdict(int)
    for rel in relations.values():
        relation_count[rel.get("from")] += 1
        relation_count[rel.get("to")] += 1
    
    # Find recent entities with high relation count
    since = datetime.now() - timedelta(days=RECENT_DAYS)
    rising_topics = []
    
    for eid, entity in entities.items():
        created = entity.get("created", "")
        if created:
            try:
                created_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if created_date > since:
                    rels = relation_count.get(eid, 0)
                    if rels >= min_relations:
                        rising_topics.append({
                            "entity_id": eid,
                            "type": entity.get("type", "unknown"),
                            "relation_count": rels,
                            "created": created[:10],
                        })
            except:
                pass
    
    # Sort by relation count descending
    rising_topics.sort(key=lambda x: x["relation_count"], reverse=True)
    return rising_topics

def compute_type_distribution(kg):
    """Compute entity type distribution."""
    entities = kg.get("entities", {})
    types = defaultdict(int)
    
    for entity in entities.values():
        t = entity.get("type", "unknown")
        types[t] += 1
    
    return dict(types)

def load_trend_history():
    """Load historical trend data for comparison."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"snapshots": []}

def save_trend_snapshot(growth_data, type_dist, rising_topics):
    """Save current snapshot to history for trend comparison."""
    history = load_trend_history()
    
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "entity_growth": growth_data,
        "top_types": dict(sorted(type_dist.items(), key=lambda x: x[1], reverse=True)[:5]),
        "rising_topic_count": len(rising_topics),
    }
    
    # Keep last 14 snapshots
    history["snapshots"].append(snapshot)
    history["snapshots"] = history["snapshots"][-14:]
    history["last_updated"] = datetime.now().isoformat()
    
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def analyze_trends(growth_data, rising_topics, type_dist, history):
    """Analyze trends and generate alerts."""
    alerts = []
    insights = []
    
    # Check growth rate vs history
    snapshots = history.get("snapshots", [])
    if len(snapshots) >= 2:
        prev_growth = snapshots[-1].get("entity_growth", {}).get("growth_rate", 0)
        curr_growth = growth_data.get("growth_rate", 0)
        
        if curr_growth > prev_growth * 1.5 and curr_growth > GROWTH_RATE_THRESHOLD:
            alerts.append({
                "type": "rising_entity_growth",
                "message": f"Entity growth accelerating: {curr_growth:.1%} (was {prev_growth:.1%})",
                "severity": "medium",
            })
    
    # Check if new rising topics
    if len(rising_topics) > 3:
        alerts.append({
            "type": "rising_topics_detected",
            "message": f"{len(rising_topics)} rising topics with high connectivity",
            "severity": "low",
        })
        insights.append(f"Active rising topics: {', '.join(t['entity_id'][:30] for t in rising_topics[:3])}")
    
    # Check for new types emerging
    current_types = set(type_dist.keys())
    if len(snapshots) >= 1:
        prev_types = set(snapshots[-1].get("top_types", {}).keys())
        new_types = current_types - prev_types
        if new_types:
            alerts.append({
                "type": "new_entity_types",
                "message": f"New entity types detected: {', '.join(list(new_types)[:3])}",
                "severity": "low",
            })
    
    # High-growth entity clusters
    if growth_data.get("recent_new", 0) > 10:
        insights.append(f"High creation rate: {growth_data['recent_new']} new entities in last {growth_data['period_days']} days")
    
    return alerts, insights

def run_check():
    """Quick trend check."""
    kg = load_kg()
    if not kg:
        print("❌ KG not found")
        return None
    
    growth = compute_entity_growth(kg, days=7)
    rising = find_rising_topics(kg)
    
    print("📊 Innovation Trend Check")
    print(f"   Entity Growth (7d): {growth['recent_new']} new / {growth['total']} total = {growth['growth_rate']:.1%}")
    print(f"   Rising Topics: {len(rising)}")
    
    if rising:
        print("   Top rising topics:")
        for t in rising[:3]:
            print(f"      - {t['entity_id'][:40]} ({t['type']}): {t['relation_count']} rels")
    
    return {
        "growth": growth,
        "rising_count": len(rising),
    }

def run_full_analysis():
    """Full trend analysis with alerts."""
    kg = load_kg()
    if not kg:
        print("❌ KG not found")
        return False
    
    print("🔍 Innovation Trend Analysis")
    print("=" * 50)
    
    # Compute metrics
    growth = compute_entity_growth(kg, days=7)
    rising = find_rising_topics(kg)
    types = compute_type_distribution(kg)
    history = load_trend_history()
    
    print(f"\n📈 Entity Growth (7-day)")
    print(f"   New entities: {growth['recent_new']}")
    print(f"   Total entities: {growth['total']}")
    print(f"   Growth rate: {growth['growth_rate']:.1%}")
    
    print(f"\n🔥 Rising Topics ({RELATIONS_FOR_RISING}+ relations, recent)")
    print(f"   Count: {len(rising)}")
    if rising:
        for t in rising[:5]:
            print(f"      - {t['entity_id'][:40]}")
            print(f"        type={t['type']}, rels={t['relation_count']}, created={t['created']}")
    
    print(f"\n📦 Entity Types (top 5)")
    for t, c in sorted(types.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   {t}: {c}")
    
    # Analyze trends
    alerts, insights = analyze_trends(growth, rising, types, history)
    
    print(f"\n🚨 Alerts ({len(alerts)})")
    if alerts:
        for a in alerts:
            print(f"   [{a['severity'].upper()}] {a['message']}")
    else:
        print("   None")
    
    print(f"\n💡 Insights ({len(insights)})")
    for i in insights:
        print(f"   - {i}")
    
    # Save snapshot
    save_trend_snapshot(growth, types, rising)
    
    # Compile result
    result = {
        "timestamp": datetime.now().isoformat(),
        "entity_growth": growth,
        "rising_topics": rising[:10],
        "type_distribution": dict(sorted(types.items(), key=lambda x: x[1], reverse=True)[:10]),
        "alerts": alerts,
        "insights": insights,
    }
    
    with open(TRENDS_FILE, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Saved to {TRENDS_FILE}")
    
    return result

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Quick trend check")
    parser.add_argument("--full", action="store_true", help="Full analysis with alerts")
    parser.add_argument("--test", action="store_true", help="Test mode")
    args = parser.parse_args()
    
    if args.check:
        run_check()
    elif args.full or args.test:
        result = run_full_analysis()
        if result:
            print(f"\n✅ Analysis complete — {len(result.get('alerts', []))} alerts")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
