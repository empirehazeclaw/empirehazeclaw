#!/bin/bash
# ================================================
# 🐕 Watchdog Wrapper Script für Cron
# ================================================
# Wrapper für autonomous/watchdog_agent.py
# Läuft alle 5 Minuten via Cron
#
# Crontab Eintrag:
# */5 * * * * /home/clawbot/.openclaw/workspace/scripts/watchdog.sh >> /home/clawbot/.openclaw/workspace/logs/watchdog_cron.log 2>&1

WORKSPACE="/home/clawbot/.openclaw/workspace"
PYTHON="/usr/bin/python3"
WATCHDOG_SCRIPT="${WORKSPACE}/autonomous/watchdog_agent.py"
LOG_DIR="${WORKSPACE}/logs"

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

# Run watchdog
exec ${PYTHON} ${WATCHDOG_SCRIPT} 2>&1
