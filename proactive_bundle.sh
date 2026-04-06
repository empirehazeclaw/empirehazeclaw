#!/bin/bash
# Proactive Agent + Self Learning Bundle
# Runs every hour to check triggers and learn

echo "🧠 Proactive Agent & Learning Bundle - $(date)"

# Run proactive agent
python3 /home/clawbot/.openclaw/workspace/scripts/proactive_agent.py

# Run weekly learning analysis (only on certain days)
DAY=$(date +%u)
if [ "$DAY" = "1" ]; then
    echo "📊 Running weekly learning analysis..."
    python3 /home/clawbot/.openclaw/workspace/scripts/self_learning.py
fi

# Analyze last cron run outcomes
echo "📈 Analyzing cron outcomes..."
python3 /home/clawbot/.openclaw/workspace/scripts/analyze_cron_performance.py 2>/dev/null

echo "✅ Bundle complete"
