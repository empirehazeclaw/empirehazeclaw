# ⏱️ TIMEOUT VERBESSERUNGEN — Implementiert 2026-04-09 23:40 UTC

---

## ✅ KONFIGURATION (Gateway Config)

| Setting | Alter Wert | Neuer Wert | Effekt |
|---------|-----------|------------|--------|
| `agents.defaults.maxConcurrent` | 4 | **8** | Mehr parallele Tasks |
| `agents.defaults.timeoutSeconds` | 30 | **60** | Längere Agent-Timeouts |
| `agents.defaults.subagents.maxConcurrent` | 8 | **8** | (unverändert) |
| `agents.defaults.subagents.runTimeoutSeconds` | 30 | **300** | 5min für Background-Tasks |
| `agents.defaults.heartbeat.every` | 30m | **15m** | Schnellere Heartbeats |

---

## 🔄 OFFENE IMPLEMENTIERUNGEN

### Custom Lanes (NICHT UNTERSTÜTZT)
- **GitHub Issue:** `#16055` — maxConcurrent propagiert nicht
- **Schema:** `lane` und `laneConcurrency` werden NICHT unterstützt
- **Status:** Warten auf OpenClaw Update

### Sessions_send Fire-and-Forget
- **Status:** SOUL.md Updates nötig
- **Pattern:** `timeoutSeconds: 0` für Notifications
- **Befehl:** Alle SOUL.md aktualisieren

---

## 📋 SOUL.md UPDATE (Broadcast an alle Agenten)

```
Timeout-Handling Update (2026-04-09):

REGEL 1: Fire-and-Forget Notifications
- Nutze: sessions_send(timeoutSeconds: 0)
- Beispiel: message() für Discord/Telegram Notifications
- Kein Warten auf Antwort

REGEL 2: Background Tasks
- Nutze: sessions_spawn(runtime: "subagent", runTimeoutSeconds: 300)
- Non-blocking, Ergebnis kommt als Event

REGEL 3: Auf Antwort warten
- Nutze: sessions_send(timeoutSeconds: 30)
- Nur wenn Antwort wirklich nötig

REGEL 4: Cron Jobs
- Nutze: sessionTarget: "isolated" für lange Tasks
- Timeout: 30s default, 120s für Builder
```

---

## 📝 TICKET FÜR OPENC LAW

```
Title: Custom Lanes pro Agent unterstützen
Issue: GitHub #16055
Status: Offen
Feature: agents.list[].lane + laneConcurrency
Workaround: Custom Lanes via agents.defaults.maxConcurrent
```

---

*Erstellt: 2026-04-09 23:40 UTC*
*CEO Sir HazeClaw*