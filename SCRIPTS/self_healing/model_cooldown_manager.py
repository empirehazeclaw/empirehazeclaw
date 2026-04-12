#!/usr/bin/env python3
"""
model_cooldown_manager.py - Model Cooldown State Management
Sir HazeClaw - 2026-04-12

Verwaltet Cooldown States für Models nach failures/rate limits.
Kann von anderen Scripts aufgerufen werden um Model availability zu prüfen.

Usage:
    python3 model_cooldown_manager.py --status     # Show all cooldowns
    python3 model_cooldown_manager.py --set MODEL --minutes 30  # Set cooldown
    python3 model_cooldown_manager.py --clear MODEL  # Clear cooldown
    python3 model_cooldown_manager.py --available   # List available models
"""

import json
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
STATE_FILE = WORKSPACE / "memory" / "model_cooldown.json"

# Default cooldown durations (minutes) by failure type
COOLDOWN_DEFAULTS = {
    "rate_limit": 15,
    "auth_error": 60,
    "timeout": 10,
    "server_error": 30,
    "unknown": 15,
}

DEFAULT_COOLDOWN = 15

def load_state() -> Dict:
    """Lädt Cooldown State."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "cooldowns": {},  # model_id -> {reason, until, failures}
        "history": [],    # Recent cooldowns for analysis
    }

def save_state(state: Dict):
    """Speichert Cooldown State."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def set_cooldown(model_id: str, reason: str, minutes: int = None, state: Dict = None) -> Dict:
    """Setzt ein Model in Cooldown."""
    if state is None:
        state = load_state()
    
    if minutes is None:
        minutes = COOLDOWN_DEFAULTS.get(reason, DEFAULT_COOLDOWN)
    
    until = datetime.now() + timedelta(minutes=minutes)
    
    cooldown_entry = {
        "reason": reason,
        "until": until.isoformat(),
        "set_at": datetime.now().isoformat(),
        "minutes": minutes,
        "failures": state["cooldowns"].get(model_id, {}).get("failures", 0) + 1,
    }
    
    state["cooldowns"][model_id] = cooldown_entry
    
    # Add to history (keep last 50)
    history_entry = {
        "model": model_id,
        "reason": reason,
        "until": until.isoformat(),
        "set_at": datetime.now().isoformat(),
    }
    state["history"].append(history_entry)
    state["history"] = state["history"][-50:]
    
    save_state(state)
    return cooldown_entry

def clear_cooldown(model_id: str, state: Dict = None) -> bool:
    """Entfernt Cooldown für ein Model."""
    if state is None:
        state = load_state()
    
    if model_id in state["cooldowns"]:
        del state["cooldowns"][model_id]
        save_state(state)
        return True
    return False

def is_in_cooldown(model_id: str, state: Dict = None) -> bool:
    """Prüft ob Model aktuell in Cooldown ist."""
    if state is None:
        state = load_state()
    
    cooldown = state["cooldowns"].get(model_id)
    if not cooldown:
        return False
    
    until = datetime.fromisoformat(cooldown["until"])
    if datetime.now() < until:
        return True
    
    # Cooldown abgelaufen - automatisch entfernen
    clear_cooldown(model_id, state)
    return False

def get_cooldown_remaining(model_id: str, state: Dict = None) -> int:
    """Gibt verbleibende Cooldown Minuten zurück."""
    if state is None:
        state = load_state()
    
    cooldown = state["cooldowns"].get(model_id)
    if not cooldown:
        return 0
    
    until = datetime.fromisoformat(cooldown["until"])
    remaining = (until - datetime.now()).total_seconds() / 60
    return max(0, int(remaining))

def get_available_models(models: List[str], state: Dict = None) -> List[str]:
    """Gibt Liste von Models zurück die NICHT in Cooldown sind."""
    if state is None:
        state = load_state()
    
    available = []
    for model_id in models:
        if not is_in_cooldown(model_id, state):
            available.append(model_id)
    return available

def get_best_available(models: List[str], state: Dict = None) -> Optional[str]:
    """Gibt das erste verfügbare Model zurück (bevorzugt Reihenfolge)."""
    available = get_available_models(models, state)
    return available[0] if available else None

def record_failure(model_id: str, reason: str = "unknown", state: Dict = None):
    """Recorded einen Model Failure und setzt Cooldown wenn nötig."""
    if state is None:
        state = load_state()
    
    failures = state["cooldowns"].get(model_id, {}).get("failures", 0)
    
    # Nach 3 failures in kurzer Zeit -> Cooldown
    if failures >= 3:
        minutes = COOLDOWN_DEFAULTS.get(reason, DEFAULT_COOLDOWN) * (failures // 3)
        set_cooldown(model_id, reason, minutes, state)
        print(f"⚠️ {model_id}: {failures} failures, cooldown {minutes}m")
    else:
        # Nur failure zählen ohne cooldown
        if model_id not in state["cooldowns"]:
            state["cooldowns"][model_id] = {"failures": 0}
        state["cooldowns"][model_id]["failures"] = failures + 1
        state["cooldowns"][model_id]["last_failure"] = datetime.now().isoformat()
        save_state(state)

def record_success(model_id: str, state: Dict = None):
    """Recorded einen Model Success und cleared Cooldown."""
    if state is None:
        state = load_state()
    
    if clear_cooldown(model_id, state):
        print(f"✅ {model_id}: Cooldown cleared")
    else:
        # Reset failure count
        if model_id in state["cooldowns"]:
            state["cooldowns"][model_id]["failures"] = 0
            save_state(state)

def show_status(state: Dict = None):
    """Zeigt aktuellen Cooldown Status."""
    if state is None:
        state = load_state()
    
    print("\n📊 MODEL COOLDOWN STATUS")
    print("=" * 50)
    
    cooldowns = state.get("cooldowns", {})
    
    if not cooldowns:
        print("No models in cooldown.\n")
        return
    
    for model_id, data in cooldowns.items():
        remaining = get_cooldown_remaining(model_id, state)
        reason = data.get("reason", "unknown")
        failures = data.get("failures", 0)
        
        if remaining > 0:
            print(f"⚡ {model_id}")
            print(f"   Reason: {reason}")
            print(f"   Remaining: {remaining}m")
            print(f"   Failures: {failures}")
        else:
            print(f"✅ {model_id}: Available (was in cooldown)")
    print()

def main():
    parser = argparse.ArgumentParser(description="Model Cooldown Manager")
    parser.add_argument("--status", action="store_true", help="Show cooldown status")
    parser.add_argument("--set", metavar="MODEL", help="Set cooldown for model")
    parser.add_argument("--clear", metavar="MODEL", help="Clear cooldown for model")
    parser.add_argument("--minutes", type=int, default=None, help="Cooldown minutes")
    parser.add_argument("--reason", default="unknown", help="Failure reason")
    parser.add_argument("--available", nargs="*", help="List available models")
    parser.add_argument("--record-failure", metavar="MODEL", help="Record failure")
    parser.add_argument("--record-success", metavar="MODEL", help="Record success")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.set:
        entry = set_cooldown(args.set, args.reason, args.minutes)
        print(f"⚡ {args.set}: Cooldown set for {entry['minutes']}m ({entry['reason']})")
    elif args.clear:
        if clear_cooldown(args.clear):
            print(f"✅ {args.clear}: Cooldown cleared")
        else:
            print(f"ℹ️ {args.clear}: Was not in cooldown")
    elif args.available is not None:
        models = args.available if args.available else ["minimax/MiniMax-M2.7", "openai/gpt-4o-mini"]
        available = get_available_models(models)
        print(f"Available models: {available}")
        best = get_best_available(models)
        print(f"Best: {best}")
    elif args.record_failure:
        record_failure(args.record_failure, args.reason)
    elif args.record_success:
        record_success(args.record_success)
    else:
        parser.print_help()

if __name__ == "__main__":
    sys.exit(main())
