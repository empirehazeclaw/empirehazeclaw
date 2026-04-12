#!/usr/bin/env python3
"""
session_pin_manager.py - Session Pin Management für Model Failover
Sir HazeClaw - 2026-04-12

Verwaltet Session Model Pins für Auto-Failover wenn ein Model ausfällt.

Usage:
    python3 session_pin_manager.py --list              # List all sessions mit pins
    python3 session_pin_manager.py --set SESSION MODEL # Pin session to model
    python3 session_pin_manager.py --clear SESSION      # Clear pin
    python3 session_pin_manager.py --failover MODEL    # Failover all sessions from model
    python3 session_pin_manager.py --healthy MODEL      # Mark model healthy, restore pins
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
AGENTS_DIR = Path("/home/clawbot/.openclaw/agents")
STATE_FILE = WORKSPACE / "memory" / "session_pins.json"

# Fallback chain
DEFAULT_MODEL_CHAIN = [
    "minimax/MiniMax-M2.7",
    "openai/gpt-4o-mini",
    "openrouter/qwen3-coder:free",
]

def load_state() -> Dict:
    """Lädt Session Pin State."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "pinned_sessions": {},  # session_id -> {model, original_model, pinned_at}
        "model_to_sessions": {},  # model -> [session_ids]
        "pin_history": [],  # Recent pin changes
    }

def save_state(state: Dict):
    """Speichert Session Pin State."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_active_sessions() -> List[Dict]:
    """Holt alle aktiven Sessions aus agents directory."""
    sessions = []
    
    if not AGENTS_DIR.exists():
        return sessions
    
    for agent_dir in AGENTS_DIR.iterdir():
        if not agent_dir.is_dir():
            continue
        
        sessions_file = agent_dir / "sessions" / "sessions.json"
        if sessions_file.exists():
            try:
                with open(sessions_file) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for session in data:
                            session["agent"] = agent_dir.name
                            sessions.append(session)
                    elif isinstance(data, dict):
                        data["agent"] = agent_dir.name
                        sessions.append(data)
            except Exception as e:
                print(f"⚠️ Error reading {sessions_file}: {e}")
    
    return sessions

def get_session_pin(session_id: str, state: Dict = None) -> Optional[str]:
    """Gibt das gepinnte Model für eine Session zurück."""
    if state is None:
        state = load_state()
    return state.get("pinned_sessions", {}).get(session_id, {}).get("model")

def pin_session(session_id: str, model: str, state: Dict = None) -> bool:
    """Pinnt eine Session auf ein bestimmtes Model."""
    if state is None:
        state = load_state()
    
    # Altes Model merken falls es ein original war
    current_pin = get_session_pin(session_id, state)
    
    state["pinned_sessions"][session_id] = {
        "model": model,
        "original_model": current_pin if current_pin else None,
        "pinned_at": "null",  # Will be set below
    }
    
    # Update model_to_sessions mapping
    if current_pin and current_pin in state.get("model_to_sessions", {}):
        state["model_to_sessions"][current_pin] = [
            s for s in state["model_to_sessions"].get(current_pin, []) 
            if s != session_id
        ]
    
    if model not in state.get("model_to_sessions", {}):
        state["model_to_sessions"][model] = []
    if session_id not in state["model_to_sessions"][model]:
        state["model_to_sessions"][model].append(session_id)
    
    # Pin history
    state["pin_history"].append({
        "session": session_id,
        "model": model,
        "action": "pin",
        "at": "null"
    })
    state["pin_history"] = state["pin_history"][-100:]  # Keep last 100
    
    save_state(state)
    return True

def clear_pin(session_id: str, state: Dict = None) -> bool:
    """Entfernt Pin für eine Session (restore original)."""
    if state is None:
        state = load_state()
    
    pinned = state.get("pinned_sessions", {}).get(session_id)
    if not pinned:
        return False
    
    model = pinned.get("model")
    
    del state["pinned_sessions"][session_id]
    
    # Update model_to_sessions
    if model and model in state.get("model_to_sessions", {}):
        state["model_to_sessions"][model] = [
            s for s in state["model_to_sessions"].get(model, [])
            if s != session_id
        ]
    
    # Pin history
    state["pin_history"].append({
        "session": session_id,
        "model": model,
        "action": "unpin",
        "at": "null"
    })
    state["pin_history"] = state["pin_history"][-100:]
    
    save_state(state)
    return True

def failover_session(session_id: str, from_model: str, state: Dict = None) -> Optional[str]:
    """Failovert eine Session auf nächstes verfügbares Model."""
    if state is None:
        state = load_state()
    
    # Find next model in chain after from_model
    chain = DEFAULT_MODEL_CHAIN
    try:
        idx = chain.index(from_model)
        next_models = chain[idx + 1:]
    except ValueError:
        next_models = chain[1:]  # Skip first if not found
    
    # Use first available from next_models
    # (Hier könnte cooldowns manager integrated werden)
    for model in next_models:
        # Simple check: wenn nicht "failed" in cooldowns
        # Vollständige integration kommt später
        pin_session(session_id, model, state)
        print(f"  🔄 {session_id}: {from_model} → {model}")
        return model
    
    print(f"  ⚠️ {session_id}: No fallback available for {from_model}")
    return None

def failover_all_from_model(failed_model: str, state: Dict = None) -> List[str]:
    """Failovert alle Sessions die auf failed_model gepinnt sind."""
    if state is None:
        state = load_state()
    
    sessions_to_failover = state.get("model_to_sessions", {}).get(failed_model, [])
    
    if not sessions_to_failover:
        print(f"No sessions pinned to {failed_model}")
        return []
    
    results = []
    for session_id in sessions_to_failover:
        result = failover_session(session_id, failed_model, state)
        if result:
            results.append(session_id)
    
    print(f"\n✅ Failed over {len(results)} sessions from {failed_model}")
    return results

def list_sessions_with_pins(state: Dict = None) -> List[Dict]:
    """Listet alle Sessions mit ihren aktuellen Pins."""
    if state is None:
        state = load_state()
    
    sessions = get_active_sessions()
    pinned = state.get("pinned_sessions", {})
    
    result = []
    for session in sessions:
        session_id = session.get("id") or session.get("sessionId")
        if not session_id:
            continue
        
        pin_info = pinned.get(session_id, {})
        if pin_info:
            session["pinned_model"] = pin_info.get("model")
            session["original_model"] = pin_info.get("original_model")
            result.append(session)
    
    return result

def show_status(state: Dict = None):
    """Zeigt aktuellen Pin Status."""
    if state is None:
        state = load_state()
    
    print("\n📊 SESSION PIN MANAGER STATUS")
    print("=" * 50)
    
    pinned = state.get("pinned_sessions", {})
    
    if not pinned:
        print("No pinned sessions.\n")
    else:
        print(f"Pinned sessions: {len(pinned)}\n")
        for session_id, info in pinned.items():
            model = info.get("model", "unknown")
            print(f"📌 {session_id[:20]}...")
            print(f"   Model: {model}")
    
    # Model -> Sessions mapping
    mapping = state.get("model_to_sessions", {})
    if mapping:
        print("\n📍 Model → Sessions:")
        for model, sessions in mapping.items():
            print(f"   {model}: {len(sessions)} sessions")
    
    # Recent history
    history = state.get("pin_history", [])
    if history:
        print(f"\n📜 Recent pin history ({len(history)} entries):")
        for entry in history[-5:]:
            print(f"   {entry['action']}: {entry['session'][:15]}... → {entry['model']}")

def main():
    parser = argparse.ArgumentParser(description="Session Pin Manager")
    parser.add_argument("--list", action="store_true", help="List all pinned sessions")
    parser.add_argument("--set", nargs=2, metavar=("SESSION", "MODEL"), help="Pin session to model")
    parser.add_argument("--clear", metavar="SESSION", help="Clear pin for session")
    parser.add_argument("--failover", metavar="MODEL", help="Failover all sessions from model")
    parser.add_argument("--healthy", metavar="MODEL", help="Mark model healthy, restore pins")
    parser.add_argument("--status", action="store_true", help="Show full status")
    
    args = parser.parse_args()
    
    if args.list:
        sessions = list_sessions_with_pins()
        if not sessions:
            print("No pinned sessions.")
        else:
            print(f"\n📌 PINNED SESSIONS ({len(sessions)}):")
            for s in sessions:
                print(f"  {s.get('id', s.get('sessionId', '?'))}: {s.get('pinned_model')}")
    
    elif args.set:
        session_id, model = args.set
        pin_session(session_id, model)
        print(f"✅ Pinned {session_id} to {model}")
    
    elif args.clear:
        if clear_pin(args.clear):
            print(f"✅ Cleared pin for {args.clear}")
        else:
            print(f"ℹ️ {args.clear} was not pinned")
    
    elif args.failover:
        results = failover_all_from_model(args.failover)
        print(f"✅ Failed over {len(results)} sessions")
    
    elif args.healthy:
        # Clear all pins for this model (model is back)
        state = load_state()
        sessions = state.get("model_to_sessions", {}).get(args.healthy, [])
        for session_id in sessions:
            clear_pin(session_id, state)
        print(f"✅ Restored {len(sessions)} sessions from {args.healthy}")
    
    elif args.status:
        show_status()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    sys.exit(main())
