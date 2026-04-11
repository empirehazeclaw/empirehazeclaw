#!/bin/bash
for i in 1 2 3 4 5; do
  echo "=== RUN $i/5 ==="
  python3 /home/clawbot/.openclaw/workspace/scripts/learning_coordinator.py --full
  echo ""
done
