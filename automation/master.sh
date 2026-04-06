#!/bin/bash
# Master Automation Script - Consolidates all cron jobs
# Run this script hourly and it will handle all automations

DATE=$(date +%H)
DAY=$(date +%u)

echo "=== Master Automation $(date) ==="

# Hourly tasks (every hour)
echo "[$(date +%H:%M)] Running hourly tasks..."

# Every 15 minutes
if [ "$(date +%M)" = "00" ] || [ "$(date +%M)" = "15" ] || [ "$(date +%M)" = "30" ] || [ "$(date +%M)" = "45" ]; then
    echo "  - Health check..."
    cd /home/clawbot/.openclaw/workspace && python3 scripts/agents/health_check.py 2>/dev/null
fi

# Hourly at minute 5
if [ "$(date +%M)" = "05" ]; then
    echo "  - Cost tracker..."
    cd /home/clawbot/.openclaw/workspace && python3 scripts/auto_cost_tracker.py 2>/dev/null
    
    echo "  - Session cleanup..."
    cd /home/clawbot/.openclaw && ./scripts/session_reset.sh 2>/dev/null
fi

# Daily tasks (at 3 AM)
if [ "$DATE" = "03" ] && [ "$(date +%M)" = "00" ]; then
    echo "[$DATE:00] Running daily tasks..."
    echo "  - Backup..."
    cd /home/clawbot/.openclaw/workspace && ./scripts/unified_backup.sh 2>/dev/null
fi

# Morning tasks (at 6 AM)
if [ "$DATE" = "06" ] && [ "$(date +%M)" = "00" ]; then
    echo "[$DATE:00] Morning tasks..."
    echo "  - Self improvement..."
    cd /home/clawbot/.openclaw/workspace/self_improve && ./councils_daily.sh 2>/dev/null
    
    echo "  - Analytics..."
    cd /home/clawbot/.openclaw/workspace && python3 scripts/multi_platform_analytics.py 2>/dev/null
fi

# Midday tasks (at 8 AM)
if [ "$DATE" = "08" ] && [ "$(date +%M)" = "00" ]; then
    echo "[$DATE:00] Midday tasks..."
    echo "  - Hook testing..."
    cd /home/clawbot/.openclaw/workspace && python3 scripts/hook_testing.py 2>/dev/null
fi

# Evening tasks (at 20 = 8 PM)
if [ "$DATE" = "20" ] && [ "$(date +%M)" = "00" ]; then
    echo "[$DATE:00] Evening tasks..."
    echo "  - Feedback loop..."
    cd /home/clawbot/.openclaw/workspace && python3 scripts/feedback_loop.py 2>/dev/null
fi

# Weekly (Monday at 9 AM)
if [ "$DAY" = "1" ] && [ "$DATE" = "09" ] && [ "$(date +%M)" = "00" ]; then
    echo "[$DATE:00] Weekly tasks..."
    echo "  - Memory synthesis..."
    cd /home/clawbot/.openclaw/workspace/memory && ./synthesize.sh 2>/dev/null
fi

echo "=== Master Automation Complete ==="
