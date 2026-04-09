# CEO Failover System

**Dokumentation:** `2026-04-09`  
**Status:** 🔄 Implementiert

---

## Overview

Das Failover-System stellt sicher dass bei einem CEO-Ausfall ein Backup-Agent die Koordination übernimmt.

## Architektur

```
CEO (Primary)
    ↓ (3x missed heartbeat)
Security Officer (Primary Backup)
    ↓ (wenn Security auch down)
Builder (Secondary Backup)
    ↓ (wenn Builder auch down)
Data Manager (Tertiary Backup)
```

## Heartbeat-Verzeichnis

```
/home/clawbot/.openclaw/workspace/system/heartbeats/
├── ceo.json                    # CEO heartbeat
├── security_officer.json       # Security heartbeat
├── builder.json                # Builder heartbeat
├── data_manager.json          # Data Manager heartbeat
├── heartbeat.py                # Script zum Updaten
└── ceo_failover_monitor.py    # Failover-Monitor
```

## Backup-Kette

| Priorität | Agent | Rolle bei Failover |
|-----------|-------|-------------------|
| 1 | Security Officer | Übernimmt CEO wenn CEO 3x nicht heartbeatet |
| 2 | Builder | Übernimmt wenn Security auch down |
| 3 | Data Manager | Übernimmt wenn Builder auch down |

## Failover-Trigger

**Bedingung:** CEO heartbeatet 3x nicht (45 Minuten)

**Ablauf:**
1. `ceo_failover_monitor.py` läuft alle 15 Minuten
2. Prüft CEO heartbeat Alter
3. Bei 3x missed → Backup-Agent wird informiert
4. Backup-Agent startet Aufgaben-Annahme

## Recovery

**Wenn CEO wieder online:**
1. CEO heartbeat normal
2. Monitor erkennt Recovery
3. Backup-Agent wird benachrichtigt
4. Backup-Agent gibt CEO-Rechte zurück

## Cron-Jobs

### CEO Heartbeat (läuft im CEO Agent)
```
*/15 * * * * /home/clawbot/.openclaw/workspace/system/heartbeats/heartbeat.py ceo
```

### Failover Monitor (läuft auf System-Ebene)
```
*/15 * * * * /home/clawbot/.openclaw/workspace/system/heartbeats/ceo_failover_monitor.py
```

## Status-Prüfung

```bash
# Aktuellen Failover-Status anzeigen
cat /home/clawbot/.openclaw/workspace/system/heartbeats/failover_state.json
```

## Logs

```
/home/clawbot/.openclaw/workspace/system/heartbeats/
```

---

*Zuletzt aktualisiert: 2026-04-09*