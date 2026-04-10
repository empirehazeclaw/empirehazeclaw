# Sir HazeClaw Scripts

**Stand:** 2026-04-10
**Scripts:** 55 total, 9 heute erstellt

---

## 🎯 MONITORING SCRIPTS

### quick_check.py ⭐
Schneller System-Check (alle 5min).
```bash
python3 scripts/quick_check.py
```

### health_monitor.py ⭐
Vollständiger Health Report.
```bash
python3 scripts/health_monitor.py --report
```

### health_alert.py ⭐
Alert-System bei Problemen.
```bash
python3 scripts/health_alert.py
```

### cron_monitor.py ⭐
Cron Job Status anzeigen.
```bash
python3 scripts/cron_monitor.py
```

### cron_watchdog.py ⭐
Überwacht Cron Jobs auf Fehler.
```bash
python3 scripts/cron_watchdog.py
```

### common_issues_check.py ⭐
Prüft auf häufige Probleme.
```bash
python3 scripts/common_issues_check.py
```

---

## 🛡️ SECURITY SCRIPTS

### security-audit.sh ⭐
Security Audit für Workspace.
```bash
bash scripts/security-audit.sh
```

### vault.py ⭐
Encrypted Secrets Storage (AES-256-GCM).
```bash
python3 scripts/vault.py set <key> <value> -n "<note>"
python3 scripts/vault.py get <key>
python3 scripts/vault.py list
```

---

## 💾 BACKUP SCRIPTS

### backup_verify.py ⭐
Backup Validierung.
```bash
python3 scripts/backup_verify.py
```

### auto_backup.py ⭐
Automatischer Workspace Backup.
```bash
python3 scripts/auto_backup.py
python3 scripts/auto_backup.py --dry-run
```

---

## 📊 REPORT SCRIPTS

### system_report.py ⭐
Umfassender System-Report.
```bash
python3 scripts/system_report.py
```

### daily_summary.py ⭐
Tägliche Zusammenfassung.
```bash
python3 scripts/daily_summary.py
```

### morning_brief.py ⭐
Telegram-formatierter Morning Brief.
```bash
python3 scripts/morning_brief.py
python3 scripts/morning_brief.py --format telegram
```

### kgml_summary.py
Knowledge Graph als Markdown.
```bash
python3 scripts/kgml_summary.py [kg_json] [output_md]
```

### openrouter_monitor.py ⭐
OpenRouter API Monitor.
```bash
python3 scripts/openrouter_monitor.py
```

---

## 📅 ACTIVE CRONS (7)

| Cron | Zeit | Script |
|------|------|--------|
| CEO Daily Briefing | 11:00 UTC | (Agent) |
| Evening Capture | 21:00 UTC | evening_capture.py |
| Nightly Dreaming | 02:00 UTC | (Agent) |
| Security Audit | 08:00 UTC | security-audit.sh |
| Health Check | Hourly | quick_check.py ⭐ |
| Cron Watchdog | Every 6h | cron_watchdog.py ⭐ |
| Daily Auto Backup | 03:00 UTC | auto_backup.py ⭐ |

⭐ = Heute erstellt

---

## 🧪 QUALITY ASSURANCE (2026-04-10)

Alle Scripts wurden getestet:
- [x] Syntax geprüft
- [x] Mit echten Daten ausgeführt
- [x] Dokumentiert
- [x] Git committed

### Test Results (2026-04-10 20:48-20:49 UTC)

| Script | Status | Notes |
|--------|--------|-------|
| morning_brief.py | ✅ | Git commits fixed, shows today+yesterday |
| weekly_review.py | ✅ | Works correctly |
| self_check.py | ✅ | Found 3 patterns to avoid |
| kg_updater.py | ✅ | add/list/stats work |
| evening_summary.py | ✅ | Works correctly |
| health_monitor.py | ✅ | System healthy |
| backup_verify.py | ✅ | Integrity OK |
| cron_monitor.py | ✅ | 8 enabled, 24 disabled |
| quick_check.py | ✅ | All checks passed |
| daily_summary.py | ✅ | Works correctly |
| openrouter_monitor.py | ✅ | API responding |
| system_report.py | ✅ | Works correctly |
| auto_backup.py | ✅ | Backup created |
| cron_watchdog.py | ✅ | All healthy |
| common_issues_check.py | ✅ | Found 2 issues (expected) |

---

## 📊 SCRIPTS TODAY

| Script | Zweck | Status |
|--------|-------|--------|
| morning_brief.py | Morning Brief | ✅ Getestet |
| weekly_review.py | Weekly Review | ✅ Getestet |
| evening_summary.py | Evening Summary | ✅ Getestet |
| self_check.py | Self-Check | ✅ Getestet |
| kg_updater.py | KG Management | ✅ Getestet |
| quick_check.py | Rapid Check | ✅ Getestet |
| health_monitor.py | Health Report | ✅ Getestet |
| backup_verify.py | Backup Verify | ✅ Getestet |
| cron_monitor.py | Cron Status | ✅ Getestet |
| cron_watchdog.py | Cron Watchdog | ✅ Getestet |
| daily_summary.py | Daily Summary | ✅ Getestet |
| system_report.py | System Report | ✅ Getestet |
| openrouter_monitor.py | OpenRouter Monitor | ✅ Getestet |
| auto_backup.py | Auto Backup | ✅ Getestet |
| common_issues_check.py | Issues Check | ✅ Getestet |
| idempotency_check.py | Script Safety | ✅ Created |

---

*Sir HazeClaw — CEO*
*Erstellt: 2026-04-10*
*Letztes Update: 2026-04-10 20:49 UTC*