# 🔧 CRON ERROR REPORT
**Erstellt:** 2026-04-12 13:30 UTC

---

## 📊 Cron Status Overview

| Status | Count |
|--------|-------|
| OK | 15 |
| Error | 4 |
| Idle | 3 |
| **Total** | **22** |

---

## ❌ Error Crons

| Cron | Last Run | Issue |
|------|----------|-------|
| Token Budget Tracker | 13h ago | Script error |
| Session Cleanup Daily | 10h ago | Script error |
| CEO Daily Briefing | 4h ago | Script error |
| KG Lifecycle Manager | 11h ago | Script error |

---

## 💤 Idle Crons

| Cron | Last Run | Status |
|------|----------|--------|
| Memory Dreaming Promoter | Never | Not triggered |
| Run auto documentation | Never | Weekly (Mon) |
| CEO Weekly Review | Never | Weekly (Mon) |

---

## 🎯 Action Items

### Fix Priority:
1. CEO Daily Briefing → wichtigste Funktion
2. Token Budget Tracker → KPI tracking
3. Session Cleanup → System maintenance
4. KG Lifecycle Manager → KG quality

---

## ✅ Recommendations

1. Run `openclaw cron runs <cron_id>` for error details
2. Check logs: `journalctl -u openclaw --since "1 hour ago"`
3. Fix scripts or disable if not needed

