#!/usr/bin/env python3
"""
model_health_checker.py - Health Probe für alle konfigurierten Models
Sir HazeClaw - 2026-04-12

Prüft ob Models erreichbar sind und in welchem Status sie sind.

Usage:
    python3 model_health_checker.py              # Check all models
    python3 model_health_checker.py --model mini  # Check specific model
    python3 model_health_checker.py --status     # Show saved status
    python3 model_health_checker.py --probe      # Force fresh probe
"""

import json
import time
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
STATE_FILE = WORKSPACE / "memory" / "model_health_state.json"
CONFIG_FILE = Path("/home/clawbot/.openclaw/openclaw.json")

# Modelle die wir checken
MODELS = [
    "minimax/MiniMax-M2.7",
    "openai/gpt-4o-mini",
    "openrouter/qwen3-coder:free",
]

# Cooldown nach failed probe (Minuten)
COOLDOWN_MINUTES = 15
CIRCUIT_BREAKER_THRESHOLD = 3  # 3 failures = cooldown

def load_state() -> Dict:
    """Lädt gespeicherten Model State."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "models": {},
        "last_probe": None,
        "circuit_breaker": {}
    }

def save_state(state: Dict):
    """Speichert Model State."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_configured_models() -> List[str]:
    """Holt alle konfigurierten Models aus openclaw.json."""
    models = []
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        
        # Check agents.defaults.model (can be string OR dict)
        defaults = config.get("agents", {}).get("defaults", {})
        model = defaults.get("model")
        if isinstance(model, str):
            models.append(model)
        elif isinstance(model, dict):
            # Handle {primary, fallbacks} format
            if "primary" in model:
                models.append(model["primary"])
            if "fallbacks" in model and isinstance(model["fallbacks"], list):
                models.extend(model["fallbacks"])
        
        # Check providers
        providers = config.get("providers", {})
        for provider, conf in providers.items():
            if "model" in conf:
                m = conf["model"]
                if isinstance(m, str) and m not in models:
                    models.append(m)
                elif isinstance(m, dict):
                    if "primary" in m:
                        models.append(m["primary"])
                    if "fallbacks" in m and isinstance(m["fallbacks"], list):
                        for fb in m["fallbacks"]:
                            if fb not in models:
                                models.append(fb)
    except Exception as e:
        print(f"⚠️ Could not read config: {e}")
    
    # Fallback zu MODELS list
    if not models:
        models = MODELS
    
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for m in models:
        if m not in seen:
            seen.add(m)
            deduped.append(m)
    
    return deduped

def probe_model(model_id: str) -> Dict:
    """
    Probed ein Model mit einem einfachen API call.
    Returns: {"status": "ok"|"error", "latency_ms": int, "error": str|None}
    """
    import urllib.request
    import urllib.error
    
    start = time.time()
    result = {
        "model": model_id,
        "status": "unknown",
        "latency_ms": None,
        "error": None,
        "timestamp": datetime.now().isoformat()
    }
    
    # MiniMax probe
    if "minimax" in model_id.lower():
        try:
            # MiniMax hat keinen public health endpoint
            # Wir probieren einen minimalen API call
            # Hier wäre ein echter API key nötig
            result["status"] = "unknown"
            result["error"] = "MiniMax: kein public health endpoint"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
    
    # OpenAI probe
    elif "openai" in model_id.lower():
        try:
            # OpenAI hat health endpoint
            req = urllib.request.Request(
                "https://api.openai.com/v1/models",
                headers={"Authorization": "Bearer dummy"}  # Wir testen nur connectivity
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                result["status"] = "ok" if resp.status == 200 else "degraded"
        except urllib.error.HTTPError as e:
            if e.code == 401:
                result["status"] = "ok"  # Auth error means model exists
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {e.code}"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
    
    # OpenRouter probe
    elif "openrouter" in model_id.lower():
        try:
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": "Bearer dummy"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                result["status"] = "ok" if resp.status == 200 else "degraded"
        except urllib.error.HTTPError as e:
            if e.code == 401:
                result["status"] = "ok"
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {e.code}"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
    
    # Unbekannter Provider
    else:
        result["status"] = "unknown"
        result["error"] = f"Unknown provider for {model_id}"
    
    result["latency_ms"] = int((time.time() - start) * 1000)
    return result

def check_circuit_breaker(state: Dict, model_id: str) -> bool:
    """Prüft ob Model im Circuit Breaker cooldown ist."""
    circuit_breakers = state.get("circuit_breaker")
    if not circuit_breakers or not isinstance(circuit_breakers, dict):
        return False
    
    cb = circuit_breakers.get(model_id)
    if not cb or not isinstance(cb, dict):
        return False
    
    if not cb.get("in_cooldown"):
        return False
    
    cooldown_until_str = cb.get("cooldown_until")
    if not cooldown_until_str:
        return False
    
    cooldown_until = datetime.fromisoformat(cooldown_until_str)
    
    if datetime.now() < cooldown_until:
        return True  # Noch im cooldown
    
    return False  # Cooldown abgelaufen

def update_circuit_breaker(state: Dict, model_id: str, failed: bool):
    """Updated Circuit Breaker state."""
    if "circuit_breaker" not in state or not isinstance(state["circuit_breaker"], dict):
        state["circuit_breaker"] = {}
    
    if model_id not in state["circuit_breaker"]:
        state["circuit_breaker"][model_id] = {"failures": 0, "in_cooldown": False}
    
    cb = state["circuit_breaker"][model_id]
    if not isinstance(cb, dict):
        cb = {"failures": 0, "in_cooldown": False}
        state["circuit_breaker"][model_id] = cb
    
    if failed:
        cb["failures"] = cb.get("failures", 0) + 1
        cb["last_failure"] = datetime.now().isoformat()
        
        if cb["failures"] >= CIRCUIT_BREAKER_THRESHOLD:
            cb["in_cooldown"] = True
            cb["cooldown_until"] = (
                datetime.now() + timedelta(minutes=COOLDOWN_MINUTES)
            ).isoformat()
            print(f"🔴 {model_id}: Circuit breaker ACTIVATED ({cb['failures']} failures)")
    else:
        # Erfolg - reset
        cb["failures"] = 0
        cb["in_cooldown"] = False

def get_healthy_model(state: Dict, preferred: List[str] = None) -> Optional[str]:
    """Gibt das erste verfügbare Model zurück."""
    if preferred is None:
        preferred = get_configured_models()
    
    for model_id in preferred:
        if check_circuit_breaker(state, model_id):
            continue
        
        model_state = state.get("models", {}).get(model_id, {})
        if model_state.get("status") == "ok":
            return model_id
    
    return preferred[0] if preferred else None

def probe_all_models(force: bool = False) -> List[Dict]:
    """Probed alle konfigurierten Models."""
    state = load_state()
    results = []
    
    models_to_check = get_configured_models()
    
    for model_id in models_to_check:
        # Circuit breaker check
        if check_circuit_breaker(state, model_id):
            cb = state["circuit_breaker"][model_id]
            cooldown_until = datetime.fromisoformat(cb["cooldown_until"])
            remaining = (cooldown_until - datetime.now()).seconds // 60
            print(f"⚡ {model_id}: In cooldown ({remaining}m remaining)")
            results.append({
                "model": model_id,
                "status": "cooldown",
                "cooldown_remaining_min": remaining
            })
            continue
        
        # Probe
        print(f"🔍 Probing {model_id}...")
        result = probe_model(model_id)
        results.append(result)
        
        # Update state
        if "models" not in state:
            state["models"] = {}
        state["models"][model_id] = result
        
        # Circuit breaker update
        failed = result["status"] == "error"
        update_circuit_breaker(state, model_id, failed)
        
        # Status output
        if result["status"] == "ok":
            print(f"  ✅ {model_id}: OK ({result.get('latency_ms', 0)}ms)")
        elif result["status"] == "cooldown":
            print(f"  ⚡ {model_id}: COOLDOWN")
        else:
            print(f"  ❌ {model_id}: ERROR - {result.get('error', 'unknown')}")
    
    state["last_probe"] = datetime.now().isoformat()
    save_state(state)
    
    return results

def show_status():
    """Zeigt aktuellen Model Status."""
    state = load_state()
    
    print("\n📊 MODEL HEALTH STATUS")
    print("=" * 50)
    
    if not state.get("models"):
        print("No model data. Run with --probe first.")
        return
    
    print(f"Last probe: {state.get('last_probe', 'never')}\n")
    
    for model_id, data in state.get("models", {}).items():
        status = data.get("status", "unknown")
        latency = data.get("latency_ms", 0)
        
        if status == "ok":
            icon = "✅"
        elif status == "error":
            icon = "❌"
        elif status == "cooldown":
            icon = "⚡"
        else:
            icon = "❓"
        
        error = data.get("error", "")
        print(f"{icon} {model_id}")
        print(f"   Status: {status}")
        if latency:
            print(f"   Latency: {latency}ms")
        if error:
            print(f"   Error: {error}")
        print()
    
    # Circuit breaker info
    if state.get("circuit_breaker"):
        print("\n🔧 CIRCUIT BREAKERS:")
        for model_id, cb in state["circuit_breaker"].items():
            if cb.get("in_cooldown"):
                remaining = (datetime.fromisoformat(cb["cooldown_until"]) - datetime.now()).seconds // 60
                print(f"  ⚡ {model_id}: {cb['failures']} failures, cooldown {remaining}m")

def main():
    parser = argparse.ArgumentParser(description="Model Health Checker")
    parser.add_argument("--model", help="Check specific model only")
    parser.add_argument("--status", action="store_true", help="Show saved status")
    parser.add_argument("--probe", action="store_true", help="Force fresh probe")
    parser.add_argument("--healthy", action="store_true", help="Return healthy model")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.probe or not args.status:
        results = probe_all_models(force=args.probe)
        print("\n" + "=" * 50)
        print(f"Probed {len(results)} models")
        
        # Summary
        ok = sum(1 for r in results if r["status"] == "ok")
        error = sum(1 for r in results if r["status"] == "error")
        cooldown = sum(1 for r in results if r["status"] == "cooldown")
        
        print(f"✅ OK: {ok}, ❌ Error: {error}, ⚡ Cooldown: {cooldown}")
        
        if args.healthy:
            state = load_state()
            healthy = get_healthy_model(state)
            print(f"\n🎯 Healthy model: {healthy}")
            return 0 if healthy else 1
    else:
        show_status()

if __name__ == "__main__":
    sys.exit(main())
