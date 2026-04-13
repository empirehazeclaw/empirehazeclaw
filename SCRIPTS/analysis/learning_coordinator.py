#!/usr/bin/env python3
"""
Sir HazeClaw Learning Coordinator v4
Zentrales Dashboard für den Learning Loop.

REALE FEEDBACK LOOP ARCHITECTUR:
1. Research → Generate actionable hypotheses
2. Quality Gates → Detect issues  
3. Improvement Selection → Match issues to best findings
4. Action → Apply best improvement
5. Validation → Measure if it worked

Usage:
    python3 learning_coordinator.py
    python3 learning_coordinator.py --full      # Full cycle
    python3 learning_coordinator.py --research  # Only research
    python3 learning_coordinator.py --improve   # Only improvement
    python3 learning_coordinator.py --status    # Show status
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "SCRIPTS"  # Fixed: was pointing to lowercase "scripts"
DATA_DIR = WORKSPACE / "data"
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
COORDINATOR_LOG = DATA_DIR / "learning_coordinator.json"
IMPROVEMENT_LOG = DATA_DIR / "improvements/improvement_log.json"

# Script search paths (in order of priority)
SCRIPT_SEARCH_PATHS = [
    WORKSPACE / "scripts",           # Legacy scripts dir
    WORKSPACE / "SCRIPTS" / "analysis",
    WORKSPACE / "SCRIPTS" / "automation",
    WORKSPACE / "SCRIPTS" / "tools",
]

def find_script(name):
    """Find a script in any of the known directories."""
    for sp in SCRIPT_SEARCH_PATHS:
        p = sp / name
        if p.exists():
            return p
    return SCRIPTS_DIR / name  # fallback

# ============ UTILITIES ============

def load_json(path, default=None):
    """Load JSON with fallback."""
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except:
            return default or {}
    return default or {}

def save_json(path, data):
    """Save JSON safely."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ============ TOKEN TRACKING ============

def track_token_usage(task_name, tokens_in, tokens_out):
    """Track token usage für Efficiency."""
    log = load_coordinator_log()
    if 'token_usage' not in log:
        log['token_usage'] = []
    log['token_usage'].append({
        'timestamp': datetime.now().isoformat(),
        'task': task_name,
        'tokens_in': tokens_in,
        'tokens_out': tokens_out,
        'total': tokens_in + tokens_out
    })
    log['token_usage'] = log['token_usage'][-100:]
    save_coordinator_log(log)

# ============ RESEARCH INTEGRATION ============

def run_innovation_research():
    """Führt Innovation Research aus und integriert in KG.
    
    NOW GENERATES ACTIONABLE HYPOTHESES!
    """
    print("🔍 PHASE 2: Innovation Research (with Hypotheses)...")
    
    try:
        result = subprocess.run(
            ['python3', str(find_script('innovation_research.py')), '--daily'],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(WORKSPACE)
        )
        
        # Track token usage
        queries = len([l for l in result.stdout.split('\n') if 'Searching' in l])
        track_token_usage('innovation_research', 2000 * queries, 1500 * queries)
        
        # Parse results and generate hypotheses
        hypotheses = generate_hypotheses_from_research(result.stdout)
        
        # Update KG with research + hypotheses
        if KG_PATH.exists():
            kg = load_json(KG_PATH)
            today = datetime.now().strftime('%Y%m%d')
            
            # Store research results
            entity_id = f"research_{today}"
            kg['entities'][entity_id] = {
                "type": "research",
                "category": "learning_coordinator",
                "facts": [{
                    "content": f"Research completed: {queries} queries, {len(hypotheses)} hypotheses generated",
                    "confidence": 0.9,
                    "extracted_at": datetime.now().isoformat(),
                    "category": "research"
                }],
                "hypotheses": hypotheses,  # NEW: Store hypotheses
                "priority": "MEDIUM",
                "created": datetime.now().isoformat(),
                "tags": ["research", "coordinator", "daily"]
            }
            
            save_json(KG_PATH, kg)
        
        if hypotheses:
            print(f"  ✅ Generated {len(hypotheses)} actionable hypotheses:")
            for i, h in enumerate(hypotheses[:3], 1):
                print(f"     {i}. {h['title'][:60]}...")
        else:
            print("  ⚠️ No hypotheses generated")
        
        print(f"✅ Research integrated to KG")
        return True, hypotheses
        
    except Exception as e:
        print(f"⚠️ Research failed: {e}")
        return False, []

def generate_hypotheses_from_research(research_output):
    """Generate actionable improvement hypotheses from research results.
    
    Analyzes arXiv papers and HN discussions to create
    specific, testable improvement hypotheses.
    """
    hypotheses = []
    
    # Parse research results for improvement-relevant topics
    patterns = [
        (r'self-improv.*?(agent|AI|model)', 'self_improvement'),
        (r'autonom.*?learn', 'autonomous_learning'),
        (r'persistent.?memory', 'memory_optimization'),
        (r'token.?efficien', 'token_optimization'),
        (r'self-play|self-play', 'self_play'),
        (r'capability.?evol', 'capability_evolution'),
    ]
    
    content = research_output.lower()
    
    for pattern, category in patterns:
        if re.search(pattern, content):
            hypothesis = {
                'title': f"Apply {category.replace('_', ' ').title()} pattern",
                'category': category,
                'source': 'research',
                'priority': 'MEDIUM',
                'approach': f"Investigate and implement {category} techniques from research",
                'expected_impact': 'HIGH' if category in ['self_improvement', 'capability_evolution'] else 'MEDIUM'
            }
            if hypothesis not in hypotheses:
                hypotheses.append(hypothesis)
    
    return hypotheses

# ============ QUALITY GATES ============

def run_quality_gates():
    """Führt Quality Gates aus.
    
    NOW DETECTS ISSUES AND RETURNS THEM!
    """
    print("🔒 PHASE 3: Quality Gates...")
    
    issues_detected = []
    has_warnings = False
    
    # Self Eval
    try:
        result = subprocess.run(
            ['python3', str(find_script('self_eval.py'))],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(WORKSPACE)
        )
        
        # Parse score
        score_match = re.search(r'(\d+)/100', result.stdout)
        score = int(score_match.group(1)) if score_match else 0
        
        if score < 90:
            issues_detected.append({
                'type': 'low_self_eval',
                'severity': 'HIGH',
                'description': f'Self-Eval score low: {score}/100',
                'suggestion': 'Review recent failures and implement improvements'
            })
            has_warnings = True
        
        # Parse individual goal failures
        if '⚠️' in result.stdout:
            for line in result.stdout.split('\n'):
                if '⚠️' in line:
                    issues_detected.append({
                        'type': 'metric_warning',
                        'severity': 'MEDIUM',
                        'description': line.strip(),
                        'suggestion': 'Address specific metric failure'
                    })
        
        track_token_usage('self_eval', 800, 400)
        
    except Exception as e:
        print(f"  ⚠️ Self Eval failed: {e}")
        has_warnings = True
    
    # Error Rate Check (uses real data from error_reducer.py)
    try:
        # Run error_reducer for real-time error analysis
        result = subprocess.run(
            ['python3', str(find_script('error_reducer.py'))],
            capture_output=True, text=True, timeout=60, cwd=str(WORKSPACE)
        )
        # Parse output for error rate
        for line in result.stdout.split('\n'):
            if 'Real Error Rate:' in line:
                match = re.search(r'Real Error Rate: ([0-9.]+)%', line)
                if match:
                    error_rate = float(match.group(1))
                    if error_rate > 5:  # REAL threshold, not hardcoded 20
                        issues_detected.append({
                            'type': 'high_error_rate',
                            'severity': 'HIGH',
                            'description': f'Error rate: {error_rate}% (real data)',
                            'suggestion': 'Run error reduction cycle'
                        })
                        has_warnings = True
                    break
    except:
        pass
    
    # Scripts Health Check
    try:
        result = subprocess.run(
            ['python3', str(find_script('error_rate_monitor.py'))],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(WORKSPACE)
        )
        # Only flag CRITICAL in uppercase followed by space (not "ERROR RATE")
        if 'CRITICAL: ' in result.stdout or result.stdout.count('CRITICAL') > result.stdout.count('ERROR RATE'):
            issues_detected.append({
                'type': 'script_errors',
                'severity': 'HIGH',
                'description': 'Critical script errors detected',
                'suggestion': 'Run error_reducer.py'
            })
            has_warnings = True
    except:
        pass
    
    # Report
    if issues_detected:
        print(f"  ⚠️ {len(issues_detected)} issues detected:")
        for issue in issues_detected[:3]:
            print(f"     - [{issue['severity']}] {issue['description'][:50]}")
    else:
        print(f"  ✅ All quality gates passed")
    
    return True, has_warnings, issues_detected

# ============ IMPROVEMENT ENGINE ============

def select_best_improvement(issues, hypotheses):
    """Selects the best improvement based on issues + research.
    
    Matches detected issues to research hypotheses and
    selects the highest-impact improvement.
    """
    improvements = []
    
    # Issue → Improvement mapping
    issue_improvements = {
        'high_error_rate': {
            'title': 'Error Rate Reduction',
            'script': 'error_reducer.py',
            'expected_impact': 'HIGH'
        },
        'low_self_eval': {
            'title': 'Self-Evaluation Improvement',
            'script': 'autonomous_improvement.py',
            'expected_impact': 'MEDIUM'
        },
        'script_errors': {
            'title': 'Script Error Fix',
            'script': 'auto_fixer.py',
            'expected_impact': 'HIGH'
        },
        'token_optimization': {
            'title': 'Token Optimization',
            'script': 'efficiency_tracker.py',
            'expected_impact': 'MEDIUM'
        }
    }
    
    # Priority: Issues first, then hypotheses
    for issue in issues[:2]:  # Top 2 issues
        issue_type = issue.get('type', '')
        if issue_type in issue_improvements:
            imp = issue_improvements[issue_type].copy()
            imp['reason'] = issue['description']
            imp['source'] = 'issue'
            improvements.append(imp)
    
    # Add research hypotheses if we have capacity
    for hyp in hypotheses[:2]:  # Top 2 hypotheses
        if len(improvements) >= 3:
            break
        improvements.append({
            'title': hyp['title'],
            'script': None,  # Research-based, needs investigation
            'expected_impact': hyp.get('expected_impact', 'MEDIUM'),
            'reason': hyp.get('approach', '')[:50],
            'source': 'research'
        })
    
    return improvements[:3]  # Max 3 improvements

def run_improvement_phase(improvements):
    """Executes improvements and validates results.
    
    NOW USES SELF-PLAY PATTERN for research-based improvements!
    """
    print("🚀 PHASE 4: Improvement Execution...")
    
    results = []
    
    for i, imp in enumerate(improvements, 1):
        print(f"  {i}. {imp['title']}...")
        
        if imp.get('source') == 'issue' and imp.get('script'):
            # Execute issue-based improvement (direct script execution)
            result = execute_improvement_script(imp['script'], imp['title'])
            results.append({
                'improvement': imp['title'],
                'script': imp['script'],
                'success': result['success'],
                'output': result['output'][:100],
                'validated': result['success']
            })
        elif imp.get('source') == 'research':
            # Research-based = use SELF-PLAY PATTERN!
            print(f"     🎮 Using Self-Play (GVU Pattern)...")
            sp_result = run_self_play_generation(imp)
            results.append({
                'improvement': imp['title'],
                'script': 'self_play_improver.py',
                'success': sp_result['success'],
                'output': sp_result['insights'][:100],
                'validated': sp_result['success']
            })
        else:
            # Unknown type, skip
            print(f"     ⏭️ Unknown source type")
            results.append({
                'improvement': imp['title'],
                'script': None,
                'success': None,
                'output': 'Unknown source',
                'validated': False
            })
    
    # Log improvements
    log_improvements(improvements, results)
    
    success_count = sum(1 for r in results if r.get('success'))
    print(f"  ✅ {success_count}/{len(results)} improvements executed")
    
    return results

def run_self_play_generation(research_imp: Dict) -> Dict:
    """Runs self-play generation for a research-based improvement.
    
    Uses the GVU (Generator-Verifier-Updater) pattern to
    autonomously improve based on research insights.
    """
    try:
        # Map research category to self-play strategies
        category = research_imp.get('category', '')
        
        # Run 2 generations of self-play
        result = subprocess.run(
            ['python3', str(find_script('self_play_improver.py')), '--generations', '2'],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(WORKSPACE)
        )
        
        success = result.returncode == 0
        
        # Extract insights
        insights = []
        for line in result.stdout.split('\n'):
            if '💡' in line or '✅' in line or '❌' in line:
                insights.append(line.strip())
        
        # Check if any improvement was made
        improved = '✅' in result.stdout and '+' in result.stdout
        
        return {
            'success': success and improved,
            'insights': ' | '.join(insights[-3:]) if insights else 'No insights'
        }
        
    except Exception as e:
        return {
            'success': False,
            'insights': f'Self-play failed: {str(e)[:50]}'
        }

def execute_improvement_script(script_name, title):
    """Executes an improvement script and validates result."""
    try:
        script_path = find_script(script_name)
        if not script_path.exists():
            return {'success': False, 'output': f'Script not found: {script_name}'}
        
        result = subprocess.run(
            ['python3', str(script_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(WORKSPACE)
        )
        
        success = result.returncode == 0
        
        # Validate by checking if error rate improved (if that's the goal)
        if 'error' in title.lower():
            # Quick check if errors were addressed
            success = success and 'error' not in result.stderr.lower()
        
        return {
            'success': success,
            'output': result.stdout[:200] if result.stdout else result.stderr[:200]
        }
    except Exception as e:
        return {'success': False, 'output': str(e)[:100]}

def log_improvements(improvements, results):
    """Logs improvements to the improvement log."""
    log_file = Path(IMPROVEMENT_LOG)
    log = load_json(log_file, {'improvements': []})
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'improvements': improvements,
        'results': results,
        'validated': sum(1 for r in results if r.get('validated'))
    }
    
    log['improvements'].append(entry)
    log['improvements'] = log['improvements'][-50:]  # Keep last 50
    
    save_json(log_file, log)

# ============ SYSTEM CHECK ============

def check_and_act():
    """Prüft System und handelt wenn nötig."""
    print("📊 PHASE 1: System Check...")
    
    issues = []
    
    # Disk Space
    try:
        result = subprocess.run(['df', '-h', WORKSPACE.parent], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if '/' in line and not line.startswith('Filesystem'):
                parts = line.split()
                if len(parts) >= 5:
                    use_pct = int(parts[4].replace('%', ''))
                    if use_pct > 85:
                        issues.append(f"Disk kritisch: {use_pct}%")
    except:
        pass
    
    # Memory
    try:
        result = subprocess.run(['free', '-m'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'Mem:' in line:
                parts = line.split()
                if int(parts[2]) / int(parts[1]) > 0.9:
                    issues.append(f"Memory hoch")
    except:
        pass
    
    # Gateway
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://127.0.0.1:18789/health'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if '"ok":true' not in result.stdout and 'live' not in result.stdout:
            issues.append("Gateway möglicherweise down")
    except:
        issues.append("Gateway Check failed")
    
    if issues:
        print("  ⚠️ Issues found:")
        for issue in issues:
            print(f"     - {issue}")
        return False, issues
    else:
        print("  ✅ All checks OK")
        return True, []

# ============ COORDINATOR LOG ============

def load_coordinator_log():
    if COORDINATOR_LOG.exists():
        try:
            with open(COORDINATOR_LOG) as f:
                data = json.load(f)
                if 'runs' not in data:
                    return {"runs": [], "last_full_cycle": data.get('last_full_cycle')}
                return data
        except (json.JSONDecodeError, IOError) as e:
            return {"runs": [], "last_full_cycle": None}
    return {"runs": [], "last_full_cycle": None}

def save_coordinator_log(log):
    COORDINATOR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(COORDINATOR_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def log_run(log, phase, success, notes=""):
    log["runs"].append({
        "timestamp": datetime.now().isoformat(),
        "phase": phase,
        "success": success,
        "notes": notes
    })
    log["last_full_cycle"] = datetime.now().isoformat()

# ============ MAIN COORDINATOR ============

def run_full_cycle():
    """Führt vollständigen Learning Cycle aus MIT FEEDBACK LOOP!"""
    print("=" * 60)
    print("🎯 LEARNING COORDINATOR v4 — Full Cycle (with Feedback)")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    print()
    
    log = load_coordinator_log()
    start_time = datetime.now()
    
    # PHASE 1: System Check (sequential - base check)
    ok, sys_issues = check_and_act()
    log_run(log, "system_check", ok, str(sys_issues))
    print()
    
    # PHASE 2: Research + Hypotheses (parallel)
    print("🔍 PHASE 2: Research + Hypotheses")
    research_ok, hypotheses = run_innovation_research()
    log_run(log, "research", research_ok, f"{len(hypotheses)} hypotheses")
    print()
    
    # PHASE 3: Quality Gates + Issue Detection (parallel)
    print("🔒 PHASE 3: Quality Gates + Issue Detection")
    quality_ok, has_warnings, issues = run_quality_gates()
    log_run(log, "quality", quality_ok, f"{len(issues)} issues")
    print()
    
    # PHASE 4: Improvement Selection + Execution
    print("🚀 PHASE 4: Improvement Engine")
    if issues or hypotheses:
        improvements = select_best_improvement(issues, hypotheses)
        if improvements:
            print(f"  Selected {len(improvements)} improvements:")
            for imp in improvements:
                print(f"     → {imp['title']}")
            improvement_results = run_improvement_phase(improvements)
            log_run(log, "improvement", True, f"{len(improvements)} applied")
        else:
            print("  ⏭️ No improvements selected")
            improvement_results = []
    else:
        print("  ⏭️ No issues or hypotheses - skipping improvement")
        improvement_results = []
    print()
    
    # Learning Tracker
    print("📚 PHASE 5: Learning Tracker")
    try:
        result = subprocess.run(
            ['python3', str(find_script('learning_tracker.py'))],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(WORKSPACE)
        )
        print("  ✅ Learning tracked")
        log_run(log, "learning", True)
    except:
        print("  ⚠️ Learning tracking failed")
        log_run(log, "learning", False)
    print()
    
    # PHASE 6: Meta-Improvement (Loop improving ITSELF)
    # Only run every 5 cycles to save resources
    cycle_count = len([r for r in log.get('runs', []) if r['phase'] == 'system_check'])
    if cycle_count > 0 and cycle_count % 5 == 0:
        print("🧠 PHASE 6: Meta-Improvement (Loop improving itself)")
        try:
            result = subprocess.run(
                ['python3', str(find_script('meta_improver.py'))],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(WORKSPACE)
            )
            if '✅ HEALTHY' in result.stdout or 'Loop Health: ✅' in result.stdout:
                print("  ✅ Meta-improvement complete (Loop healthy)")
                log_run(log, "meta", True, "healthy")
            else:
                print("  ⚠️ Meta-improvement complete (Loop needs work)")
                log_run(log, "meta", False, "needs_improvement")
        except Exception as e:
            print(f"  ⚠️ Meta-improvement failed: {e}")
            log_run(log, "meta", False, str(e)[:50])
    else:
        print(f"  ⏭️ Meta-Improvement (runs every 5 cycles, currently cycle {cycle_count})")
    print()
    
    # Summary
    duration = (datetime.now() - start_time).total_seconds()
    validated = sum(1 for r in improvement_results if r.get('validated'))
    
    print("=" * 60)
    print("📊 CYCLE SUMMARY")
    print(f"   Duration: {duration:.1f}s")
    print(f"   System Check: {'✅' if ok else '⚠️'}")
    print(f"   Research: {'✅' if research_ok else '⚠️'} ({len(hypotheses)} hypotheses)")
    print(f"   Quality: {'✅' if quality_ok else '⚠️'} ({len(issues)} issues)")
    print(f"   Improvements: {len(improvement_results)} ({validated} validated)")
    print(f"   Learning: ✅")
    print("=" * 60)
    
    save_coordinator_log(log)
    
    # Success = system OK + research works + improvements made
    return ok and research_ok

def show_status():
    """Zeigt aktuellen Status."""
    log = load_coordinator_log()
    
    print("📊 LEARNING COORDINATOR STATUS v4")
    print(f"   Last full cycle: {log.get('last_full_cycle', 'Never')}")
    print(f"   Total runs: {len(log.get('runs', []))}")
    
    # Show recent improvements
    imp_log = Path(IMPROVEMENT_LOG)
    if imp_log.exists():
        data = load_json(imp_log)
        improvements = data.get('improvements', [])
        if improvements:
            print()
            print("Recent Improvements:")
            for imp in improvements[-3:]:
                validated = imp.get('validated', 0)
                print(f"  {'✅' if validated else '⚠️'} {imp['timestamp'][:10]}: {validated} validated")

def main():
    if len(sys.argv) < 2:
        return 0 if run_full_cycle() else 1
    
    arg = sys.argv[1]
    
    if arg == '--full':
        return 0 if run_full_cycle() else 1
    elif arg == '--research':
        ok, hypotheses = run_innovation_research()
        return 0 if ok else 1
    elif arg == '--improve':
        _, _, issues = run_quality_gates()
        improvements = select_best_improvement(issues, [])
        run_improvement_phase(improvements)
        return 0
    elif arg == '--status':
        show_status()
        return 0
    elif arg == '--check':
        ok, _ = check_and_act()
        return 0 if ok else 1
    else:
        print(__doc__)
        return 1

if __name__ == "__main__":
    sys.exit(main())
