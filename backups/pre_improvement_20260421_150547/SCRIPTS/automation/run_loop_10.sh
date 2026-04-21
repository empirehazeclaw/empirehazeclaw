#!/bin/bash
cd /home/clawbot/.openclaw/workspace/scripts
for i in {1..10}; do
  echo "=== Run $i/10 ==="
  python3 learning_loop_v3.py 2>&1 | grep -E "(Iteration|Loop Score|Validation|Cross-pattern)"
  echo ""
done
