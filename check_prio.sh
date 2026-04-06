#!/bin/bash
# Check Priority 1 items before responding

echo "=== 🚩 P1 CHECK ==="
echo ""
echo "⚡ REGELN:"
grep -A2 "## 🚩 PRIORITY" MASTER_MEMORY.md | head -10
echo ""
echo "✅ P1 CHECK DONE"
