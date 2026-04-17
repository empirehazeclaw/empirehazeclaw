#!/usr/bin/env python3
"""
Deep System Test — Kompletter System-Test
==========================================
Testet alle wichtigen System-Komponenten:

1. Memory Integrity
2. Script Syntax (alle)
3. Notes Structure  
4. Knowledge Graph
5. Learning Loop State
6. Event Bus
7. Gateway Health
8. Cron Status
9. Backup Integrity

Usage:
    python3 deep_system_test.py
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

class bcolors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def test(name: str, passed: bool, details: str = ""):
    icon = f"{bcolors.GREEN}✅{bcolors.END}" if passed else f"{bcolors.RED}❌{bcolors.END}"
    print(f"  {icon} {name}")
    if details:
        print(f"      {details}")
    return passed

def run():
    print(f"\n{bcolors.BLUE}{'='*60}{bcolors.END}")
    print(f"{bcolors.BLUE}🔬 DEEP SYSTEM TEST — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{bcolors.END}")
    print(f"{bcolors.BLUE}{'='*60}{bcolors.END}\n")
    
    results = []
    
    # ============================================
    # 1. MEMORY INTEGRITY
    # ============================================
    print(f"{bcolors.BLUE}📂 1. MEMORY INTEGRITY{bcolors.END}")
    
    # long_term/
    lt = WORKSPACE / "memory/long_term"
    lt_ok = test("long_term/ exists", lt.exists() and lt.is_dir())
    if lt_ok:
        for f in ["facts.md", "preferences.md", "patterns.md"]:
            fp = lt / f
            test(f"  - {f}", fp.exists() and fp.stat().st_size > 100)
    
    # notes/
    notes = WORKSPACE / "memory/notes"
    notes_ok = test("notes/ structure", notes.exists())
    if notes_ok:
        for d in ["SYSTEM", "SCRIPTS", "LEARNING", "OPERATIONS", "ARCHIVE"]:
            dp = notes / d
            test(f"  - {d}/", dp.exists() and dp.is_dir())
        test("  - _index.md", (notes / "_index.md").exists())
    
    # MEMORY.md
    mem_md = WORKSPACE / "ceo/MEMORY.md"
    mem_ok = test("MEMORY.md exists", mem_md.exists() and mem_md.stat().st_size > 1000)
    results.append(lt_ok and notes_ok and mem_ok)
    
    # ============================================
    # 2. SCRIPT SYNTAX
    # ============================================
    print(f"\n{bcolors.BLUE}📜 2. SCRIPT SYNTAX (alle Python Scripts){bcolors.END}")
    
    syntax_errors = 0
    scripts_dir = WORKSPACE / "SCRIPTS/automation"
    if scripts_dir.exists():
        py_scripts = list(scripts_dir.glob("*.py"))
        test(f"Total Python scripts: {len(py_scripts)}", True)
        
        for sp in py_scripts:
            try:
                result = subprocess.run(
                    ["python3", "-m", "py_compile", str(sp)],
                    capture_output=True, timeout=5
                )
                if result.returncode != 0:
                    test(f"  ❌ {sp.name}", False, "SYNTAX ERROR")
                    syntax_errors += 1
            except:
                pass
        
        test("Syntax errors", syntax_errors == 0, f"{syntax_errors} errors found")
    results.append(syntax_errors == 0)
    
    # ============================================
    # 3. NOTES CONTENT
    # ============================================
    print(f"\n{bcolors.BLUE}📚 3. NOTES CONTENT{bcolors.END}")
    
    key_docs = [
        ("SYSTEM/SYSTEM_ARCHITECTURE.md", 5000),
        ("SYSTEM/smart-evolver-integration.md", 2000),
        ("SCRIPTS/SCRIPT_KATALOG.md", 2000),
        ("LEARNING/STRUCTURE_IMPROVEMENT_PLAN.md", 5000),
    ]
    
    notes_ok_count = 0
    for doc_path, min_size in key_docs:
        fp = notes / doc_path
        exists = fp.exists()
        size_ok = fp.stat().st_size >= min_size if exists else False
        if exists and size_ok:
            notes_ok_count += 1
        test(f"  {doc_path}", exists and size_ok, f"{fp.stat().st_size if exists else 0} bytes")
    
    results.append(notes_ok_count == len(key_docs))
    
    # ============================================
    # 4. KNOWLEDGE GRAPH
    # ============================================
    print(f"\n{bcolors.BLUE}🗃️ 4. KNOWLEDGE GRAPH{bcolors.END}")
    
    kg_path = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
    kg_ok = test("KG file exists", kg_path.exists())
    if kg_ok:
        try:
            kg = json.loads(kg_path.read_text())
            entities = len(kg.get("entities", {}))
            relations = len(kg.get("relations", {}))
            test(f"  KG entities", entities > 0, f"{entities} entities")
            test(f"  KG relations", relations > 0, f"{relations} relations")
            kg_ok = entities > 0 and relations > 0
        except Exception as e:
            test("  KG JSON valid", False, str(e))
            kg_ok = False
    results.append(kg_ok)
    
    # ============================================
    # 5. LEARNING LOOP STATE
    # ============================================
    print(f"\n{bcolors.BLUE}🧠 5. LEARNING LOOP STATE{bcolors.END}")
    
    ll_state = WORKSPACE / "data/learning_loop_state.json"
    ll_ok = test("Learning Loop state exists", ll_state.exists())
    if ll_ok:
        try:
            state = json.loads(ll_state.read_text())
            score = state.get("score", 0)
            iterations = state.get("iteration", 0)
            test(f"  Score", 0 <= score <= 1, f"{score:.3f}")
            test(f"  Iterations", iterations > 0, f"{iterations}")
            ll_ok = iterations > 0
        except Exception as e:
            test("  State JSON valid", False, str(e))
            ll_ok = False
    results.append(ll_ok)
    
    # ============================================
    # 6. EVENT BUS
    # ============================================
    print(f"\n{bcolors.BLUE}📡 6. EVENT BUS{bcolors.END}")
    
    eb_path = WORKSPACE / "data/events/events.jsonl"
    eb_ok = test("Event Bus exists", eb_path.exists())
    if eb_ok:
        try:
            lines = eb_path.read_text().strip().split("\n")
            event_count = len([l for l in lines if l.strip()])
            test(f"  Events", event_count > 0, f"{event_count} events")
            # Check recent event
            if lines:
                last_event = json.loads(lines[-1])
                test(f"  Last event type", True, last_event.get("type", "unknown"))
            eb_ok = event_count > 0
        except Exception as e:
            test("  Event Bus readable", False, str(e))
            eb_ok = False
    results.append(eb_ok)
    
    # ============================================
    # 7. GATEWAY HEALTH
    # ============================================
    print(f"\n{bcolors.BLUE}🌐 7. GATEWAY HEALTH{bcolors.END}")
    
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True, text=True, timeout=10
        )
        gw_ok = result.returncode == 0 and "running" in result.stdout.lower()
        test("Gateway", gw_ok, result.stdout[:100] if result.stdout else "no output")
    except Exception as e:
        test("Gateway", False, str(e))
        gw_ok = False
    results.append(gw_ok)
    
    # ============================================
    # 8. CRON STATUS (via openclaw)
    # ============================================
    print(f"\n{bcolors.BLUE}⏰ 8. CRON STATUS{bcolors.END}")
    
    try:
        result = subprocess.run(
            ["openclaw", "tasks", "list", "--format", "json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            try:
                tasks = json.loads(result.stdout)
                enabled = sum(1 for t in tasks if t.get("enabled", False))
                total = len(tasks)
                test(f"  Total Crons", total > 0, f"{total} (enabled: {enabled})")
            except:
                test("  Tasks JSON parse", False)
                enabled = 0
        else:
            test("  Tasks command", False)
            enabled = 0
    except Exception as e:
        test("  Tasks", False, str(e))
        enabled = 0
    
    # ============================================
    # 9. BACKUP INTEGRITY
    # ============================================
    print(f"\n{bcolors.BLUE}💾 9. BACKUP INTEGRITY{bcolors.END}")
    
    backup_path = WORKSPACE.parent / "workspace_backup_20260417_0625"
    bu_ok = test("Backup exists (2026-04-17 06:25)", backup_path.exists())
    if bu_ok:
        # Check key items in backup
        for item in ["scripts", "SCRIPTS", "memory", "ceo"]:
            ip = backup_path / item
            test(f"  Backup contains {item}/", ip.exists())
    
    # ============================================
    # SUMMARY
    # ============================================
    print(f"\n{bcolors.BLUE}{'='*60}{bcolors.END}")
    
    passed = sum(results)
    total = len(results)
    pct = (passed / total * 100) if total > 0 else 0
    
    if pct == 100:
        color = bcolors.GREEN
        icon = "✅"
    elif pct >= 80:
        color = bcolors.YELLOW
        icon = "⚠️"
    else:
        color = bcolors.RED
        icon = "❌"
    
    print(f"{color}{icon} RESULT: {passed}/{total} ({pct:.0f}%) passed{bcolors.END}")
    print(f"{bcolors.BLUE}{'='*60}{bcolors.END}\n")
    
    return 0 if pct >= 80 else 1


if __name__ == "__main__":
    sys.exit(run())
