# MODUL 01: Core Kernel

**Modul:** OpenClaw Gateway + CEO Agent
**Status:** ✅ Dokumentiert
**Letztes Update:** 2026-04-17

---

## 1.1 SYSTEM STACK

```
┌─────────────────────────────────────────────────────────┐
│  SIR HAZECLAW — AI AGENT SYSTEM                         │
├─────────────────────────────────────────────────────────┤
│  Gateway:       OpenClaw 2026.4.14 | ws://127.0.0.1:18789
│  Model:         MiniMax M2.7 (default)                  │
│  Node.js:       v22.22.2                                │
│  OS:            Linux 6.8.0-106-generic (x64)            │
│  Server:       srv1432586 | 8GB RAM | 96GB Storage     │
│  Communication: Telegram (Primary)                       │
└─────────────────────────────────────────────────────────┘
```

---

## 1.2 GATEWAY CONFIG

**Konfigurationsdatei:** `~/.openclaw/openclaw.json`

| Property | Wert | Notes |
|----------|------|-------|
| Version | 2026.4.14 | Aktuell (Update 2026.4.15 verfügbar) |
| Gateway Port | 18789 | Local loopback |
| Bind | loopback | Sicher, kein externer Zugriff |
| Trusted Proxies | leer | Da loopback, kein Problem |
| Auth Token | ✅ gesetzt | |

**Gateway Health:**
```bash
curl http://localhost:18789/health
# → {"ok":true,"status":"live"}
```

**Gateway Service:**
```bash
systemctl status openclaw
# → running (pid 476936, state active)
```

---

## 1.3 CEO AGENT

**Agent ID:** `ceo`
**Session:** `agent:ceo:telegram:direct:5392634979`

### Agent Konfiguration

| Property | Wert |
|----------|------|
| Model | minimax/MiniMax-M2.7 |
| Context | 205k tokens |
| Thinking | high |
| Capabilities | inlinebuttons |

### Agent Workspace

```
~/.openclaw/agents/ceo/
├── agent/
│   └── auth-profiles.json      # MINIMAX API Key (runtime)
├── sessions/
│   └── sessions.json          # 544 sessions
└── ...
```

### CEO Workspace

```
~/.openclaw/workspace/ceo/
├── SOUL.md                    # Persönlichkeit
├── USER.md                    # Nico's Profile
├── MEMORY.md                  # Langzeit-Gedächtnis
├── HEARTBEAT.md              # Status-Datei
├── IDENTITY.md               # "Sir HazeClaw"
├── TOOLS.md                  # Lokale Tool-Notes
├── AGENTS.md                 # Workspace-Regeln
├── memory/                   # Memory System
│   ├── short_term/          # Aktuelle Sessions
│   ├── long_term/           # Persistente Fakten
│   ├── episodes/            # Erlebnisse
│   ├── procedural/         # Skills/Wissen
│   ├── kg/                  # Knowledge Graph
│   ├── notes/               # Permanent Notes
│   └── ARCHIVE/             # Archiv
├── docs/                    # Dokumentation
│   └── architecture/        # Diese Dokumentation
└── skills/                  # Agent-Skills
```

---

## 1.4 API KEYS & SECRETS

### Speicherorte

| Ort | Zweck | Inhalt |
|-----|-------|--------|
| `secrets/secrets.env` | Langzeit-Backup | Alle API Keys |
| `agents/ceo/agent/auth-profiles.json` | **Runtime Key Store** | MINIMAX Key |

### Aktueller MINIMAX Key

```
Key ID: sk-cp-eQ6DbkJtxCAkw_zYabMlyK1B-...
Location: /home/clawbot/.openclaw/agents/ceo/agent/auth-profiles.json
```

### Environment Variables

Keys werden aus `secrets.env` zur Laufzeit geladen:
- `MINIMAX_API_KEY`
- `OPENROUTER_API_KEY`
- `GITHUB_TOKEN`
- etc.

---

## 1.5 KOMMUNIKATION

### Telegram (Primary)

| Property | Wert |
|----------|------|
| Chat ID | 5392634979 |
| Channel | telegram |
| Type | direct |

### Discord (Disabled)

| Property | Wert |
|----------|------|
| Channel | Discord |
| Token | In secrets.env |
| Status | ⚫ Disabled (kein Konto aktiv) |

---

## 1.6 SYSTEM RESSOURCEN

```bash
# CPU Load
0.27 (sehr gut)

# RAM
1.8/7.8 GB used, 5.9 GB available

# Disk
28/96 GB used (29%)

# Uptime
11 days, 16 hours
```

---

## 1.7 PLUGINS & EXTENSIONS

### Aktive Plugins

| Plugin | Status | Notes |
|--------|--------|-------|
| voice-call | ⚠️ Warning | Duplicate plugin ID — bundled wird von global überschrieben |

### Plugin Allowlist

```json
plugins.allow: empty
# → discovered non-bundled plugins may auto-load
```

---

## 1.8 SESSION MANAGEMENT

| Metric | Wert |
|-------|------|
| Total Sessions | 544 |
| Active Sessions | ? |
| Session Context | 205k tokens max |
| Memory Chunks | 334 |
| Memory Sources | memory (plugin memory-core) |

---

## 1.9 TASK MANAGEMENT

```bash
openclaw tasks list
```

| Metric | Wert |
|-------|------|
| Task Pressure | 0 queued, 0 running |
| Tracked Tasks | 3020 |
| Issues | 14 |

**Hinweis:** 3020 tracked tasks sind历史的 — die meisten sind abgeschlossen aber noch in der queue. 14 "issues" sind ebenfalls历史的.

---

## 1.10 BACKUP & RECOVERY

### Auto-Recovery

- **Cron:** Gateway Recovery Check alle 15 min
- **Script:** `gateway_recovery.py`
- **Was es tut:** Prüft Gateway Health, startet neu wenn DOWN

### Backups

| Backup | Schedule | Location |
|--------|----------|----------|
| Daily Auto Backup | 04:00 UTC | `backups/daily_backup_*/` |
| Weekly Backup | Sonntag 04:00 UTC | `backups/weekly_backup_*/` |
| Post-Integration | 2026-04-16 | `backups/post_integration_20260416_210413/` |

---

*Modul 01 — Core Kernel | Sir HazeClaw 🦞*
