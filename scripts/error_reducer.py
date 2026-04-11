#!/usr/bin/env python3
"""
error_reducer.py — Real Error Analysis from Session Data
Sir HazeClaw - 2026-04-11

Parst echte Session-Daten und berechnet aktuelle Error-Rate.
VERFEINERT: Reduziert False Positives durch präzisere Pattern.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SESSION_DIR = Path("/home/clawbot/.openclaw/agents/ceo/sessions")
LOG_FILE = WORKSPACE / "logs" / "error_reducer.log"
METRICS_FILE = WORKSPACE / "memory" / "session_metrics_history.json"

def log(msg):
    """Log Nachricht."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def is_real_error(entry):
    """Prüft ob ein Entry einen echten Error enthält."""
    if entry.get('type') == 'message':
        msg = entry.get('message', {})
        
        # Check if it's a toolResult with embedded JSON error
        if msg.get('role') == 'toolResult':
            content = msg.get('content', [])
            if isinstance(content, list) and len(content) > 0:
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text = item.get('text', '')
                        if text.strip().startswith('{'):
                            try:
                                parsed = json.loads(text)
                                if parsed.get('status') == 'error':
                                    return True
                            except:
                                pass
        
        # Also check details.status for direct errors
        content = msg.get('content', [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'toolResult':
                    details = item.get('details', {})
                    if details.get('status') in ['error', 'failed']:
                        return True
    return False

def extract_error_info(entry):
    """Extrahiert Error-Informationen aus einem Entry."""
    info = {
        'tool': 'unknown',
        'error': '',
        'category': 'unknown'
    }
    
    if entry.get('type') == 'message':
        msg = entry.get('message', {})
        
        # Check embedded JSON error first
        if msg.get('role') == 'toolResult':
            content = msg.get('content', [])
            if isinstance(content, list) and len(content) > 0:
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text = item.get('text', '')
                        if text.strip().startswith('{'):
                            try:
                                parsed = json.loads(text)
                                if parsed.get('status') == 'error':
                                    info['tool'] = parsed.get('tool', 'unknown')
                                    info['error'] = parsed.get('error', '')
                                    return info
                            except:
                                pass
        
        # Fallback to old format
        content = msg.get('content', [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'toolResult':
                    details = item.get('details', {})
                    info['tool'] = item.get('toolName', 'unknown')
                    info['error'] = details.get('error', '') or details.get('aggregated', '')
                    break
    
    return info

def categorize_error(error_text, tool_name):
    """Kategorisiert einen echten Error präzise."""
    
    # Präzise Patterns - nur echte Errors
    patterns = {
        'timeout': [
            (r'Command.*timed out', 'timeout'),
            (r'Subprocess.*timed out', 'timeout'),
            (r'exec.*timeout.*exceeded', 'timeout'),
            (r'timeout.*exceeded', 'timeout'),
        ],
        'not_found': [
            (r'No such file', 'not_found'),
            (r'Cannot find', 'not_found'),
            (r'not found', 'not_found'),
            (r'ENOENT', 'not_found'),
            (r'Path.*does not exist', 'not_found'),
        ],
        'permission': [
            (r'Permission denied', 'permission'),
            (r'EACCES', 'permission'),
            (r'Access denied', 'permission'),
        ],
        'exec_error': [
            (r'exec preflight.*detected', 'exec_error'),
            (r'complex interpreter invocation', 'exec_error'),
            (r'Command not found', 'exec_error'),
            (r'python.*command not found', 'exec_error'),
        ],
        'json_error': [
            (r'JSONDecodeError', 'json_error'),
            (r'Unexpected token', 'json_error'),
            (r'invalid json', 'json_error'),
        ],
        'validation_error': [
            (r'AssertionError', 'validation_error'),
            (r'Test.*failed', 'validation_error'),
            (r'validation.*failed', 'validation_error'),
        ],
        'syntax_error': [
            (r'SyntaxError', 'syntax_error'),
            (r'syntax error', 'syntax_error'),
            (r'ParseError', 'syntax_error'),
        ],
        'crash': [
            (r'SIGSEGV', 'crash'),
            (r'SIGABRT', 'crash'),
            (r'Signal.*killed', 'crash'),
            (r'Killed.*signal', 'crash'),
        ],
    }
    
    error_lower = error_text.lower()
    
    # Prüfe Patterns
    for category, pattern_list in patterns.items():
        for pattern, _ in pattern_list:
            if re.search(pattern, error_text, re.IGNORECASE):
                return category
    
    # Fallback: generische Fehler erkennen
    if 'error' in error_lower or 'failed' in error_lower:
        #_exec preflight ist ein häufiger exec Fehler
        if 'preflight' in error_lower:
            return 'exec_error'
        if 'timeout' in error_lower:
            return 'timeout'
        if 'not found' in error_lower:
            return 'not_found'
        if 'permission' in error_lower:
            return 'permission'
        if 'json' in error_lower:
            return 'json_error'
        if 'exception' in error_lower:
            return 'exception'
    
    return 'unknown'

def parse_sessions(sessions):
    """Parse alle Sessions und sammle echte Error-Daten."""
    real_errors = []
    
    for session_file in sessions:
        try:
            with open(session_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        if is_real_error(entry):
                            info = extract_error_info(entry)
                            if info['error']:
                                real_errors.append(info)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            log(f"Error parsing {session_file}: {e}")
    
    return real_errors

def calculate_error_rate(sessions, real_errors):
    """Berechnet echte Error-Rate."""
    total_messages = 0
    
    for session_file in sessions:
        try:
            with open(session_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get('type') == 'message':
                            total_messages += 1
                    except:
                        pass
        except:
            pass
    
    if total_messages > 0:
        return (len(real_errors) / total_messages) * 100, len(real_errors), total_messages
    return 0.0, 0, 0

def main():
    print("🔍 ERROR REDUCER — Real Error Analysis (v2)")
    print("=" * 50)
    
    # Load recent sessions
    print("\n📊 Loading recent sessions...")
    sessions = list(SESSION_DIR.glob("*.jsonl"))
    print(f"   Total sessions: {len(sessions)}")
    
    # Parse and find real errors
    print("\n🔍 Analyzing errors...")
    real_errors = parse_sessions(sessions)
    
    # Calculate error rate
    error_rate, error_count, msg_count = calculate_error_rate(sessions, real_errors)
    
    print(f"\n📈 Real Error Rate: {error_rate:.2f}%")
    print(f"   Total real errors: {error_count}")
    print(f"   Total messages: {msg_count}")
    
    # Categorize errors
    categorized = defaultdict(lambda: {'count': 0, 'examples': []})
    for err in real_errors:
        cat = categorize_error(err['error'], err['tool'])
        categorized[cat]['count'] += 1
        if len(categorized[cat]['examples']) < 3:
            categorized[cat]['examples'].append(err['error'][:80])
    
    print(f"\n🚨 Error Breakdown:")
    for category, data in sorted(categorized.items(), key=lambda x: x[1]['count'], reverse=True):
        if data['count'] > 0:
            pct = (data['count'] / error_count * 100) if error_count > 0 else 0
            print(f"   {category}: {data['count']} ({pct:.1f}%)")
            for ex in data.get('examples', [])[:2]:
                print(f"      → {ex}")
    
    # Top tools with errors
    tools = defaultdict(int)
    for err in real_errors:
        tools[err['tool']] += 1
    
    if tools:
        print(f"\n🔧 Top Error Tools:")
        for tool, count in sorted(tools.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {tool}: {count}")
    
    # Update metrics file
    try:
        metrics = {"history": []}
        if METRICS_FILE.exists():
            with open(METRICS_FILE, 'r') as f:
                metrics = json.load(f)
        
        metrics["history"].append({
            "timestamp": datetime.now().isoformat(),
            "error_rate": round(error_rate, 2),
            "error_count": error_count,
            "msg_count": msg_count
        })
        
        # Keep only last 100 entries
        metrics["history"] = metrics["history"][-100:]
        
        METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(METRICS_FILE, 'w') as f:
            json.dump(metrics, f, indent=2)
    except Exception as e:
        log(f"Error updating metrics: {e}")
    
    print(f"\n✅ Analysis complete")
    return error_rate

if __name__ == "__main__":
    main()
