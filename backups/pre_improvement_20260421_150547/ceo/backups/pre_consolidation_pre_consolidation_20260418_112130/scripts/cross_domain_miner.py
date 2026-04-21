#!/usr/bin/env python3
"""
Cross-Domain Miner — Phase 5, Day 1
===================================
Discovers relationships between different task domains.

Features:
- Domain transfer learning (learnings from Type A → Type B)
- DiscoGAN-inspired relation discovery
- Latent connection detection
- Transfer accuracy tracking

Usage:
    python3 cross_domain_miner.py --mine             # Mine cross-domain patterns
    python3 cross_domain_miner.py --transfer <src> <dst> # Suggest transfer
    python3 cross_domain_miner.py --patterns        # Show discovered patterns
    python3 cross_domain_miner.py --report          # Generate report
"""

import json
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
MINING_DIR = WORKSPACE / "memory" / "evaluations" / "cross_domain"
MINING_FILE = MINING_DIR / "cross_domain_patterns.json"
KG_PATH = WORKSPACE / "memory" / "kg" / "knowledge_graph.json"

def init_dirs():
    MINING_DIR.mkdir(parents=True, exist_ok=True)
    if not MINING_FILE.exists():
        MINING_FILE.write_text(json.dumps({
            "patterns": [],
            "transfers": [],
            "domain_graph": {},
            "version": "1.0"
        }))

def load_mining():
    init_dirs()
    return json.loads(MINING_FILE.read_text())

def save_mining(data):
    MINING_FILE.write_text(json.dumps(data, indent=2))

def load_kg():
    if KG_PATH.exists():
        return json.load(open(KG_PATH))
    return {"entities": {}, "relations": {}}

def extract_domains():
    """Extract domains from KG entities."""
    kg = load_kg()
    
    domains = defaultdict(list)
    
    for name, entity in kg.get("entities", {}).items():
        entity_type = entity.get("type", "unknown")
        
        # Categorize into domains
        if entity_type in ["learning", "antipattern"]:
            learning_type = entity.get("learning_type", "unknown")
            if "timeout" in learning_type.lower() or "api" in learning_type.lower():
                domains["network"].append((name, entity))
            elif "validation" in learning_type.lower() or "input" in learning_type.lower():
                domains["data"].append((name, entity))
            elif "context" in learning_type.lower() or "memory" in learning_type.lower():
                domains["memory"].append((name, entity))
            elif "delegation" in learning_type.lower() or "agent" in learning_type.lower():
                domains["orchestration"].append((name, entity))
            else:
                domains["general"].append((name, entity))
        
        elif entity_type in ["failure", "error"]:
            domains["reliability"].append((name, entity))
        
        elif entity_type == "strategy":
            domains["strategy"].append((name, entity))
    
    return domains

def find_cross_domain_patterns():
    """Find patterns that transfer across domains."""
    domains = extract_domains()
    mining = load_mining()
    
    patterns = []
    pattern_id = len(mining.get("patterns", [])) + 1
    
    domain_list = list(domains.keys())
    
    # Compare domain pairs
    for i, domain_a in enumerate(domain_list):
        for domain_b in domain_list[i+1:]:
            entities_a = domains[domain_a]
            entities_b = domains[domain_b]
            
            if not entities_a or not entities_b:
                continue
            
            # Look for common properties
            common_tags = find_common_properties(entities_a, entities_b)
            
            if common_tags:
                pattern = {
                    "id": f"XDP-{pattern_id:04d}",
                    "domain_a": domain_a,
                    "domain_b": domain_b,
                    "common_properties": common_tags,
                    "transferability": calculate_transferability(entities_a, entities_b, common_tags),
                    "examples": {
                        domain_a: [name for name, _ in entities_a[:2]],
                        domain_b: [name for name, _ in entities_b[:2]]
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                patterns.append(pattern)
                pattern_id += 1
    
    # Save patterns
    mining["patterns"] = patterns
    save_mining(mining)
    
    print(f"\nCross-Domain Mining Complete")
    print("=" * 50)
    print(f"Domains found: {len(domains)}")
    print(f"Patterns discovered: {len(patterns)}")
    
    for p in patterns[:5]:
        print(f"\n[{p['id']}] {p['domain_a']} <-> {p['domain_b']}")
        print(f"  Common: {', '.join(p['common_properties'][:5])}")
        print(f"  Transferability: {p['transferability']:.2f}")
    
    return patterns

def find_common_properties(entities_a, entities_b):
    """Find common properties between two sets of entities."""
    props_a = extract_properties(entities_a)
    props_b = extract_properties(entities_b)
    
    common = list(set(props_a) & set(props_b))
    return common[:10]  # Top 10

def extract_properties(entities):
    """Extract properties from entities."""
    props = set()
    
    for name, entity in entities:
        # From tags
        for tag in entity.get("tags", []):
            props.add(tag)
        
        # From learning_type
        lt = entity.get("learning_type", "")
        if lt:
            props.add(lt)
        
        # From category
        cat = entity.get("category", "")
        if cat:
            props.add(cat)
        
        # From facts content
        for fact in entity.get("facts", []):
            content = fact.get("content", "")
            words = content.lower().split()
            # Extract significant words
            for word in words:
                if len(word) > 4:
                    props.add(word)
    
    return props

def calculate_transferability(entities_a, entities_b, common_props):
    """Calculate how transferable learnings are between domains."""
    if not common_props:
        return 0.0
    
    # Factors:
    # 1. Number of common properties
    prop_score = min(len(common_props) / 5, 1.0) * 0.4
    
    # 2. Sample size in both domains
    size_score = min(min(len(entities_a), len(entities_b)) / 5, 1.0) * 0.3
    
    # 3. Evidence quality (have facts)
    evidence_a = sum(1 for _, e in entities_a if e.get("facts"))
    evidence_b = sum(1 for _, e in entities_b if e.get("facts"))
    evidence_score = ((evidence_a / max(len(entities_a), 1)) + (evidence_b / max(len(entities_b), 1))) / 2 * 0.3
    
    return min(prop_score + size_score + evidence_score, 1.0)

def suggest_transfer(source_domain, target_domain):
    """Suggest what can be transferred from source to target domain."""
    mining = load_mining()
    
    # Find existing patterns
    matching = [
        p for p in mining.get("patterns", [])
        if (p["domain_a"] == source_domain and p["domain_b"] == target_domain) or
           (p["domain_a"] == target_domain and p["domain_b"] == source_domain)
    ]
    
    if matching:
        best = max(matching, key=lambda x: x["transferability"])
        print(f"\nTransfer suggestion: {source_domain} -> {target_domain}")
        print(f"=" * 50)
        print(f"Pattern: {best['id']}")
        print(f"Transferability: {best['transferability']:.2f}")
        print(f"Common properties: {', '.join(best['common_properties'][:5])}")
        print(f"\nRecommendations:")
        print(f"  - Apply {source_domain} strategies to {target_domain}")
        print(f"  - Share: {', '.join(best['common_properties'][:3])}")
        return best
    
    # No pattern - use general heuristics
    print(f"\nNo direct pattern found for {source_domain} -> {target_domain}")
    print(f"Using general heuristics:")
    
    heuristics = get_transfer_heuristics(source_domain, target_domain)
    for h in heuristics:
        print(f"  -> {h}")
    
    return heuristics

def get_transfer_heuristics(source, target):
    """Get general transfer heuristics between domains."""
    heuristics = []
    
    # Timeout patterns transfer to reliability
    if source in ["network", "general"] and target in ["reliability", "orchestration"]:
        heuristics.append("Timeout handling patterns likely transferable")
        heuristics.append("Retry logic applicable")
        heuristics.append("Error categorization approach useful")
    
    # Memory patterns transfer to orchestration
    if source == "memory" and target in ["orchestration", "strategy"]:
        heuristics.append("Context management transferable")
        heuristics.append("Cache strategies applicable")
        heuristics.append("State tracking patterns useful")
    
    # Data patterns transfer broadly
    if source == "data" and target != "data":
        heuristics.append("Validation patterns transferable")
        heuristics.append("Input sanitization approaches applicable")
        heuristics.append("Schema design patterns useful")
    
    # Strategy patterns transfer
    if source == "strategy":
        heuristics.append("Strategy selection framework applicable")
        heuristics.append("Fallback strategies transferable")
        heuristics.append("Optimization patterns useful")
    
    return heuristics if heuristics else ["No obvious transfer patterns - treat as separate domains"]

def show_patterns():
    """Show all discovered cross-domain patterns."""
    mining = load_mining()
    patterns = mining.get("patterns", [])
    
    if not patterns:
        print("[*] No patterns found. Run --mine first.")
        return
    
    print(f"\nCross-Domain Patterns ({len(patterns)} total)")
    print("=" * 50)
    
    sorted_patterns = sorted(patterns, key=lambda x: -x["transferability"])
    
    for p in sorted_patterns[:10]:
        transfer = p["transferability"]
        bar = "█" * int(transfer * 10) + "░" * (10 - int(transfer * 10))
        print(f"\n[{p['id']}] {p['domain_a']} <-> {p['domain_b']}")
        print(f"  Transferability: [{bar}] {transfer:.2f}")
        print(f"  Common: {', '.join(p['common_properties'][:3])}")
    
    # Show domain graph
    show_domain_graph(mining)

def show_domain_graph(mining):
    """Show domain relationship graph."""
    domains = set()
    connections = []
    
    for p in mining.get("patterns", []):
        domains.add(p["domain_a"])
        domains.add(p["domain_b"])
        connections.append((p["domain_a"], p["domain_b"], p["transferability"]))
    
    print(f"\n\nDomain Graph:")
    print(f"  Nodes: {', '.join(sorted(domains))}")
    print(f"  Connections: {len(connections)}")
    
    for src, dst, transfer in sorted(connections, key=lambda x: -x[2])[:5]:
        print(f"    {src} --({transfer:.2f})--> {dst}")

def generate_report():
    """Generate cross-domain analysis report."""
    mining = load_mining()
    domains = extract_domains()
    patterns = mining.get("patterns", [])
    
    # Calculate stats
    by_domain = defaultdict(list)
    for p in patterns:
        by_domain[p["domain_a"]].append(p)
        by_domain[p["domain_b"]].append(p)
    
    most_connected = sorted(by_domain.items(), key=lambda x: -len(x[1]))[:5]
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "domains_found": len(domains),
        "patterns_discovered": len(patterns),
        "domain_stats": {d: len(e) for d, e in domains.items()},
        "most_connected_domains": [(d, len(p)) for d, p in most_connected],
        "high_transferability": [
            {"id": p["id"], "domains": f"{p['domain_a']}-{p['domain_b']}", "score": p["transferability"]}
            for p in sorted(patterns, key=lambda x: -x["transferability"])[:5]
        ]
    }
    
    print(f"\nCross-Domain Mining Report")
    print("=" * 50)
    print(f"Generated: {report['generated_at'][:19]}")
    print(f"Domains found: {report['domains_found']}")
    print(f"Patterns discovered: {report['patterns_discovered']}")
    
    print(f"\nDomain sizes:")
    for d, count in sorted(report['domain_stats'].items(), key=lambda x: -x[1]):
        print(f"  {d}: {count}")
    
    print(f"\nMost connected domains:")
    for d, count in most_connected:
        print(f"  {d}: {count} patterns")
    
    if report['high_transferability']:
        print(f"\nTop transferability patterns:")
        for p in report['high_transferability']:
            print(f"  {p['id']}: {p['domains']} ({p['score']:.2f})")
    
    report_file = WORKSPACE / "docs" / "cross_domain_report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\nReport saved: {report_file}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Cross-Domain Miner")
    parser.add_argument("--mine", action="store_true", help="Mine cross-domain patterns")
    parser.add_argument("--transfer", nargs=2, metavar=("SOURCE", "TARGET"), help="Suggest transfer from source to target")
    parser.add_argument("--patterns", action="store_true", help="Show discovered patterns")
    parser.add_argument("--report", action="store_true", help="Generate report")
    
    args = parser.parse_args()
    
    init_dirs()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    if args.mine:
        find_cross_domain_patterns()
    
    if args.transfer:
        suggest_transfer(args.transfer[0], args.transfer[1])
    
    if args.patterns:
        show_patterns()
    
    if args.report:
        generate_report()

if __name__ == "__main__":
    main()
