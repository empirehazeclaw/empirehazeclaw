# Lektion 10: Scheduling & Cron

## 🎯 Lernziel
Verstehe das Cron-System, Heartbeats und Checkpoints. Automatisierung macht den Unterschied zwischen einer funktionierenden und einer großartigen Flotte.

---

## 10.1 Das Prinzip

```
MANUELL:     Nico muss dich every time erinnern
             → Fehleranfällig, zeitaufwändig

AUTOMATISCH: System erinnert sich selbst
             → Zuverlässig, skalierbar
```

---

## 10.2 Cron — Das OpenClaw Scheduling

### Grundkonzepte

```javascript
// Cron-Job erstellen
cron({
  action: "add",
  job: {
    name: "Daily Backup",
    schedule: { kind: "cron", expr: "0 2 * * *" },
    payload: { kind: "agentTurn", message: "Führe Backup durch..." }
  }
})
```

### Cron-Expression lesen

```
┌───────────── Minute (0-59)
│ ┌───────────── Stunde (0-23)
│ │ ┌───────────── Tag (1-31)
│ │ │ ┌───────────── Monat (1-12)
│ │ │ │ ┌───────────── Wochentag (0-7, 0 und 7 = Sonntag)
│ │ │ │ │
* * * * *
```

### Beispiele

| Expression | Bedeutung |
|------------|-----------|
| `0 * * * *` | Jede Stunde zur vollen Stunde |
| `0 0 * * *` | Täglich um Mitternacht |
| `0 9 * * 1-5` | Mo-Fr um 09:00 |
| `0 18 * * 0` | Sonntag um 18:00 |
| `30 4 * * *` | Täglich um 04:30 |
| `0 */6 * * *` | Alle 6 Stunden |
| `0 9,17 * * *` | 09:00 und 17:00 täglich |

---

## 10.3 Schedule-Typen

### cron — Wiederkehrend
```javascript
schedule: { kind: "cron", expr: "0 9 * * *" }
```

### at — Einmalig
```javascript
schedule: { kind: "at", at: "2026-04-15T10:00:00Z" }
```

### every — Intervall
```javascript
schedule: { kind: "every", everyMs: 3600000 } // Jede Stunde
```

---

## 10.4 Payload-Typen

### agentTurn — Agent-Task
```javascript
payload: {
  kind: "agentTurn",
  message: "Führe Security Audit durch...",
  timeoutSeconds: 1800
}
```

### systemEvent — System-Event
```javascript
payload: {
  kind: "systemEvent",
  text: "HEARTBEAT_TRIGGER"
}
```

---

## 10.5 Session-Targets

| Target | Beschreibung |
|--------|--------------|
| `main` | Hauptsession (nur systemEvent) |
| `isolated` | Isolierte Einmal-Session |
| `current` | Aktuelle Session |
| `session:xyz` | Bestimmte Session |

```javascript
sessionTarget: "isolated"  // Für Cron-Jobs am besten
```

---

## 10.6 Delivery — Ergebnisse senden

### announce — An Channel senden
```javascript
delivery: {
  mode: "announce",
  channel: "telegram",
  to: "5392634979"
}
```

### webhook — HTTP POST
```javascript
delivery: {
  mode: "webhook",
  to: "https://my-server.com/webhook"
}
```

### none — Kein Delivery
```javascript
delivery: { mode: "none" }  // Nur Ergebnis speichern
```

---

## 10.7 Aktive Crons der Flotte

### System-Crons

| Job | Schedule | Funktion |
|-----|----------|----------|
| sqlite_vacuum | 03:00 UTC | Datenbank optimieren |
| session_cleanup | 04:00 UTC | Alte Sessions löschen |
| kg_auto_populate | 06:00 UTC | Knowledge Graph füllen |
| semantic_search | 06:00 UTC | Semantische Suche |

### Agent-Crons

| Job | Schedule | Funktion |
|-----|----------|----------|
| CEO Briefing | 09:00 UTC (Berlin) | Daily Status |
| Flashcards | 09:00 UTC | Lern-Karten |
| Security Officer | 10:00 UTC | Daily Audit |
| Data Manager | 11:31 UTC | Daily Check |
| Research | 13:00 UTC | Daily Research |
| University Loop | So 18:00 UTC | Self-Improvement |
| Agent Training | So 19:00 UTC | Agent-Zertifizierung |

---

## 10.8 Heartbeat — Das Lebenszeichen

### Wann?

```
Heartbeat = Kurzes "Ich lebe noch" Signal

BEVOR ein langer Task startet:  Heartbeat
NACH einem Task:                  Status-Report
BEI Problemen:                    Warning
AUF ANFRAGE:                     Vollständiger Status
```

### Heartbeat als System

```
Cron feuert alle 5 Min
    │
    ▼
OpenClaw sendet HEARTBEAT
    │
    ▼
Agent liest HEARTBEAT.md
    │
    ▼
Check: Gibt es was zu tun?
    │
    ▼
JA → Task ausführen
NEIN → "HEARTBEAT_OK"
```

---

## 10.9 Checkpoint — Fortschritt sichern

### Checkpoint-Datei

```markdown
## Checkpoint — 2026-04-08T17:30:00Z

### Laufender Task
- Task: Backup-Script
- Fortschritt: 80%
- Gestartet: 17:00 UTC
- Erwartet fertig: 17:45 UTC

### Letzte Aktion
- Retention-Policy implementiert
- Logging hinzugefügt

### Nächste Aktion
- Testen des Scripts

### Blocker
- Keine
```

### Checkpoint-Regeln

```
1. Schreibe Checkpoint BEVOR du den Status vergessen könntest
2. Checkpoint enthält: Was, Wo, Wann, Nächste Schritte
3. Bei Recovery: Checkpoint lesen, nicht raten
4. Checkpoint ist KEIN Ersatz für Report
```

---

## 10.10 Wake Modes

### now — Sofort aufwecken
```javascript
wakeMode: "now"  // Trigger feuert sofort
```

### next-heartbeat — Beim nächsten Heartbeat
```javascript
wakeMode: "next-heartbeat"  // Standard
```

---

## 10.11 Failure Alerts

### Cron-Job überwachen

```javascript
cron({
  action: "add",
  job: {
    name: "Critical Backup",
    schedule: { kind: "cron", expr: "0 2 * * *" },
    failureAlert: {
      after: 3,  // Nach 3 Fehlern
      channel: "telegram",
      to: "5392634979"
    }
  }
})
```

### Cooldown

```javascript
failureAlert: {
  after: 3,
  cooldownMs: 3600000,  // 1 Stunde zwischen Alerts
  ...
}
```

---

## 10.12 Cron Job verwalten

### list — Alle Jobs anzeigen
```javascript
cron({ action: "list" })
```

### run — Sofort ausführen
```javascript
cron({ action: "run", jobId: "job-id-hier" })
```

### runs — History anzeigen
```javascript
cron({ action: "runs", jobId: "job-id-hier" })
```

### remove — Löschen
```javascript
cron({ action: "remove", jobId: "job-id-hier" })
```

---

## 10.13 Best Practices

### DO's
```
✅ Nutze ISO-Zeiten für at-Schedules
✅ Setze failureAlert für kritische Jobs
✅ Nutze "isolated" für Cron-Jobs
✅ Schreibe Checkpoints bei langen Tasks
✅ Teste Cron-Jobs manuell mit "run"
```

### DON'Ts
```
❌ Cron-Jobs die sich selbst ändern (Loop-Gefahr)
❌ Cron alle 5 Sekunden (Overload)
❌ Keine Timeouts setzen (Runaway Jobs)
❌ Vergessen failureAlert zu setzen
❌ Cron für alles — manche Tasks sind besser manuell
```

---

## 10.14 Anti-Patterns

### Zu oft
```javascript
// ❌ JEDE SEKUNDE
schedule: { kind: "every", everyMs: 1000 }

// ✅ MINIMAL 1 MINUTE
schedule: { kind: "every", everyMs: 60000 }
```

### Kein Timeout
```javascript
// ❌ OHNE TIMEOUT
payload: { kind: "agentTurn", message: "..." }  // Läuft ewig!

// ✅ MIT TIMEOUT
payload: { kind: "agentTurn", message: "...", timeoutSeconds: 300 }
```

---

## 📝 Zusammenfassung

| Konzept | Beschreibung |
|---------|--------------|
| cron | Wiederkehrende Schedules (cron expr) |
| at | Einmalige Zeit (ISO timestamp) |
| every | Intervall in Millisekunden |
| isolated | Beste Session-Type für Cron |
| delivery | Wie Ergebnis zugestellt wird |
| Heartbeat | Regelmäßiges Lebenszeichen |
| Checkpoint | Fortschritt sichern |
| failureAlert | Alarm bei wiederholten Fehlern |

---

## ✅ Checkpoint

- [ ] Was bedeutet "0 9 * * * *" in Cron?
- [ ] Was ist der Unterschied zwischen "at" und "cron"?
- [ ] Warum ist "isolated" der beste Session-Target für Cron?
- [ ] Wann solltest du einen Checkpoint schreiben?
- [ ] Was ist der Unterschied zwischen wakeMode "now" und "next-heartbeat"?

---

*Lektion 10 — Scheduling & Cron — Version 1.0*
