# System Manager Skill

**Version:** 1.0.0  
**Created:** 2026-04-10  
**Status:** Active

## Purpose

System health monitoring, backup management, and cron orchestration.

## Scripts

### Health Monitoring
```bash
python3 scripts/health_monitor.py          # Full health report
python3 scripts/quick_check.py            # Fast system check (6 checks)
python3 scripts/health_alert.py            # Alert system
```

### Backup Management
```bash
python3 scripts/backup_verify.py           # Verify backups
python3 scripts/auto_backup.py             # Auto backup system
```

### Cron Management
```bash
python3 scripts/cron_monitor.py            # Monitor all cron jobs
python3 scripts/cron_watchdog.py          # Watchdog for failed jobs
```

### System Routines
```bash
python3 scripts/morning_routine.py         # Morning checklist
python3 scripts/evening_routine.py        # Evening checklist
```

## Quick Health Check

Run this for a fast system status:
```bash
python3 scripts/quick_check.py
```

Checks:
- Gateway (port 18789)
- Disk space (>10%)
- Memory (<90%)
- Load average (<4.0)
- Database integrity
- Backup existence

## Morning Routine

Run all morning checks:
```bash
python3 scripts/morning_routine.py
```

Includes:
- Health check
- Backup verify
- Cron status
- Habit tracker
- Quality metrics
- Self-evaluation

## Evening Routine

Run all evening checks:
```bash
python3 scripts/evening_routine.py
```

Includes:
- Self-evaluation
- Quality metrics
- Habit check-in
- Deep reflection (Sundays)

## Cron Jobs

Active crons (8):
- CEO Daily Briefing: 11:00 UTC
- Evening Capture: 21:00 UTC
- Nightly Dreaming: 02:00 UTC
- Security Audit: 08:00 UTC
- Health Check: Hourly
- Cron Watchdog: Every 6h
- Daily Auto Backup: 03:00 UTC
- Weekly Review: Sunday 10:00 UTC

## Notes

- All scripts return structured data for monitoring
- Health alerts stored in memory/alerts/
- Backup verification runs automatically
