#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Proactive Scanner
Phase 2: Autonomy Supervisor Erweiterung

Prüft regelmäßig:
- Log-Patterns (Fehler, Warnings)
- KG-Wachstum (Stagnation, Orphan)
- Memory-Usage (Stale, orphan data)
- Cron-Performance (Timing issues)
- Learning Loop Score (Trend analysis)

Usage:
    python3 scanner.py              # Full scan
    python3 scanner.py --quick     # Quick checks only
    python3 scanner.py --dry-run   # Show what would be done
    python3 scanner.py --report    # JSON report
"""

import os
import sys
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data"
KG_DIR = WORKSPACE / "ceo" / "memory" / "kg"
MEMORY_DIR = WORKSPACE / "ceo" / "memory"
LOG_FILE = WORKSPACE / "logs" / "proactive_scanner.log"

# Thresholds
MAX_ERROR_RATE = 0.05  # 5% errors in recent logs
MAX_WARNING_RATE = 0.15  # 15% warnings
KG_ORPHAN_THRESHOLD = 0.30  # 30% orphans = issue
SCORE_DECLINE_THRESHOLD = 0.05  # 5% decline in 1h = concern
STALE_FILE_DAYS = 7  # Files not touched in 7 days

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def scan_logs() -> dict:
    """Scan recent logs for patterns."""
    findings = []
    error_count = 0
    warning_count = 0
    total_lines = 0
    
    # Scan last 24h of logs
    cutoff = datetime.now() - timedelta(hours=24)
    
    for log_file in LOG_DIR.glob("*.log"):
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff:
                continue
                
            with open(log_file) as f:
                for line in f:
                    total_lines += 1
                    if "[ERROR]" in line or "error" in line.lower():
                        error_count += 1
                    if "[WARN]" in line or "warning" in line.lower():
                        warning_count += 1
        except Exception as e:
            findings.append(f"LOG_SCAN_ERROR: {log_file.name}: {e}")
    
    if total_lines > 0:
        error_rate = error_count / total_lines
        warning_rate = warning_count / total_lines
        
        if error_rate > MAX_ERROR_RATE:
            findings.append(f"HIGH_ERROR_RATE: {error_rate:.2%} (threshold: {MAX_ERROR_RATE:.2%})")
        
        if warning_rate > MAX_WARNING_RATE:
            findings.append(f"HIGH_WARNING_RATE: {warning_rate:.2%} (threshold: {MAX_WARNING_RATE:.2%})")
    
    return {
        "status": "OK" if not findings else "FINDINGS",
        "errors": error_count,
        "warnings": warning_count,
        "findings": findings
    }

def scan_kg() -> dict:
    """Check KG health."""
    findings = []
    
    kg_file = KG_DIR / "knowledge_graph.json"
    if not kg_file.exists():
        return {"status": "NO_KG", "findings": ["KG file not found"]}
    
    try:
        with open(kg_file) as f:
            kg = json.load(f)
        
        entities = kg.get("entities", [])
        relations = kg.get("relations", [])
        
        if not entities:
            return {"status": "EMPTY_KG", "findings": ["KG has no entities"]}
        
        # Check orphan rate
        # entities is dict with entity names as keys
        entity_ids = set(entities.keys()) if isinstance(entities, dict) else set()
        connected = set()
        
        # Relations may be dict with 'from'/'to' (key is string index) or list with 'source'/'target'
        if isinstance(relations, dict):
            # Dict format: {'0': {'from': 'A', 'to': 'B'}, ...}
            for rel in relations.values():
                if isinstance(rel, dict):
                    if rel.get("from"):
                        connected.add(rel["from"])
                    if rel.get("to"):
                        connected.add(rel["to"])
        elif isinstance(relations, list):
            # List format: [{'source': 'A', 'target': 'B'}, ...]
            for rel in relations:
                if isinstance(rel, dict):
                    if rel.get("source"):
                        connected.add(rel["source"])
                    if rel.get("target"):
                        connected.add(rel["target"])
        
        orphan_count = len(entity_ids - connected)
        orphan_rate = orphan_count / len(entity_ids) if entity_ids else 0
        
        if orphan_rate > KG_ORPHAN_THRESHOLD:
            findings.append(f"HIGH_ORPHAN_RATE: {orphan_rate:.1%} ({orphan_count} orphans)")
        
        # Check entity count trend
        entity_count = len(entities)
        
        return {
            "status": "OK" if not findings else "FINDINGS",
            "entity_count": entity_count,
            "relation_count": len(relations),
            "orphan_rate": orphan_rate,
            "findings": findings
        }
    except Exception as e:
        return {"status": "ERROR", "findings": [f"KG_SCAN_ERROR: {e}"]}

def scan_memory() -> dict:
    """Check for stale/orphan memory files."""
    findings = []
    stale_files = []
    
    cutoff = datetime.now() - timedelta(days=STALE_FILE_DAYS)
    
    # Check short_term
    short_term = MEMORY_DIR / "short_term"
    if short_term.exists():
        for f in short_term.glob("*.md"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                stale_files.append(str(f.name))
    
    # Check temp files
    temp_dir = WORKSPACE / "TEMPORARY"
    if temp_dir.exists():
        for f in temp_dir.glob("**/*"):
            if f.is_file():
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                age_days = (datetime.now() - mtime).days
                if age_days > STALE_FILE_DAYS:
                    stale_files.append(f"OLD_TEMP: {f.name}")
    
    if stale_files:
        findings.append(f"STALE_FILES: {len(stale_files)} files older than {STALE_FILE_DAYS} days")
    
    return {
        "status": "OK" if not findings else "FINDINGS",
        "stale_count": len(stale_files),
        "findings": findings[:5]  # Limit to first 5
    }

def scan_crons() -> dict:
    """Check cron performance via logs."""
    findings = []
    
    # Check for cron errors in recent logs
    error_jobs = defaultdict(int)
    
    cutoff = datetime.now() - timedelta(hours=6)
    
    for log_file in LOG_DIR.glob("*.log"):
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff:
                continue
                
            with open(log_file) as f:
                content = f.read()
                if "error" in content.lower() or "failed" in content.lower():
                    # Try to extract job name from log
                    for line in content.split("\n"):
                        if "error" in line.lower() and "cron" in line.lower():
                            # Check if line timestamp is recent (within cutoff)
                            try:
                                # Format: [2026-04-17 02:02:57]
                                ts_str = line.split("]")[0].replace("[", "")
                                line_time = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                                if line_time >= cutoff:
                                    findings.append(f"CRON_ERROR: {line[:100]}")
                            except:
                                # If can't parse timestamp, only include if file is recent
                                if mtime >= cutoff:
                                    findings.append(f"CRON_ERROR: {line[:100]}")
        except:
            pass
    
    return {
        "status": "OK" if not findings else "FINDINGS",
        "findings": findings[:3]  # Limit to 3
    }

def scan_learning() -> dict:
    """Check learning loop score trend."""
    findings = []
    
    # Read recent learning loop log
    log_file = LOG_DIR / "learning_core.log"
    if not log_file.exists():
        return {"status": "UNKNOWN", "findings": ["No learning log found"]}
    
    try:
        lines = []
        with open(log_file) as f:
            lines = f.readlines()
        
        # Get last 5 scores if available
        scores = []
        for line in lines[-20:]:
            if "Score:" in line or "score" in line.lower():
                try:
                    # Try to extract score
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if "score" in p.lower() and i+1 < len(parts):
                            scores.append(float(parts[i+1].replace(",", "")))
                except:
                    pass
        
        if len(scores) >= 2:
            recent_avg = sum(scores[-3:]) / min(3, len(scores))
            older_avg = sum(scores[:3]) / min(3, len(scores))
            
            if older_avg > 0:
                decline = (older_avg - recent_avg) / older_avg
                if decline > SCORE_DECLINE_THRESHOLD:
                    findings.append(f"SCORE_DECLINE: {decline:.1%} decline detected")
        
        return {
            "status": "OK" if not findings else "FINDINGS",
            "recent_scores": scores[-5:] if scores else [],
            "findings": findings
        }
    except Exception as e:
        return {"status": "ERROR", "findings": [f"LEARNING_SCAN_ERROR: {e}"]}

def main():
    mode = "full"
    if "--quick" in sys.argv:
        mode = "quick"
    elif "--dry-run" in sys.argv:
        mode = "dry-run"
    elif "--report" in sys.argv:
        mode = "report"
    
    log("Proactive Scanner START", "INFO")
    
    results = {}
    
    # Run all scans
    if mode in ["full", "quick"]:
        results["logs"] = scan_logs()
        results["kg"] = scan_kg()
        results["memory"] = scan_memory()
        
        if mode == "full":
            results["crons"] = scan_crons()
            results["learning"] = scan_learning()
    
    # Aggregate findings
    all_findings = []
    for key, val in results.items():
        if isinstance(val, dict) and "findings" in val:
            all_findings.extend(val.get("findings", []))
    
    status = "CLEAN" if not all_findings else f"ISSUES({len(all_findings)})"
    
    log(f"Proactive Scanner END: {status}", "INFO")
    
    if mode == "report":
        print(json.dumps({"status": status, "results": results, "findings": all_findings}, indent=2))
    elif mode == "dry-run":
        print(f"Would report: {status}")
        for f in all_findings[:5]:
            print(f"  - {f}")
    else:
        if all_findings:
            print(f"🔍 PROACTIVE SCAN: {status}")
            for f in all_findings[:5]:
                print(f"  ⚠️ {f}")
        else:
            print(f"✅ PROACTIVE SCAN: All clean")
    
    return 0 if not all_findings else 1

if __name__ == "__main__":
    sys.exit(main())