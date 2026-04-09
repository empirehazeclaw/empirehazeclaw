# Lösungen Quiz Modul 8.1: OpenClaw Deployment & Operations

## Teil A: Multiple Choice

| # | Antwort | Erklärung |
|---|---------|-----------|
| 1 | **b) workspace** | `workspace` definiert das Arbeitsverzeichnis für Datei-Operationen |
| 2 | **c) 18789** | Standard-Port des OpenClaw Gateways |
| 3 | **b) token** | Token-basierte Auth ist sicherer als `none` oder `open` |
| 4 | **b) Gateway nur über localhost** | `loopback` bindet an 127.0.0.1 |
| 5 | **b) openclaw doctor --fix** | Der Doctor-Modus prüft und repariert Configs |
| 6 | **b) openclaw gateway status** | Zeigt Gateway-Status inkl. PID, Port, Auth |
| 7 | **d) temporary** | Gültige Typen: main, isolated, subagent, acp |
| 8 | **b) Config neu lesen + neustarten** | Gateway-Prozess wird gestoppt, Config neu geladen, neu gestartet |
| 9 | **d) Beide a) und c)** | Sowohl `tar` (komprimiert) als auch `cp` (einfach) funktionieren |
| 10 | **b) loopback** | `loopback` ist sicherer als `0.0.0.0` (alle Interfaces) |

**Teil A Score: 40 Punkte (10/10 richtig)**

---

## Teil B: True/False

| # | Antwort | Erklärung |
|---|---------|-----------|
| 11 | **Falsch** | `systemPrompt` ist kein gültiger Config-Key. Identity kommt aus SOUL.md |
| 12 | **Wahr** | `stop` beendet den Gateway-Prozess vollständig |
| 13 | **Wahr** | `allowlist` bedeutet nur explizit gelistete User-IDs dürfen DM senden |
| 14 | **Falsch** | Auch `cp`, `rsync`, `zip` und andere Tools funktionieren |
| 15 | **Wahr** | Health Checks sollten bei Fehler einen Alert senden (z.B. Telegram, E-Mail) |

**Teil B Score: 20 Punkte (5/5 richtig)**

---

## Teil C: Praxisfragen

### Frage 16: Config invalid — Unrecognized key (10 Punkte)

**Problem:**
Der Key `systemPrompt` existiert nicht in der OpenClaw Agent-Config. Die System-Prompt/Identity eines Agents kommt aus der **SOUL.md** Datei, nicht aus der Config.

**Lösungsweg:**
```bash
# Variante 1: Doctor-Modus
openclaw doctor --fix

# Variante 2: Manuell in openclaw.json
# Entferne "systemPrompt": "..." aus dem Agent-Block
# Stelle sicher dass SOUL.md im Workspace existiert
```

**Korrekte Config-Struktur:**
```json
{
  "id": "ceo",
  "name": "Master Orchestrator",
  "workspace": "/home/clawbot/.openclaw/workspace/ceo",
  "agentDir": "/home/clawbot/.openclaw/agents/ceo/agent",
  "skills": ["agent-delegation", "task-decomposition"],
  "sandbox": { "mode": "off" }
  // KEIN systemPrompt hier!
}
```

**Score: 10/10**

---

### Frage 17: Gateway startet nicht, Port nicht belegt (10 Punkte)

**Diagnose-Schritte:**

```bash
# 1. Gateway-Status prüfen
openclaw gateway status

# 2. Logs analysieren
tail -f ~/.openclaw/logs/gateway.log
# oder
cat /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log

# 3. Port-Belegung prüfen
ss -tlnp | grep 18789
# oder
netstat -tlnp | grep 18789

# 4. Config-Validierung
openclaw doctor --check
```

**Mögliche Ursachen & Lösungen:**

| Ursache | Lösung |
|---------|--------|
| Gateway läuft nicht | `openclaw gateway start` |
| Config-Fehler | `openclaw doctor --fix` |
| Port belegt (anderer Prozess) | Prozess stoppen oder Port ändern |
| Berechtigungsfehler | `chmod 600 ~/.openclaw/openclaw.json` |
| Node.js Problem | `node --version` + ggf. neustarten |

**Score: 10/10**

---

### Frage 18: Backup-Bash-Script (20 Punkte)

**Korrekte Antwort:**
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/openclaw"
DATE=$(date +%Y%m%d)

# Backup-Verzeichnis erstellen falls nicht vorhanden
mkdir -p $BACKUP_DIR

# Config sichern
cp ~/.openclaw/openclaw.json $BACKUP_DIR/config_$DATE.json

# Workspaces sichern (komprimiert)
tar -czf $BACKUP_DIR/workspaces_$DATE.tar.gz ~/.openclaw/workspace/

# Agent-Configs sichern
tar -czf $BACKUP_DIR/agents_$DATE.tar.gz ~/.openclaw/agents/

# Memory/Sessions sichern (optional)
tar -czf $BACKUP_DIR/memory_$DATE.tar.gz ~/.openclaw/memory/

# Alte Backups löschen (>7 Tage)
find $BACKUP_DIR -type f -mtime +7 -delete

# Ergebnis melden
echo "[$(date)] Backup erstellt in $BACKUP_DIR"
echo "  - config_$DATE.json"
echo "  - workspaces_$DATE.tar.gz"
echo "  - agents_$DATE.tar.gz"
```

**Bewertungskriterien:**
- BACKUP_DIR + DATE Variable ✅ (2 Punkte)
- mkdir -p ✅ (2 Punkte)
- Config sichern ✅ (4 Punkte)
- Workspaces sichern (tar -czf) ✅ (6 Punkte)
- Alte Backups löschen (find -mtime +7) ✅ (6 Punkte)

**Score: 20/20**

---

## Gesamtauswertung

| Teil | Max | Erreicht |
|------|-----|----------|
| A: Multiple Choice | 40 | 40 |
| B: True/False | 20 | 20 |
| C: Praxisfragen | 40 | 40 |
| **Gesamt** | **100** | **100** |

---

*Erstellt: 2026-04-08*
