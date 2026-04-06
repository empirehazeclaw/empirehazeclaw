#!/bin/bash
# Night Shift - Arbeitet während Nico schläft
echo "🌙 Night Shift started $(date)"

# 1. Check leads
python3 scripts/run_agent.py revenue

# 2. Create content
python3 scripts/run_agent.py content

# 3. Research
python3 scripts/run_agent.py research

echo "🌅 Night Shift complete $(date)"
