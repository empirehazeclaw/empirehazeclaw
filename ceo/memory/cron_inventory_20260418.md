# Cron Inventory — 2026-04-18

## System Crontab (user: clawbot)
| # | Script | Schedule | Letzter Run | Status |
|---|--------|----------|------------|--------|
| 1 | sqlite_vacuum.sh | 0 3 * * * | Unbekannt | 🟡 |
| 2 | session_cleanup.py | 0 4 * * * | Unbekannt | 🟡 |
| 3 | kg_auto_populate.py | 0 6 * * * | Unbekannt | 🟡 |
| 4 | semantic_search.py | 30 6 * * * | Unbekannt | 🟡 |
| 5 | evening_capture.py | 0 21 * * * | Unbekannt | 🟡 |
| 6 | github_backup.sh | 0 23 * * * | ~21h ago | ✅ |
| 7 | weekly_review_zettel.py | 0 22 * * 0 | ~1d ago | ✅ |
| 8 | morning_brief.sh | 0 9 * * * | Unbekannt | 🟡 |
| 9 | health_agent.py | */11 * * * * | ~3min ago | ✅ |
| 10 | research_agent.py | 0 * * * * | ~1h ago | ✅ |
| 11 | data_agent.py | 30 * * * * | ~30min ago | ✅ |

**Total system crons: 11**

## OpenClaw Internal Agents
| Agent | Schedule | Status |
|-------|----------|--------|
| Health Agent | */11 min (via openclaw) | ✅ Active |
| Research Agent | Hourly (via openclaw) | ✅ Active |
| Data Agent | 30min (via openclaw) | ✅ Active |

## Diskrepanz MEMORY vs Realität
| Metric | MEMORY.md | Realität |
|--------|-----------|----------|
| Active Crons | 26 | 11 system + 3 agents = 14 |

**Erklärung:**
- MEMORY.md zählte "26 active Crons" inkl. OpenClaw internal plugins
- OpenClaw hat viele interne Mechanismen (Event Bus, agent executor, etc.)
- Die 14Crons in crontab sind die主 cron jobs
- Zusätzlich gibt es OpenClaw Cron Plugins die nicht in crontab erscheinen

## Fehlende Cron Jobs (aus MEMORY.md)
Folgende Crons aus MEMORY.md sind NICHT in crontab:
- Learning Loop (hourly) — nicht in crontab, aber in `/workspace/scripts/` vorhanden
- Self-Improver (daily) — nicht in crontab
- Evolver — nicht in crontab
- KG Embedding Updater — nicht in crontab

Diese Scripts existieren, aber sind NICHT als Cron job aktiv.
→ MEMORY.md ist überholt, Crons die "active" sein sollten sind deaktiviert.

## Korrektur Bedarf
MEMORY.md Section "SYSTEM CONFIG" → Crons: "26" → sollte "14" sein (11 + 3 agents)

*Erstellt: 2026-04-18 08:20 UTC durch Subagent (timeout, daher manuell)*