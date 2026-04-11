#!/bin/bash
echo "=== MEMORY SYSTEMS FULL TEST ==="
echo ""

echo "=== 1. MEMORY_API.py status ==="
python3 scripts/MEMORY_API.py status
echo ""

echo "=== 2. memory_cleanup.py ==="
python3 scripts/memory_cleanup.py
echo ""

echo "=== 3. Hybrid Search Test ==="
python3 scripts/memory_hybrid_search.py "learning"
echo ""

echo "=== 4. CEO Memory Structure ==="
ls -la ceo/memory/
echo ""

echo "=== 5. Docs Created ==="
ls -la docs/
echo ""

echo "=== TEST COMPLETE ==="
