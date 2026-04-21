#!/usr/bin/env python3
"""
Anomaly Detector — Sir HazeClaw Monitoring
==========================================
Proaktive Anomalie-Erkennung für alle CEO-Systeme.

Trackt:
  - Token Usage Burst (stündlich)
  - API Response Time Degradation
  - Session Creation Rate
  - KG Growth Stagnation
  - Event Diversity / Famine
  - Cron Error Rate Spike

Usage:
    python3 anomaly_detector.py --check all
    python3 anomaly_detector.py --check token_burst
    python3 anomaly_detector.py --report

Phase 3 of System Optimization Plan
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data"
MEMORY_DIR = WORKSPACE / "ceo/memory"
OUTPUT_FILE = DATA_DIR / "anomaly_detector_state.json"
KG_FILE = MEMORY_DIR / "kg/knowledge_graph.json"
EVENT_FILE = DATA_DIR / "events/events.jsonl"
CRON_STATE_FILE = DATA_DIR / "cron_monitor_state.json"


def load_state() -> dict:
    """Load or initialize state file."""
    if OUTPUT_FILE.exists():
        return json.load(open(OUTPUT_FILE))
    return {"checks": {}, "alerts": [], "last_run": None}


def save_state(state: dict):
    """Save state to file."""
    state["last_run"] = datetime.utcnow().isoformat() + "Z"
    with open(OUTPUT_FILE, "w") as f:
        json.dump(state, f, indent=2)


def check_token_burst(state: dict) -> dict:
    """
    Token Usage Burst Detection.
    
    Alert wenn:
    - Token-Verbrauch in einer Stunde > 2x Durchschnitt
    - Oder > 500k Tokens in einer Stunde
    """
    result = {"anomaly": False, "severity": "info", "message": "", "details": {}}
    
    # Load token usage from MiniMax/litellm logs
    # For now, use session_status if available
    token_data = DATA_DIR / "token_usage_history.json"
    if not token_data.exists():
        result["message"] = "No token usage data yet"
        return result
    
    data = json.load(open(token_data))
    if len(data) < 3:
        result["message"] = "Insufficient data for analysis"
        return result
    
    # Calculate hourly averages
    hourly = defaultdict(int)
    for entry in data:
        ts = entry.get("timestamp", "")
        if ts:
            hour = ts[:13]  # YYYY-MM-DDTHH
            hourly[hour] += entry.get("tokens", 0)
    
    if not hourly:
        result["message"] = "No hourly data"
        return result
    
    hours = sorted(hourly.items(), key=lambda x: x[0])
    if len(hours) < 2:
        result["message"] = "Need at least 2 hours of data"
        return result
    
    values = [v for _, v in hours]
    avg = sum(values) / len(values)
    last_hour = hours[-1][1]
    
    result["details"] = {
        "last_hour_tokens": last_hour,
        "average_tokens": avg,
        "ratio": last_hour / avg if avg > 0 else 0,
        "hour_count": len(hours),
    }
    
    if last_hour > avg * 2 and last_hour > 500000:
        result["anomaly"] = True
        result["severity"] = "critical"
        result["message"] = f"Token burst: {last_hour:,} tokens (avg: {avg:,.0f}, ratio: {last_hour/avg:.1f}x)"
    elif last_hour > avg * 1.5:
        result["anomaly"] = True
        result["severity"] = "warning"
        result["message"] = f"Token elevation: {last_hour:,} tokens (avg: {avg:,.0f})"
    
    return result


def check_api_response_times(state: dict) -> dict:
    """
    API Response Time Degradation Detection.
    
    Alert wenn:
    - Response Time im letzten Durchlauf > 2x Durchschnitt
    - Oder Response Time > 10s für Standard-Operationen
    """
    result = {"anomaly": False, "severity": "info", "message": "", "details": {}}
    
    rt_file = DATA_DIR / "api_response_times.json"
    if not rt_file.exists():
        result["message"] = "No response time data"
        return result
    
    data = json.load(open(rt_file))
    if len(data) < 5:
        result["message"] = "Insufficient data"
        return result
    
    last = data[-1]
    values = [d.get("duration_ms", 0) for d in data]
    avg = sum(values) / len(values)
    p95 = sorted(values)[int(len(values) * 0.95)] if values else 0
    
    result["details"] = {
        "last_ms": last.get("duration_ms", 0),
        "average_ms": avg,
        "p95_ms": p95,
        "sample_count": len(values),
    }
    
    if last.get("duration_ms", 0) > avg * 2 and last.get("duration_ms", 0) > 10000:
        result["anomaly"] = True
        result["severity"] = "critical"
        result["message"] = f"Response degradation: {last.get('duration_ms')}ms (avg: {avg:.0f}ms)"
    elif last.get("duration_ms", 0) > avg * 1.5:
        result["anomaly"] = True
        result["severity"] = "warning"
        result["message"] = f"Response elevation: {last.get('duration_ms')}ms (avg: {avg:.0f}ms)"
    
    return result


def check_session_rate(state: dict) -> dict:
    """
    Session Creation Rate Detection.
    
    Alert wenn:
    - > 10 neue Sessions in einer Stunde
    - Oder plötzlicher Drop auf 0 (Heartbeat-Problem)
    """
    result = {"anomaly": False, "severity": "info", "message": "", "details": {}}
    
    # Check session creation log
    session_log = DATA_DIR / "session_creations.json"
    if not session_log.exists():
        result["message"] = "No session creation data"
        return result
    
    data = json.load(open(session_log))
    if len(data) < 3:
        result["message"] = "Insufficient data"
        return result
    
    hourly = defaultdict(int)
    for entry in data:
        ts = entry.get("created_at", "")
        if ts:
            hour = ts[:13]
            hourly[hour] += 1
    
    hours = sorted(hourly.items(), key=lambda x: x[0])
    if len(hours) < 2:
        result["message"] = "Need more data"
        return result
    
    last_count = hours[-1][1]
    values = [v for _, v in hours]
    avg = sum(values) / len(values)
    
    result["details"] = {
        "last_hour_sessions": last_count,
        "average_sessions": avg,
        "hour_count": len(hours),
    }
    
    if last_count > 10:
        result["anomaly"] = True
        result["severity"] = "warning"
        result["message"] = f"Session spike: {last_count} sessions in last hour (avg: {avg:.1f})"
    elif last_count == 0 and avg > 0.5:
        result["anomaly"] = True
        result["severity"] = "critical"
        result["message"] = f"Session famine: 0 sessions (avg: {avg:.1f}/hr)"
    
    return result


def check_kg_growth(state: dict) -> dict:
    """
    KG Growth Stagnation Detection.
    
    Alert wenn:
    - KG wächst nicht seit 48h
    - Oder KG Shrink (Entity Count drop > 10%)
    """
    result = {"anomaly": False, "severity": "info", "message": "", "details": {}}
    
    if not KG_FILE.exists():
        result["message"] = "KG file not found"
        return result
    
    kg = json.load(open(KG_FILE))
    current_entities = len(kg.get("entities", {}))
    current_relations = len(kg.get("relations", {}))
    
    # Load historical data
    kg_history = DATA_DIR / "kg_growth_history.json"
    history = []
    if kg_history.exists():
        history = json.load(open(kg_history))
    
    result["details"] = {
        "current_entities": current_entities,
        "current_relations": current_relations,
        "history_points": len(history),
    }
    
    if len(history) >= 2:
        last = history[-1]
        prev = history[-2]
        
        # Check stagnation
        time_diff_h = 0
        if last.get("timestamp") and prev.get("timestamp"):
            t1 = datetime.fromisoformat(last["timestamp"].replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(prev["timestamp"].replace("Z", "+00:00"))
            time_diff_h = (t1 - t2).total_seconds() / 3600
        
        entity_diff = current_entities - last.get("entities", current_entities)
        
        # Stagnation: no growth in 48h
        if time_diff_h >= 48 and entity_diff == 0:
            result["anomaly"] = True
            result["severity"] = "warning"
            result["message"] = f"KG stagnation: no growth in {time_diff_h:.0f}h"
        
        # Shrink
        if entity_diff < 0 and abs(entity_diff) / current_entities > 0.1:
            result["anomaly"] = True
            result["severity"] = "critical"
            result["message"] = f"KG shrink: -{abs(entity_diff)} entities"
    
    # Update history
    history.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "entities": current_entities,
        "relations": current_relations,
    })
    # Keep last 30 days
    history = history[-720:]  # 30 days * 24h
    with open(kg_history, "w") as f:
        json.dump(history, f, indent=2)
    
    return result


def check_event_diversity(state: dict) -> dict:
    """
    Event Diversity / Famine Detection.
    
    Alert wenn:
    - < 1 Event in 6 Stunden (Famine)
    - Oder nur 1 Event Type in 24h (Monotony)
    """
    result = {"anomaly": False, "severity": "info", "message": "", "details": {}}
    
    if not EVENT_FILE.exists():
        result["message"] = "No event data"
        return result
    
    lines = EVENT_FILE.read_text().strip().split("\n")
    if not lines:
        result["message"] = "No events recorded"
        return result
    
    # Analyze last 24h
    cutoff_24h = (datetime.utcnow() - timedelta(hours=24)).timestamp()
    cutoff_6h = (datetime.utcnow() - timedelta(hours=6)).timestamp()
    
    events_6h = 0
    events_24h = 0
    event_types = set()
    
    for line in lines:
        try:
            evt = json.loads(line)
            ts_str = evt.get("timestamp", "0")
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
            
            if ts > cutoff_24h:
                events_24h += 1
                event_types.add(evt.get("type", "unknown"))
                if ts > cutoff_6h:
                    events_6h += 1
        except:
            pass
    
    result["details"] = {
        "events_6h": events_6h,
        "events_24h": events_24h,
        "event_types_24h": len(event_types),
        "type_list": list(event_types),
    }
    
    if events_6h == 0:
        result["anomaly"] = True
        result["severity"] = "critical"
        result["message"] = f"Event famine: 0 events in 6h"
    elif events_24h == 0:
        result["anomaly"] = True
        result["severity"] = "warning"
        result["message"] = "Event famine: 0 events in 24h"
    elif len(event_types) <= 1 and events_24h > 5:
        result["anomaly"] = True
        result["severity"] = "warning"
        result["message"] = f"Event monotony: only {event_types} types in 24h"
    
    return result


def check_cron_error_rate(state: dict) -> dict:
    """
    Cron Error Rate Spike Detection.
    
    Alert wenn:
    - > 30% Cron Jobs mit Errors in letztem Run
    - Oder bestimmte Jobs 3x hintereinander fehlerhaft
    """
    result = {"anomaly": False, "severity": "info", "message": "", "details": {}}
    
    if not CRON_STATE_FILE.exists():
        result["message"] = "No cron state data"
        return result
    
    data = json.load(open(CRON_STATE_FILE))
    last_run = data.get("last_run", {})
    jobs = last_run.get("jobs", [])
    
    if not jobs:
        result["message"] = "No recent cron runs"
        return result
    
    total = len(jobs)
    errors = sum(1 for j in jobs if j.get("error"))
    error_rate = errors / total if total > 0 else 0
    
    result["details"] = {
        "total_jobs": total,
        "error_count": errors,
        "error_rate": error_rate,
    }
    
    if error_rate > 0.3:
        result["anomaly"] = True
        result["severity"] = "critical"
        result["message"] = f"Cron error spike: {errors}/{total} ({error_rate:.0%})"
    elif error_rate > 0.15:
        result["anomaly"] = True
        result["severity"] = "warning"
        result["message"] = f"Cron error elevation: {errors}/{total} ({error_rate:.0%})"
    
    return result


def run_all_checks(state: dict) -> dict:
    """Run all anomaly checks."""
    checks = {
        "token_burst": check_token_burst(state),
        "api_response": check_api_response_times(state),
        "session_rate": check_session_rate(state),
        "kg_growth": check_kg_growth(state),
        "event_diversity": check_event_diversity(state),
        "cron_errors": check_cron_error_rate(state),
    }
    
    anomalies = {k: v for k, v in checks.items() if v.get("anomaly")}
    
    return {
        "checks": checks,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def print_report(result: dict):
    """Print human-readable report."""
    print("=" * 60)
    print("🚨 ANOMALY DETECTOR REPORT")
    print("=" * 60)
    print(f"Timestamp: {result.get('timestamp', '?')}")
    print(f"Anomalies found: {result.get('anomaly_count', 0)}")
    print()
    
    for name, check in result.get("checks", {}).items():
        severity = check.get("severity", "info")
        icon = {"critical": "🔴", "warning": "🟠", "info": "🟢"}.get(severity, "⚪")
        msg = check.get("message", "OK")
        print(f"{icon} {name}: {msg}")
        
        if check.get("details"):
            for k, v in check.get("details", {}).items():
                print(f"   {k}: {v}")
    
    print()
    anomalies = result.get("anomalies", {})
    if anomalies:
        print(f"⚠️  {len(anomalies)} ANOMALIES DETECTED:")
        for name, data in anomalies.items():
            print(f"   - {name}: {data.get('message')}")
    else:
        print("✅ All systems nominal")


def main():
    parser = argparse.ArgumentParser(description="Anomaly Detector")
    parser.add_argument("--check", default="all", help="Check to run (all, token_burst, etc.)")
    parser.add_argument("--report", action="store_true", help="Print latest report")
    args = parser.parse_args()
    
    state = load_state()
    
    if args.report:
        report_file = DATA_DIR / "anomaly_report_latest.json"
        if report_file.exists():
            result = json.load(open(report_file))
            print_report(result)
        else:
            print("No report available. Run --check first.")
        return
    
    if args.check == "all":
        result = run_all_checks(state)
        state["checks"] = result["checks"]
        state["last_anomaly_count"] = result["anomaly_count"]
        save_state(state)
        
        # Save latest report
        report_file = DATA_DIR / "anomaly_report_latest.json"
        with open(report_file, "w") as f:
            json.dump(result, f, indent=2)
        
        print_report(result)
        
        # Alert if critical
        for name, data in result.get("anomalies", {}).items():
            if data.get("severity") == "critical":
                print(f"\n🚨 CRITICAL: {name} — Alert should be sent!")
    else:
        check_funcs = {
            "token_burst": check_token_burst,
            "api_response": check_api_response_times,
            "session_rate": check_session_rate,
            "kg_growth": check_kg_growth,
            "event_diversity": check_event_diversity,
            "cron_errors": check_cron_error_rate,
        }
        
        if args.check in check_funcs:
            result = check_funcs[args.check](state)
            print(f"📊 {args.check}:")
            print(f"   anomaly: {result.get('anomaly')}")
            print(f"   severity: {result.get('severity')}")
            print(f"   message: {result.get('message')}")
            if result.get("details"):
                for k, v in result.get("details").items():
                    print(f"   {k}: {v}")
        else:
            print(f"Unknown check: {args.check}")
            print(f"Available: {list(check_funcs.keys())}")


if __name__ == "__main__":
    main()
