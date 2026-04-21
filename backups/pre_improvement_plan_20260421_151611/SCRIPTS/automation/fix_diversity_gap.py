#!/usr/bin/env python3
import json
from datetime import datetime

reflection_file = '/home/clawbot/.openclaw/workspace/data/reflection_store.json'
data = json.loads(open(reflection_file).read())

reflections = data.get('reflections', [])

# Add code_quality reflection type
new_reflection = {
    'id': f'reflect_{int(datetime.now().timestamp() * 1000)}',
    'task_type': 'code_quality',
    'critique': 'Code quality patterns should be tracked separately from learning patterns',
    'error_type': 'quality_improvement',
    'created_at': datetime.now().isoformat(),
    'resolved': True,
    'use_count': 0
}

reflections.append(new_reflection)
data['reflections'] = reflections
open(reflection_file, 'w').write(json.dumps(data, indent=2))
print('Added code_quality reflection type')
print(f'Total types now: {len(set(r.get("task_type") for r in reflections))}')