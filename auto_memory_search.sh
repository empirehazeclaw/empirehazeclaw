#!/bin/bash
# Auto Memory Search - Called automatically for decisions

QUERY="$1"

if [ -z "$QUERY" ]; then
    echo "Usage: $0 <search_query>"
    exit 1
fi

echo "=== 🔍 AUTO MEMORY SEARCH ==="
echo "Query: $QUERY"
echo ""

# Search in priority order
echo "📌 P1 (Must Check):"
grep -i "$QUERY" MASTER_MEMORY.md 2>/dev/null | head -3

echo ""
echo "📌 P2 (Check):"
grep -i "$QUERY" memory/*.md 2>/dev/null | grep -v "P1\|P2\|P3" | head -3

echo ""
echo "=== ✅ Search Complete ==="
