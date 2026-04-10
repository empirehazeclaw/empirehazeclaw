# Sir HazeClaw Scripts

**Stand:** 2026-04-10

---

## 🎯 MONITORING SCRIPTS

### health_monitor.py
Vollständiger Health Report.
```bash
python3 scripts/health_monitor.py --report
```

### quick_check.py
Schneller System-Check.
```bash
python3 scripts/quick_check.py
```

### health_alert.py
Alert-System bei Problemen.
```bash
python3 scripts/health_alert.py
```

### cron_monitor.py
Cron Job Status anzeigen.
```bash
python3 scripts/cron_monitor.py
```

### cron_watchdog.py
Überwacht Cron Jobs auf Fehler.
```bash
python3 scripts/cron_watchdog.py
```

### common_issues_check.py
Prüft auf häufige Probleme.
```bash
python3 scripts/common_issues_check.py
```

---

## 🛡️ SECURITY SCRIPTS

### security-audit.sh
Security Audit für Workspace.
```bash
bash scripts/security-audit.sh
```

### vault.py
Encrypted Secrets Storage (AES-256-GCM).
```bash
python3 scripts/vault.py set <key> <value> -n "<note>"
python3 scripts/vault.py get <key>
python3 scripts/vault.py list
python3 scripts/vault.py delete <key>
```

---

## 💾 BACKUP SCRIPTS

### backup_verify.py
Backup Validierung.
```bash
python3 scripts/backup_verify.py
```

### auto_backup.py
Automatischer Workspace Backup.
```bash
python3 scripts/auto_backup.py
python3 scripts/auto_backup.py --dry-run
```

---

## 📊 REPORT SCRIPTS

### system_report.py
Umfassender System-Report.
```bash
python3 scripts/system_report.py
```

### daily_summary.py
Tägliche Zusammenfassung.
```bash
python3 scripts/daily_summary.py
```

### kgml_summary.py
Knowledge Graph als Markdown.
```bash
python3 scripts/kgml_summary.py [kg_json] [output_md]
```

### openrouter_monitor.py
OpenRouter API Monitor.
```bash
python3 scripts/openrouter_monitor.py
```

---

## ⚙️ OPERATIONS

### evening_capture.py
Evening Workflow (existiert).

---

## 📅 ACTIVE CRONS

| Cron | Zeit | Script |
|------|------|--------|
| CEO Daily Briefing | 11:00 UTC | (Agent) |
| Evening Capture | 21:00 UTC | evening_capture.py |
| Nightly Dreaming | 02:00 UTC | (Agent) |
| Security Audit | 08:00 UTC | security-audit.sh |
| Health Check | Hourly | quick_check.py |
| Cron Watchdog | Every 6h | cron_watchdog.py |
| Daily Auto Backup | 03:00 UTC | auto_backup.py |

---

## 🧪 TESTING

Alle Scripts wurden getestet:
- Syntax geprüft
- Mit echten Daten ausgeführt
- Keine "fake" Tests

---

*Sir HazeClaw — CEO*
*Erstellt: 2026-04-10*