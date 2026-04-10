# Sir HazeClaw Scripts

**Stand:** 2026-04-10
**Scripts:** 55 total, 16 heute verbessert/getestet

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

### cron_monitor.py ⭐ (verbessert)
Cron Job Status anzeigen - jetzt mit ✅/⚠️/❌ Status.
```bash
python3 scripts/cron_monitor.py
```

### system_report.py ⭐ (verbessert)
Umfassender System-Report - zeigt alle aktiven Crons mit Status.
```bash
python3 scripts/system_report.py
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

### backup_verify.py ⭐ (verbessert)
Backup Validierung - erkennt jetzt Backup-Paranoia.
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

### morning_brief.py ⭐ (verbessert)
Telegram-formatierter Morning Brief - zeigt jetzt heute + gestern Commits.
```bash
python3 scripts/morning_brief.py
python3 scripts/morning_brief.py --format telegram
```

### evening_summary.py ⭐ (verbessert)
Evening Summary - Commit formatting gefixt.
```bash
python3 scripts/evening_summary.py
```

### weekly_review.py ⭐
Weekly Review Report.
```bash
python3 scripts/weekly_review.py
```

### daily_summary.py ⭐ (verbessert)
Daily Summary - zeigt jetzt Pattern Status.
```bash
python3 scripts/daily_summary.py
```

### self_check.py ⭐ (verbessert)
Self-Check Script - 7 Patterns + Backup-Paranoia Erkennung.
```bash
python3 scripts/self_check.py
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

### Test Results (2026-04-10 20:48-20:53 UTC)

| Script | Status | Notes |
|--------|--------|-------|
| morning_brief.py | ✅ | Git commits fixed, shows today+yesterday |
| weekly_review.py | ✅ | Works correctly |
| self_check.py | ✅ | 7 Patterns + Backup-Paranoia detection |
| kg_updater.py | ✅ | add/list/stats work |
| evening_summary.py | ✅ | Commit formatting fixed |
| health_monitor.py | ✅ | System healthy |
| backup_verify.py | ✅ | Integrity OK |
| cron_monitor.py | ✅ | Shows status per cron (✅/⚠️/❌) |
| quick_check.py | ✅ | All checks passed |
| daily_summary.py | ✅ | Works correctly |
| openrouter_monitor.py | ✅ | API responding |
| system_report.py | ✅ | Shows status for all 8 active crons |
| auto_backup.py | ✅ | Backup created |
| cron_watchdog.py | ✅ | All healthy |
| common_issues_check.py | ✅ | Found 2 issues (expected) |

---

## 📊 SCRIPTS TODAY (Verbessert 20:51-20:53)

| Script | Improvement | Status |
|--------|-------------|--------|
| morning_brief.py | Git commits zeigen heute + gestern | ✅ |
| self_check.py | 7 Patterns + Backup-Paranoia Erkennung | ✅ |
| evening_summary.py | Commit formatting gefixt | ✅ |
| cron_monitor.py | Zeigt Status (✅/⚠️/❌) pro Cron | ✅ |
| system_report.py | Zeigt Status für alle aktiven Crons | ✅ |

---

*Sir HazeClaw — CEO*
*Erstellt: 2026-04-10*
*Letztes Update: 2026-04-10 20:49 UTC*