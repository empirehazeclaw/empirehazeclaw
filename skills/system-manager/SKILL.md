# System Manager Skill

**Version:** 1.1.0  
**Created:** 2026-04-10  
**Updated:** 2026-04-11
**Status:** Active

## Purpose

System health monitoring, backup management, cron orchestration, security hardening, and performance optimization.

## 🎯 Core Responsibilities

### 1. Health Monitoring
| Script | Purpose | Checkpoint |
|--------|---------|-----------|
| `quick_check.py` | Fast 6-point check | Gateway, Disk, Memory, Load, DBs, Backup |
| `health_monitor.py` | Full health report | All metrics + trends |
| `health_alert.py` | Alert system | Threshold-based alerts |
| `cron_monitor.py` | Monitor all cron jobs | Status, errors, timing |
| `cron_watchdog.py` | Watchdog for failed jobs | Restart/notify |

### 2. Backup & Recovery
| Script | Purpose | Schedule |
|--------|---------|----------|
| `auto_backup.py` | Automated backup | Daily 03:00 UTC |
| `backup_verify.py` | Verify backup integrity | On-demand |
| `backup_advisor/` | Backup strategy guidance | Skill |

### 3. Security
| Script | Purpose | Schedule |
|--------|---------|----------|
| `security-audit.sh` | Security audit | Daily 08:00 UTC |
| `openclaw security audit --deep` | Deep security scan | Weekly |
| `SUBAGENT_SPAWNING.md` | Subagent best practices | On-demand |

### 4. Performance
| Script | Purpose | Notes |
|--------|---------|-------|
| `NODE_COMPILE_CACHE` | Cache for faster CLI | Set in bashrc |
| `OPENCLAW_NO_RESPAWN` | Avoid respawn overhead | Set in bashrc |

## 🏃 Quick Commands

```bash
# Fast health check
python3 scripts/quick_check.py

# Full health report
python3 scripts/health_monitor.py

# System status
openclaw status

# OpenClaw doctor
openclaw doctor

# Security audit
openclaw security audit --deep
```

## 📊 Health Checkpoints

### Daily (Morning)
1. `quick_check.py` - Gateway, Disk, Memory, Load
2. `cron_monitor.py` - All crons OK?
3. `backup_verify.py` - Yesterday's backup valid?

### After Changes
1. `self_eval.py` - Score improving?
2. `test_framework.py` - Tests passing?
3. Git commit + push

## 🔄 Performance Optimization

### OpenClaw Doctor Fixes
```bash
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
mkdir -p /var/tmp/openclaw-compile-cache
```

### Subagent Health Check
```bash
python3 scripts/subagent_health_check.py
```

## 📋 Cron Jobs (Active)

| Zeit | Script | Status | Letzter Run |
|------|--------|--------|-------------|
| 08:00 | security-audit.sh | ✅ | OK |
| 09:00 | morning_brief.py | ✅ | OK |
| 21:00 | evening_capture | ✅ | OK |
| 22:00* | weekly_review.py | ✅ | - |
| Every 3h | quick_check.py | ✅ | OK |
| Every 6h | cron_watchdog.py | ✅ | OK |
| 03:00 | auto_backup.py | ✅ | OK |
| Periodisch | session_cleanup | ✅ | OK |

## 🔒 Security Hardening

### Security Audit Script
- Prüft auf code injection risks
- Validiert input paths
- Prüft API keys
- Checkt cron permissions

### Security Best Practices
1. Never exec() user input
2. Always validate paths
3. API keys in env vars
4. Backup before changes
5. Test before deploy

## 📁 Related Files

- `/home/clawbot/.openclaw/workspace/scripts/` - All scripts
- `/home/clawbot/.openclaw/workspace/skills/system-manager/SUBAGENT_SPAWNING.md` - Subagent best practices
- `/home/clawbot/.openclaw/workspace/memory/2026-04-11.md` - Daily memory
- `/home/clawbot/.openclaw/workspace/logs/` - Log files

## 🎓 Skill Levels

### Level 1: Monitor
- Run quick_check.py
- Report issues

### Level 2: Respond
- Fix common issues
- Restart services
- Clear logs

### Level 3: Optimize
- Performance tuning
- Security hardening
- Script improvements

### Level 4: Architect
- System design
- Automation workflows
- Capability evolution

---

*Last Updated: 2026-04-11*
*Part of: Sir HazeClaw Skills*
