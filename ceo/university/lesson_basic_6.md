# Lektion 6: Reporting & Kommunikation

## 🎯 Lernziel
Verstehe das Reporting-System der Flotte. Lerne task_reports, Heartbeats und wie du Nico effektiv über Fortschritt informierst.

---

## 6.1 Das Prinzip: Kein Schweigen!

### Warum Reporting?

```
Nico kann nicht lesen was in deinem Kopf passiert.
Wenn du nicht berichtest, weiß Nico nicht:
- Was gerade läuft
- Was fertig ist
- Wo Probleme sind
```

**Jeder Agent muss regelmäßig berichten.** Kein Task gilt als fertig ohne Report.

---

## 6.2 task_report.json — Das Standard-Format

### Struktur
```json
{
  "agent": "builder",
  "timestamp": "2026-04-08T17:30:00Z",
  "task_id": "backup-script-creation",
  "status": "done",
  "findings": [
    "Backup-Script erstellt",
    "Tar mit gzip-Komprimierung",
    "7-Tage-Rotation implementiert"
  ],
  "next_actions": [],
  "artifacts": [
    {
      "path": "/home/clawbot/.openclaw/workspace/builder/backup.sh",
      "size_bytes": 1247
    }
  ]
}
```

### Status-Werte

| Status | Bedeutung |
|--------|-----------|
| `in_progress` | Arbeit hat begonnen |
| `done` | Vollständig abgeschlossen |
| `warning` | Probleme, aber noch im Gang |
| `error` | Fehlgeschlagen |
| `blocked` | Wartet auf etwas |

---

## 6.3 Heartbeat — Das Lebenszeichen

### Was ist ein Heartbeat?

```
Regelmäßige kurze Status-Meldung:
"HEARTBEAT_OK" → System lebt noch
```

### Wann Heartbeat?

| Zeitpunkt | Inhalt |
|-----------|--------|
| Beim Aufwachen | "Gestartet, prüfe Tasks..." |
| Nach Task-Abusch | Kurzes "Done: X" |
| Bei Problemen | "WARNUNG: Problem bei..." |
| Auf Anfrage | Vollständiger Status-Report |

### Heartbeat-Beispiel
```
HEARTBEAT_OK

Aktive Tasks:
- Backup-Script: ✅ Fertig
- Security Audit: ⏳ Läuft (30%)
- Quiz: ⏳ Wartet auf Builder

Nächste Aktion: Security Audit abschließen
```

---

## 6.4 Reporting an Nico

### Kanäle

| Kanal | Wann nutzen |
|-------|-------------|
| Telegram (message) | Normale Updates, Fragen |
| Inline Response | Direkte Antworten |
| Cron-Delivery | Automatische Reports |

### Struktur für Nico-Updates

```
📊 **STATUS-UPDATE** — 17:30 UTC

## Erledigt ✅
- Backup-Script erstellt (backup.sh)
- Quiz Module 3 abgeschlossen (100/100)

## Läuft ⏳
- Security Audit: 50% fertig

## Blocker 🔴
- Secrets-Key fehlt noch

## Nächste Schritte
1. Security Audit finalisieren
2. GitHub Backup aktivieren
```

---

## 6.5 QC Officer — Validation Layer

### Der QC Officer validiert:
- Ist der Task wirklich fertig?
- Entspricht das Ergebnis der Spezifikation?
- Gibt es Security-Probleme?
- Ist der Report vollständig?

### QC-Workflow
```
CEO ──► Task an Builder ──► Builder Report ──► CEO
                                                │
                                                ▼
                                         QC Officer
                                                │
                                                ▼
                                         QC Report
                                                │
                                                ▼
                                         CEO informiert Nico
```

### QC-Report-Beispiel
```json
{
  "agent": "qc_officer",
  "task_id": "backup-script-review",
  "result": "PASSED",
  "findings": [
    "Script funktioniert korrekt",
    "Keine Security-Probleme gefunden",
    "Dokumentation vollständig"
  ],
  "issues": [],
  "recommendation": "APPROVED"
}
```

---

## 6.6 Fehlerberichte

### Error-Report-Struktur

```json
{
  "agent": "builder",
  "timestamp": "2026-04-08T17:45:00Z",
  "task_id": "backup-script-test",
  "status": "error",
  "error": {
    "type": "PermissionDenied",
    "message": "Cannot write to /opt/backups",
    "stack": "..."
  },
  "findings": [
    "Backup-Verzeichnis existiert nicht",
    "Keine Schreibrechte für /opt"
  ],
  "next_actions": [
    "Verzeichnis erstellen: mkdir -p /opt/backups",
    "Rechte setzen: chmod 755 /opt/backups"
  ]
}
```

---

## 6.7 Fortschritts-Updates

### Bei langen Tasks: Regelmäßig informieren

```
⏳ **PROGRESS UPDATE** — Backup-Script

Fortschritt: ████████░░ 80%

Was läuft:
- [✅] Backup-Verzeichnis erstellt
- [✅] tar-Komprimierung implementiert
- [✅] Logging hinzugefügt
- [🔄] Alte Backups löschen (macht gerade)
- [⬜] Testen

Erwartete Fertigstellung: ~5 Minuten
```

### Fortschritts-Template
```
{{ emoji }} **{{ task_name }}**

Fortschritt: █{{ filled }}{{ empty }} {{ percent }}%

Was erledigt:
{{#each done}}- [✅] {{this}}{{/each}}

Was läuft:
{{#each running}}- [🔄] {{this}}{{/each}}

Was fehlt:
{{#each todo}}- [⬜] {{this}}{{/each}}

{{ expected_completion }}
```

---

## 6.8 Anti-Patterns im Reporting

### ❌ Kein Report
```
Builder: *arbeitet 2 Stunden, sagt nichts*
CEO: "Was macht das Script?"
Builder: "War fertig, hab's nicht gesagt"
```

### ❌ Zu viel Report (Spam)
```
Builder: *jede Minute eine Nachricht*
"Arbeite..."
"Schreibe Code..."
"Noch mehr Code..."
CEO: *ignoriert alles*
```

### ❌ Vage Report
```
Builder: "Script ist fertig glaube ich"
CEO: "Welches Script? Was macht es?"
```

### ✅ Klarer Report
```
Builder: "✅ backup.sh FERTIG

- Sichert /home nach /opt/backups
- Nutzt tar mit gzip
- Löscht Backups >7 Tage
- Gespeichert: /workspace/builder/backup.sh

Bereit für Test."
```

---

## 6.9 Checkpoint + Report bei langen Tasks

### Kombination
```markdown
## Checkpoint — 17:30 UTC

Task: Backup-Script
Status: ⏳ 80% fertig
Letzte Aktion: Logging implementiert
Nächste Aktion: Alte Backups löschen

Report an Nico:
"⏳ Backup-Script bei 80%. 
Nächste: Retention-Policy. Fertig in ~5 Min."
```

---

## 6.10 Cron-Reporting

### Automatische Reports via Cron

```
CEO Briefing:      09:00 UTC (Täglich)
Security Audit:    10:00 UTC (Täglich)
Data Manager:      11:31 UTC (Täglich)
Research:          13:00 UTC (Täglich)
Evening Capture:   21:00 UTC (Täglich)
```

### Cron-Delivery konfigurieren
```javascript
cron({
  action: "add",
  job: {
    name: "Daily CEO Briefing",
    schedule: { kind: "cron", expr: "0 9 * * *" },
    payload: { kind: "agentTurn", message: "Führe Briefing durch..." },
    delivery: {
      mode: "announce",
      channel: "telegram",
      to: "5392634979"
    }
  }
})
```

---

## 📝 Zusammenfassung

| Konzept | Beschreibung |
|---------|--------------|
| task_report.json | Standardisiertes Report-Format |
| Heartbeat | Kurzes Lebenszeichen |
| Status-Werte | in_progress, done, warning, error, blocked |
| QC Officer | Unabhängige Validierung |
| Fortschritts-Update | Bei langen Tasks alle 5-10 Min |
| Anti-Patterns | Kein Report, Spam, Vage |

---

## ✅ Checkpoint

- [ ] Wie sieht die task_report.json Struktur aus?
- [ ] Was bedeutet Status "warning" vs "error"?
- [ ] Wann solltest du ein Fortschritts-Update senden?
- [ ] Was ist die Aufgabe des QC Officers?
- [ ] Was sind 3 Anti-Patterns beim Reporting?

---

*Lektion 6 — Reporting & Kommunikation — Version 1.0*
