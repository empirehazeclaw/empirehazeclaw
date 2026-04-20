# Self-Healing Plugin Analyse

**Datum:** 2026-04-12
**Status:** NICHT INTEGRATIONSFÄHIG (Version Mismatch)

---

## Was das Plugin kann (laut Doku):

### Features:
| Feature | Beschreibung |
|---------|-------------|
| Model Failover | Bei rate limit → fallback model |
| WhatsApp Reconnect | Auto-restart bei disconnect |
| Cron Failure | Auto-disable + GitHub issue |
| Plugin Crash | Auto-disable |
| Config Validation | Validiert before changes |

### Config Schema:
```json
{
  "openclaw-self-healing": {
    "enabled": true,
    "config": {
      "modelOrder": ["minimax/MiniMax-M2.7", "..."],
      "cooldownMinutes": 300,
      "dryRun": false,
      "autoFix": {
        "patchSessionPins": true,
        "disableFailingPlugins": false,
        "disableFailingCrons": false,
        "issueRepo": "owner/repo"
      }
    }
  }
}
```

---

## Problem: Version Mismatch

### Fehler:
```
plugins.entries.openclaw-self-healing-elvatis: 
  Unrecognized keys: "dryRun", "modelOrder", "cooldownMinutes", "autoFix"
```

### Mögliche Ursachen:
1. Plugin erwartet **neuere OpenClaw Version** (2026.4.x)
2. Plugin Schema ist **nicht kompatibel** mit aktueller Config-Validierung
3. Plugin ID in `openclaw.plugin.json` = `openclaw-self-healing-elvatis`
4. README nutzt aber `openclaw-self-healing` → Inkonsistenz

### Getestete Configs:
| Config Name | Ergebnis |
|-------------|----------|
| `openclaw-self-healing` + nested config | Plugin not found |
| `openclaw-self-healing` flat | Plugin not found |
| `openclaw-self-healing-elvatis` nested config | Config invalid |
| `openclaw-self-healing-elvatis` flat | Config invalid |

---

## Plugin Interna (von GitHub):

### Status File:
- Path: `~/.openclaw/workspace/memory/self-heal-status.json`
- Written alle 60s
- Enthält: health, activeModel, models[], whatsapp, cron

### State File:
- Path: `~/.openclaw/workspace/memory/self-heal-state.json`
- Persisted zwischen restarts

### Monitor Loop:
- Alle 60s: Status check
- Alle 300s: Model probe
- Bei failure: Cooldown oder failover

---

## Können wir es selber bauen?

### Was wir BRAUCHEN:
| Komponente | Implementierung |
|------------|----------------|
| Model Health Check | Script das API response prüft |
| Rate Limit Detection | Response code / headers check |
| Auto-Failover | Session pins ändern |
| Cooldown Tracking | State file mit timestamps |
| Cron Failure Detection | Cron status prüfen |
| Auto-Disable | openclaw cron disable |

### Was wir SCHON HABEN:
- ✅ `cron_error_healer.py` — erkennt Cron failures
- ✅ `self-heal-state.json` structure (aber kein writer)
- ✅ Gateway status monitoring
- ✅ Model fallback mechanism (in our scripts)

### Was FEHLT:
- ❌ Zentrales monitoring (alle 60s)
- ❌ Model health probing
- ❌ Cooldown manager
- ❌ Config backup vor changes
- ❌ GitHub issue creation

---

## Vorschlag: Eigenes Self-Healing Script

```python
#!/usr/bin/env python3
"""
self_healing_monitor.py - Eigenes Self-Healing System
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta

STATE_FILE = Path("~/.openclaw/workspace/memory/self-heal-state.json")
STATUS_FILE = Path("~/.openclaw/workspace/memory/self-heal-status.json")
CONFIG_FILE = Path("~/.openclaw/openclaw.json")

MODEL_ORDER = ["minimax/MiniMax-M2.7", "openai/gpt-4o-mini"]
COOLDOWN_MINUTES = 60
PROBE_INTERVAL_SEC = 300

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"models": {}, "cooldowns": {}}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def check_model_health(model_id):
    """Check if model is available (probe request)."""
    # TODO: Implement health check
    pass

def probe_models():
    """Alle Models checken und status aktualisieren."""
    state = load_state()
    for model_id in MODEL_ORDER:
        if model_id not in state["models"]:
            state["models"][model_id] = {"status": "available"}
        
        # Check health
        is_healthy = check_model_health(model_id)
        
        if not is_healthy:
            state["models"][model_id]["status"] = "cooldown"
            state["models"][model_id]["cooldown_reason"] = "health_check_failed"
            state["models"][model_id]["cooldown_until"] = (
                datetime.now() + timedelta(minutes=COOLDOWN_MINUTES)
            ).isoformat()

def get_active_model():
    """Hole erstes verfügbares Model."""
    state = load_state()
    for model_id in MODEL_ORDER:
        model_state = state["models"].get(model_id, {})
        if model_state.get("status") != "cooldown":
            return model_id
    return MODEL_ORDER[0]  # Fallback

def main():
    state = load_state()
    probe_models()
    save_state(state)
    
    active = get_active_model()
    print(f"Active model: {active}")

if __name__ == "__main__":
    main()
```

---

## Fazit:

| Option | Info |
|--------|------|
| **Plugin** | ❌ Version mismatch, nicht lauffähig |
| **Eigenbau** | ✅ Machbar, ca. 200 Zeilen Python |
| **Priorität** | 🟡 Mittel — cron_error_healer macht das meiste schon |

---

*Nico entscheidet: Plugin fixen lassen ODER Eigenbau*
