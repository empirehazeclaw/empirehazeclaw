#!/bin/bash
echo "=== 🌙 NIGHT SHIFT START === $(date)"

# Loop until 7:00 AM
while [ $(date +%H) -lt 7 ]; do
    
    echo "=== RUN $(date +%H:%M) ==="
    
    # 1. Generate Leads (every 2 hours)
    if [ $(($(date +%H) % 2)) -eq 0 ]; then
        echo "📧 Generating leads..."
        python3 scripts/agents/revenue_agent.py 2>/dev/null
    fi
    
    # 2. Check and send follow-ups
    echo "📧 Checking follow-ups..."
    python3 scripts/followup_automation.py 2>/dev/null
    
    # 3. Health check (every hour)
    echo "🔧 Health check..."
    python3 scripts/health_check.py 2>/dev/null
    
    # 4. Content generation (morning, evening)
    hour=$(date +%H)
    if [ "$hour" -eq 6 ] || [ "$hour" -eq 18 ]; then
        echo "✍️ Generating content..."
        python3 scripts/agents/content_agent.py 2>/dev/null
    fi
    
    # 5. Research (every 3 hours)
    if [ $(($(date +%H) % 3)) -eq 0 ]; then
        echo "🔍 Running research..."
        python3 scripts/agents/research_agent.py 2>/dev/null
    fi
    
    # 6. Bounce handling (every hour)
    echo "🧹 Bounce handling..."
    python3 scripts/outreach_bounce_handler.py 2>/dev/null
    
    echo "=== SLEEP 30 MIN ==="
    sleep 1800
done

echo "=== 🌅 MORNING - 7:00 ==="
echo "✅ Night shift complete!"
