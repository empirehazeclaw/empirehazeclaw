#!/bin/bash
cd /home/clawbot/.openclaw/workspace

echo "=== 1. Event Bus Basic ==="
python3 SCRIPTS/automation/event_bus.py stats
echo ""
python3 SCRIPTS/automation/event_bus.py consumers

echo ""
echo "=== 2. Learning Loop ==="
timeout 90 python3 SCRIPTS/automation/learning_loop_v3.py 2>&1 | tail -15

echo ""
echo "=== 3. Meta Learning ==="
timeout 30 python3 ceo/scripts/meta_learning_controller.py --with-events 2>&1 | tail -10

echo ""
echo "=== 4. Capability Evolver ==="
bash SCRIPTS/automation/run_smart_evolver.sh 2>&1 | tail -10

echo ""
echo "=== 5. Event Consumers ==="
timeout 10 python3 SCRIPTS/automation/event_bus.py consume 2>&1 | head -20

echo ""
echo "=== 6. Final Event Stats ==="
python3 SCRIPTS/automation/event_bus.py stats 2>&1 | head -30

echo ""
echo "=== 7. Integration Dashboard ==="
timeout 30 python3 SCRIPTS/automation/integration_dashboard.py --check 2>&1

echo ""
echo "=== 8. Ralph Learning ==="
timeout 60 python3 SCRIPTS/automation/ralph_learning_loop.py 2>&1 | tail -10

echo ""
echo "=== 9. KG Integrity ==="
python3 -c "
import json
kg = json.load(open('ceo/memory/kg/knowledge_graph.json'))
entities = kg.get('entities', {})
relations = kg.get('relations', {})
linked = set()
for r in relations.values():
    linked.add(r.get('from'))
    linked.add(r.get('to'))
orphans = [k for k in entities.keys() if k not in linked]
broken = sum(1 for r in relations.values() if r.get('from') not in entities or r.get('to') not in entities)
print(f'Entities: {len(entities)}')
print(f'Relations: {len(relations)}')
print(f'Orphans: {len(orphans)}')
print(f'Broken Relations: {broken}')
print(f'KG Health: {100-broken/len(relations)*100:.1f}%' if relations else 'N/A')
"

echo ""
echo "=== 10. Cron Status ==="
python3 -c "import json; crons = json.load(open('/home/clawbot/.openclaw/cron/jobs.json'))['jobs']; print(f'Total: {len(crons)}'); print(f'Active: {sum(1 for c in crons if c.get(\"enabled\"))}'); print(f'Failed: {sum(1 for c in crons if c.get(\"state\",{}).get(\"lastRunStatus\")==\"failed\")}')"