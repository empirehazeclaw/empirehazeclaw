#!/usr/bin/env python3
"""
performance_dashboard.py — Evolver Performance Tracking
Sir HazeClaw - 2026-04-11

Tracks evolver success metrics and detects stagnation.

Usage:
    python3 performance_dashboard.py              # Show dashboard
    python3 performance_dashboard.py --log ...    # Log evolution
    python3 performance_dashboard.py --check     # Check stagnation
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
EVOLVER_LOG = WORKSPACE / "data" / "evolvers" / "performance.json"

def load_performance():
    if EVOLVER_LOG.exists():
        with open(EVOLVER_LOG) as f:
            return json.load(f)
    return {
        "evolutions": [],
        "gene_usage": {},
        "stagnation_signals": []
    }

def save_performance(data):
    EVOLVER_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(EVOLVER_LOG, "w") as f:
        json.dump(data, f, indent=2)

def calculate_success_rate(data):
    """Calculate success rate."""
    evolutions = data.get("evolutions", [])
    if not evolutions:
        return 0, 0
    
    total = len(evolutions)
    successful = sum(1 for e in evolutions if e.get("success"))
    
    return (successful / total * 100), total

def check_stagnation(data):
    """Check for stagnation signals."""
    gene_usage = data.get("gene_usage", {})
    
    signals = []
    
    # Same gene used 5+ times
    for gene, count in gene_usage.items():
        if count >= 5:
            signals.append(f"SAME_GENE_REPEAT: {gene} used {count}x")
    
    # No new genes in 10 evolutions
    evolutions = data.get("evolutions", [])
    if len(evolutions) >= 10:
        recent_genes = set(e.get("gene") for e in evolutions[-10:])
        if len(recent_genes) <= 2:
            signals.append(f"LOW_DIVERSITY: Only {len(recent_genes)} genes in last 10")
    
    # Success rate dropped
    if len(evolutions) >= 5:
        recent_success = sum(1 for e in evolutions[-5:] if e.get("success"))
        if recent_success <= 1:
            signals.append("SUCCESS_RATE_DROP: <20% in last 5")
    
    return signals

def show_dashboard():
    """Show performance dashboard."""
    data = load_performance()
    evolutions = data.get("evolutions", [])
    gene_usage = data.get("gene_usage", {})
    
    print("📈 EVOLVER PERFORMANCE DASHBOARD")
    print("=" * 50)
    print()
    
    # Success rate
    success_rate, total = calculate_success_rate(data)
    print(f"📊 Success Rate: {success_rate:.1f}% ({total} evolutions)")
    
    # Gene diversity
    genes_used = len(gene_usage)
    if genes_used > 0:
        most_used = max(gene_usage.items(), key=lambda x: x[1])
        print(f"🧬 Gene Diversity: {genes_used} unique genes")
        print(f"   Most used: {most_used[0]} ({most_used[1]}x)")
    else:
        print("🧬 Gene Diversity: No data")
    print()
    
    # Stagnation check
    signals = check_stagnation(data)
    if signals:
        print("⚠️ STAGNATION SIGNALS:")
        for signal in signals:
            print(f"   - {signal}")
    else:
        print("✅ No stagnation signals")
    
    print()
    
    # Recent evolutions
    if evolutions:
        print("📋 Recent Evolutions:")
        for e in evolutions[-5:]:
            status = "✅" if e.get("success") else "❌"
            gene = e.get("gene", "unknown")
            date = e.get("date", "")[:10]
            print(f"   {status} {date}: {gene}")
    
    return success_rate, signals

def log_evolution(gene, success, blast_actual=None, blast_estimated=None):
    """Log an evolution result."""
    data = load_performance()
    
    entry = {
        "gene": gene,
        "success": success,
        "date": datetime.now().isoformat(),
        "blast_actual": blast_actual,
        "blast_estimated": blast_estimated
    }
    
    data["evolutions"].append(entry)
    data["evolutions"] = data["evolutions"][-50:]  # Keep last 50
    
    if gene not in data["gene_usage"]:
        data["gene_usage"][gene] = 0
    data["gene_usage"][gene] += 1
    
    save_performance(data)
    
    # Calculate blast accuracy if both provided
    if blast_actual and blast_estimated:
        ratio = blast_actual / blast_estimated if blast_estimated > 0 else 0
        print(f"📊 Blast Radius Accuracy: {ratio:.2f}x")
    
    print(f"✅ Evolution logged: {gene}")

def main():
    if "--log" in sys.argv:
        gene = success = blast_actual = blast_estimated = None
        for i, arg in enumerate(sys.argv):
            if arg == "--gene" and i + 1 < len(sys.argv):
                gene = sys.argv[i + 1]
            if arg == "--success" and i + 1 < len(sys.argv):
                success = sys.argv[i + 1].lower() == "true"
            if arg == "--blast_actual" and i + 1 < len(sys.argv):
                blast_actual = float(sys.argv[i + 1])
            if arg == "--blast_estimated" and i + 1 < len(sys.argv):
                blast_estimated = float(sys.argv[i + 1])
        
        if gene:
            log_evolution(gene, success, blast_actual, blast_estimated)
        return
    
    if "--check" in sys.argv:
        data = load_performance()
        signals = check_stagnation(data)
        if signals:
            print("⚠️ STAGNATION DETECTED:")
            for s in signals:
                print(f"   - {s}")
        else:
            print("✅ No stagnation")
        return
    
    # Default: show dashboard
    show_dashboard()

if __name__ == "__main__":
    main()
