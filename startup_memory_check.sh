#!/bin/bash
# MUST run at start of every session

echo "🧠 Loading Memory..."
echo ""

# 1. Check QUICK FACTS
echo "⚡ QUICK FACTS:"
grep -E "✅|❌|WORKS|BROKEN" /home/clawbot/.openclaw/workspace/memory/QUICK_FACTS.md | head -10

echo ""

# 2. Check today's notes
echo "📝 Heute:"
head -20 /home/clawbot/.openclaw/workspace/memory/2026-03-24.md

echo ""
echo "✅ Memory loaded!"
