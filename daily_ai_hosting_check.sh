#!/bin/bash
# Daily AI Hosting Health Check
# Runs at 08:00 daily

LOG="/home/clawbot/.openclaw/workspace/logs/ai_hosting_check.log"
SERVICES=(
    "http://187.124.11.27:8895:Lead Generator"
    "http://187.124.11.27:8896:AI Chatbot"
    "http://187.124.11.27:8898:SEO Tool"
    "http://187.124.11.27:8001:Trading Bot"
    "http://187.124.11.27:8892:Discord Bot"
)

echo "[$(date)] AI Hosting Health Check" >> $LOG

for service in "${SERVICES[@]}"; do
    IFS=':' read -r url name <<< "$service"
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null)
    if [ "$status" = "200" ]; then
        echo "✅ $name: OK" >> $LOG
    else
        echo "⚠️ $name: HTTP $status" >> $LOG
    fi
done

echo "[$(date)] Health Check completed" >> $LOG
