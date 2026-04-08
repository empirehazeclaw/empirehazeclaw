# Lektion 8.1: OpenClaw Deployment & Operations (运维)

## Lernziele

- OpenClaw produktiv deployen und konfigurieren
- Gateway, Agents und Channels korrekt aufsetzen
- Config-Management mit JSON-Struktur meistern
- Logs und Status-Checks durchführen
- Häufige Operations-Probleme diagnostizieren und beheben
- Backup, Recovery und Monitoring implementieren

---

## 1. Architektur Überblick

### 1.1 Das OpenClaw System

```
┌─────────────────────────────────────────────────────────────┐
│                    OPENCLAW SYSTEM                          │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   GATEWAY   │  │   AGENTS     │  │   SESSIONS        │  │
│  │  Port:18789 │  │  (ceo,       │  │  (persistent,     │  │
│  │  Auth:Token │  │   builder...) │  │   subagent)       │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   CHANNELS  │  │   MEMORY     │  │   CRON/HB         │  │
│  │  (Telegram, │  │  (files,     │  │  (scheduled       │  │
│  │   Webchat)  │  │   sessions/) │  │   tasks)          │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Verzeichnis-Struktur

```
~/.openclaw/
├── openclaw.json          # Haupt-Config
├── gateway/               # Gateway-Logs
├── workspace/             # Agent Workspaces
│   ├── ceo/
│   ├── builder/
│   └── memory/
├── agents/                # Agent-Definitionen
│   ├── ceo/agent/
│   └── builder/agent/
├── extensions/            # Plugin-Extensions
├── tasks/                  # Cron-Task-Definitionen
└── memory/
    └── sessions/          # Session-State
```

---

## 2. Konfiguration (openclaw.json)

### 2.1 Hauptstruktur

```json
{
  "meta": {
    "lastTouchedVersion": "2026.4.5",
    "lastTouchedAt": "2026-04-06T19:51:52.882Z"
  },
  "models": {
    "providers": {
      "minimax": { ... },
      "openrouter": { ... }
    }
  },
  "agents": {
    "defaults": { ... },
    "list": [ ... ]
  },
  "channels": {
    "telegram": { ... }
  },
  "gateway": {
    "port": 18789,
    "bind": "loopback",
    "auth": { "mode": "token", "token": "..." }
  }
}
```

### 2.2 Agent-Definition

```json
{
  "id": "builder",
  "name": "Builder",
  "workspace": "/home/clawbot/.openclaw/workspace/builder",
  "agentDir": "/home/clawbot/.openclaw/agents/builder/agent",
  "model": {
    "primary": "openrouter/qwen/qwen3-coder:free"
  },
  "skills": ["coding", "backend-api", "frontend"],
  "sandbox": { "mode": "off" }
}
```

**Wichtige Felder:**
- `id` — Eindeutige Agent-ID (für Delegation wichtig)
- `workspace` — Arbeitsverzeichnis für Dateien
- `agentDir` — Agent-spezifische Configs
- `model` — Primärmodell + Fallbacks
- `skills` — Flaches Array von Skill-IDs
- `sandbox` — Sicherheitsmodus

### 2.3 Model-Config

```json
"models": {
  "providers": {
    "openrouter": {
      "baseUrl": "https://openrouter.ai/api/v1",
      "api": "openai-completions",
      "models": [
        {
          "id": "qwen/qwen3-coder:free",
          "name": "Qwen3 Coder 480B",
          "input": ["text"],
          "cost": { "input": 0, "output": 0 },
          "contextWindow": 262000,
          "maxTokens": 16384,
          "reasoning": true
        }
      ]
    }
  }
}
```

### 2.4 Channel-Config (Telegram)

```json
"channels": {
  "telegram": {
    "enabled": true,
    "dmPolicy": "allowlist",
    "botToken": "8397732232:AAE...",
    "allowFrom": ["5392634979"],
    "groupPolicy": "allowlist",
    "streaming": "partial"
  }
}
```

**Policies:**
- `allowlist` — Nur explizit erlaubte IDs
- `denylist` — Alle außer explizit verbannte
- `open` — Jeder darf (nicht empfohlen)

---

## 3. Gateway Operations

### 3.1 Gateway starten/stoppen

```bash
# Status prüfen
openclaw gateway status

# Starten
openclaw gateway start

# Stoppen
openclaw gateway stop

# Neustart
openclaw gateway restart
```

### 3.2 Gateway-Konfiguration

```json
"gateway": {
  "port": 18789,
  "mode": "local",
  "bind": "loopback",
  "auth": {
    "mode": "token",
    "token": "6d1e9bb224ed1d86ba219e0ca6bc3f63715524d960e158b5"
  },
  "tailscale": { "mode": "off" },
  "nodes": {
    "denyCommands": [
      "camera.snap",
      "sms.send"
    ]
  }
}
```

**bind-Optionen:**
- `loopback` — Nur localhost (sicher)
- `0.0.0.0` — Alle Interfaces (vorsicht!)

### 3.3 Auth-Modi

| Modus | Beschreibung |
|-------|---------------|
| `token` | Token in Config, wird bei Requests mitgesendet |
| `none` | Keine Auth (nur für Tests) |
| `tailscale` | Tailscale-NetAuth |

---

## 4. Agent Operations

### 4.1 Agent-Management

```bash
# Alle Agenten auflisten
openclaw agents list

# Agent-Config prüfen
openclaw doctor --agent builder

# Agent-Session starten
openclaw session start --agent builder
```

### 4.2 Session-Typen

| Typ | Beschreibung | Use-Case |
|-----|--------------|----------|
| `main` | Hauptkonversation | Normale Chats |
| `isolated` | Komplett abgeschirmt | Sensitive Ops |
| `subagent` | Temporärer Child-Agent | Delegation |
| `acp` | ACP-Harness | Codex/Cursor |

### 4.3 Agent-Delegation

```bash
# Anfrage an Agent senden
openclaw exec --agent builder -- "echo hello"

# Session-ID herausfinden
openclaw sessions list --agent builder

# Direkt Message senden
openclaw message --session <id> -- "Task für dich"
```

---

## 5. Troubleshooting

### 5.1 Häufige Fehler

**Fehler: "Config invalid"**
```
Problem: agents.list.0: Unrecognized key: "systemPrompt"
Fix: systemPrompt ist kein gültiger Key — Identity kommt aus SOUL.md
```

**Fehler: "Gateway refused connection"**
```bash
# Prüfe ob Gateway läuft
openclaw gateway status

# Logs prüfen
tail -f ~/.openclaw/logs/gateway.log

# Port prüfen
ss -tlnp | grep 18789
```

**Fehler: "Model not found"**
```bash
# Verfügbare Modelle prüfen
openclaw models list

# Config-Validierung
openclaw doctor --fix
```

**Fehler: "Session not found"**
```bash
# Aktive Sessions
openclaw sessions list

# Session-History
openclaw sessions history <session_id>
```

### 5.2 Config-Validierung

```bash
# Doctor-Modus (prüft + fix)
openclaw doctor

# Nur prüfen
openclaw doctor --check

# Automatisch fixen
openclaw doctor --fix
```

### 5.3 Logging

```bash
# Gateway-Logs live
tail -f ~/.openclaw/logs/gateway.log

# Alle Logs
ls -la ~/.openclaw/logs/

# Log-Level setzen (in Config)
"logging": { "level": "debug" }
```

---

## 6. Backup & Recovery

### 6.1 Wichtige Dateien sichern

```bash
# Backup-Script
#!/bin/bash
BACKUP_DIR="/opt/backups/openclaw"
DATE=$(date +%Y%m%d_%H%M%S)

# Config sichern
cp ~/.openclaw/openclaw.json $BACKUP_DIR/config_$DATE.json

# Memory sichern
tar -czf $BACKUP_DIR/memory_$DATE.tar.gz ~/.openclaw/memory/

# Workspace sichern
tar -czf $BACKUP_DIR/workspace_$DATE.tar.gz ~/.openclaw/workspace/

# Agent-Configs sichern
tar -czf $BACKUP_DIR/agents_$DATE.tar.gz ~/.openclaw/agents/
```

### 6.2 Restore

```bash
# Config wiederherstellen
cp /opt/backups/openclaw/config_20260406_120000.json ~/.openclaw/openclaw.json

# Gateway neu starten
openclaw gateway restart
```

### 6.3 Datenbank-Backup (Memory)

```bash
# Session-State sichern
cp -r ~/.openclaw/memory/sessions/ /opt/backups/sessions/

# Lossless-Claw History
cp -r ~/.openclaw/memory/lossless/ /opt/backups/lossless/
```

---

## 7. Monitoring & Health Checks

### 7.1 System-Health

```bash
# Kompletter Health-Check
openclaw status

# Gateway-Status
openclaw gateway status

# Agent-Status
openclaw agents list
```

### 7.2 Automatische Health Checks (Cron)

```python
#!/usr/bin/env python3
# health_check.py — OpenClaw Health Monitor

import subprocess
import json
from datetime import datetime

def check_gateway():
    result = subprocess.run(
        ["openclaw", "gateway", "status"],
        capture_output=True, text=True
    )
    return result.returncode == 0

def check_agents():
    result = subprocess.run(
        ["openclaw", "agents", "list"],
        capture_output=True, text=True
    )
    return result.returncode == 0

def main():
    status = {
        "timestamp": datetime.utcnow().isoformat(),
        "gateway": check_gateway(),
        "agents": check_agents()
    }
    
    if not all(status.values()):
        # Alert senden
        print(f"⚠️ Health Check Failed: {status}")
    else:
        print(f"✅ Alles OK: {status}")
    
    return 0 if all(status.values()) else 1

if __name__ == "__main__":
    exit(main())
```

### 7.3 Heartbeat-Config

```json
"hooks": {
  "internal": {
    "enabled": true,
    "entries": {
      "heartbeat": {
        "enabled": true,
        "interval": 300
      }
    }
  }
}
```

---

## 8. Production Checklist

### 8.1 Pre-Deployment

- [ ] Config validiert (`openclaw doctor --fix`)
- [ ] Alle Agents getestet
- [ ] Channels konfiguriert (Telegram Bot-Token)
- [ ] Auth-Token generiert und sicher gespeichert
- [ ] Backup-Strategie definiert

### 8.2 Post-Deployment

- [ ] Gateway läuft (`openclaw gateway status`)
- [ ] Health-Check-Script aktiv
- [ ] Logs werden rotiert
- [ ] Monitoring aktiv
- [ ] Alerting konfiguriert

### 8.3 Security Hardening

- [ ] `bind: loopback` (nicht 0.0.0.0)
- [ ] Starkes Gateway-Token
- [ ] Telegram allowlist aktiv
- [ ] Dangerous Commands in denyList
- [ ] Sandbox-Modus wo möglich

---

## 9. Übungsfragen

### Frage 1: Config-Management
Welcher Key ist **nicht** gültig in einer Agent-Definition?
- a) `id`
- b) `workspace`
- c) `systemPrompt`
- d) `sandbox`

<details>
<summary>Antwort</summary>
**c) systemPrompt** — Identity/Prompt kommt aus SOUL.md, nicht aus der Config.
</details>

### Frage 2: Gateway
Was tut der Befehl `openclaw gateway restart`?
- a) Löscht alle Sessions
- b) Liest Config neu und startet Gateway-Prozess neu
- c) Updatet die Config-Version
- d) Startet einen neuen Agenten

<details>
<summary>Antwort</summary>
**b)** — Gateway wird gestoppt, Config neu gelesen, Gateway wieder gestartet.
</details>

### Frage 3: Troubleshooting
Der Gateway startet nicht mit Fehler "Config invalid". Was prüfst du zuerst?
- a) Log-Dateien
- b) `openclaw doctor --fix`
- c) Netzwerk-Port
- d) Model-Provider

<details>
<summary>Antwort</summary>
**b)** — `doctor --fix` zeigt und behebt Config-Probleme automatisch.
</details>

### Frage 4: Operations
Du willst einen Backup aller Workspaces. Welcher Befehl ist korrekt?
- a) `tar -czf backup.tar ~/.openclaw/workspace/`
- b) `cp -r ~/.openclaw/workspace /backup/`
- c) Beide sind korrekt
- d) Nur via openclaw CLI

<details>
<summary>Antwort</summary>
**c)** — Beide funktionieren. `tar` ist komprimierter, `cp` simpler.
</details>

### Frage 5: Security
Welche `bind`-Einstellung ist für Production sicherer?
- a) `0.0.0.0`
- b) `loopback`
- c) `192.168.1.1`
- d) `255.255.255.255`

<details>
<summary>Antwort</summary>
**b) loopback** — Bindet nur an localhost, kein externer Zugriff möglich.
</details>

---

## 10. Zusammenfassung

| Thema | Key-Commands |
|-------|--------------|
| **Gateway** | `openclaw gateway start/stop/restart/status` |
| **Config** | `openclaw doctor --fix` |
| **Agents** | `openclaw agents list`, `sessions list` |
| **Logs** | `tail -f ~/.openclaw/logs/gateway.log` |
| **Backup** | `tar -czf`, `cp -r` |
| **Health** | `openclaw status`, `health_check.py` |

**Merke:** OpenClaw Operations folgen dem Prinzip — Config as Code. Alles in `openclaw.json`, Workspaces und Agents als Dateien. Keine magical State, alles reproduzierbar.

---

*Ende Lektion 8.1*
