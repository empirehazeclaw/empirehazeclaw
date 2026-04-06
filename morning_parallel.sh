#!/bin/bash
# Morning parallel execution - all stats at once
cd /home/clawbot/.openclaw/workspace
python3 scripts/parallel_executor.py --template morning --max-workers 3
