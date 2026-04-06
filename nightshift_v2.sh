#!/bin/bash
# Night Shift V2 - Optimiert

echo "🌙 Night Shift started $(date)"

cd /home/clawbot/.openclaw/workspace

# 1. Generate new leads
echo "1️⃣ Generating leads..."
python3 scripts/run_agent.py revenue

# 2. Create content  
echo "2️⃣ Creating content..."
python3 scripts/run_agent.py content

# 3. Research
echo "3️⃣ Research..."
python3 scripts/run_agent.py research

# 4. Analytics
echo "4️⃣ Analytics..."
python3 scripts/daily_analytics.py

# 5. Health check
echo "5️⃣ Health check..."
python3 scripts/health_check.py

echo "🌅 Night Shift complete $(date)"
