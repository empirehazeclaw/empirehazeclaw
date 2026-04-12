#!/usr/bin/env python3
"""
gene_diversity_tracker.py — Track and Enforce Gene Diversity
Sir HazeClaw - 2026-04-11

Tracks gene usage to prevent stagnation.

Usage:
    python3 gene_diversity_tracker.py --check
    python3 gene_diversity_tracker.py --log --gene gene_name
    python3 gene_diversity_tracker.py --suggest
"""

import json
import sys
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
GENE_LOG = WORKSPACE / "data" / "gene_diversity.json"

# Available genes (from evolver)
GENES = [
    "gene_gep_repair_from_errors",
    "gene_gep_refactor_complex",
    "gene_gep_optimize_performance",
    "gene_gep_add_tests",
    "gene_gep_improve_documentation",
    "gene_gep_extract_pattern",
    "gene_gep_simplify_interface",
    "gene_gep_strengthen_security",
]

def load_log():
    if GENE_LOG.exists():
        with open(GENE_LOG) as f:
            return json.load(f)
    return {"usage": {}, "history": []}

def save_log(data):
    GENE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(GENE_LOG, "w") as f:
        json.dump(data, f, indent=2)

def log_gene(gene):
    """Log gene usage."""
    data = load_log()
    
    if gene not in data["usage"]:
        data["usage"][gene] = 0
    data["usage"][gene] += 1
    
    data["history"].append({
        "gene": gene,
        "timestamp": datetime.now().isoformat()
    })
    
    data["history"] = data["history"][-50:]  # Keep last 50
    
    save_log(data)
    
    count = data["usage"][gene]
    print(f"✅ Logged: {gene} (total: {count}x)")

def check_stagnation():
    """Check for gene stagnation."""
    data = load_log()
    usage = data.get("usage", {})
    
    print("🧬 GENE DIVERSITY CHECK")
    print("=" * 50)
    
    if not usage:
        print("No data yet. Log gene usage with --log")
        return True
    
    # Check for same gene 3+ times
    for gene, count in usage.items():
        if count >= 3:
            print(f"⚠️ STAGNATION: {gene} used {count}x!")
    
    # Calculate diversity
    total_uses = sum(usage.values())
    unique_genes = len(usage)
    
    if total_uses > 0:
        diversity_ratio = unique_genes / total_uses
        
        print(f"\n📊 Diversity:")
        print(f"   Unique Genes: {unique_genes}")
        print(f"   Total Uses: {total_uses}")
        print(f"   Diversity Ratio: {diversity_ratio:.2f}")
        
        if diversity_ratio < 0.3:
            print(f"❌ LOW DIVERSITY — Try different genes!")
            return False
        elif diversity_ratio < 0.5:
            print(f"⚠️ MEDIUM DIVERSITY — Could be better")
            return False
        else:
            print(f"✅ GOOD DIVERSITY")
            return True
    
    return True

def suggest_gene():
    """Suggest a gene to use based on diversity."""
    data = load_log()
    usage = data.get("usage", {})
    
    print("🧬 GENE SUGGESTION")
    print("=" * 50)
    
    if not usage:
        # No history — suggest random
        import random
        gene = random.choice(GENES)
        print(f"First time! Suggesting: {gene}")
        return
    
    # Find least used genes
    sorted_usage = sorted(usage.items(), key=lambda x: x[1])
    least_used = [g for g, c in sorted_usage if c < 3]
    
    if least_used:
        print(f"📋 Suggest trying: {least_used[0]}")
        print(f"   (Used {usage[least_used[0]]}x — less stagnated)")
    else:
        print("⚠️ All genes used 3x+. Consider adding new genes!")

def main():
    if "--log" in sys.argv:
        gene = None
        for i, arg in enumerate(sys.argv):
            if arg == "--gene" and i + 1 < len(sys.argv):
                gene = sys.argv[i + 1]
        
        if gene:
            log_gene(gene)
        return
    
    if "--check" in sys.argv:
        check_stagnation()
        return
    
    if "--suggest" in sys.argv:
        suggest_gene()
        return
    
    # Default
    check_stagnation()

if __name__ == "__main__":
    from datetime import datetime
    main()
