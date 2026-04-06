#!/bin/bash
# This script MUST be called before any important response

FACTS_FILE="/home/clawbot/.openclaw/workspace/memory/QUICK_FACTS.md"

if [ -f "$FACTS_FILE" ]; then
    echo "⚡ Checking QUICK_FACTS..."
    grep -E "WORKS|❌|✅" "$FACTS_FILE" | head -10
else
    echo "⚠️ QUICK_FACTS not found!"
fi
