# KGML SUMMARY FORMAT — Knowledge Graph als Markdown

**Erstellt:** 2026-04-10
**Basierend auf:** knowledge-graph-skill serialize.mjs

---

## 🎯 PROBLEM

Unser Knowledge Graph ist als JSON gespeichert. Das ist:
- Gut für机器 (lesbar für AI)
- Schlecht für Menschen (nicht leicht lesbar)

---

## 💡 LÖSUNG: KGML

**KGML = Knowledge Graph Markup Language**

Ein Textformat das:
- Für Menschen lesbar
- Für AI leicht parst
- Strukturierte Summary des KG

---

## 📋 FORMAT BEISPIEL

```markdown
# Knowledge Graph Summary

## Entities: 42

### Topics
- **Automation** (depth: 1)
  - related: Scripts, Crons, Monitoring
  - refs: 12

- **Security** (depth: 1)
  - related: Audit, Secrets, Permissions
  - refs: 8

### Systems
- **OpenClaw Gateway** (depth: 1)
  - type: service
  - related: Plugins, Crons
  - refs: 5

## Relations: 156

### Top Relation Types
| Type | Count |
|------|--------|
| uses | 42 |
| related_to | 38 |
| part_of | 24 |

## Recent Entities
- 2026-04-10: Security Audit Script
- 2026-04-10: Encrypted Vault
- 2026-04-09: OpenRouter Fix

## Knowledge Gaps
- No entity for: Email Marketing
- No relation between: Social Media → Content
```

---

## 🛠️ IMPLEMENTIERUNG

### Python Script:

```python
#!/usr/bin/env python3
"""
KGML Summary Generator
Wandelt KG JSON in lesbare Markdown Summary um.
"""

import json
from pathlib import Path
from datetime import datetime

def generate_kgml(kg_path: str, output_path: str):
    """Generiert KGML Summary aus KG JSON."""
    
    with open(kg_path) as f:
        kg = json.load(f)
    
    nodes = kg.get('nodes', {})
    edges = kg.get('edges', [])
    meta = kg.get('meta', {})
    
    # Header
    md = f"""# Knowledge Graph Summary

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Entities: {len(nodes)}
Relations: {len(edges)}

"""
    
    # Entity Types
    types = {}
    for node in nodes.values():
        t = node.get('type', 'unknown')
        types[t] = types.get(t, 0) + 1
    
    md += "## Entity Types\n\n"
    for t, count in sorted(types.items(), key=lambda x: -x[1]):
        md += f"- **{t}**: {count}\n"
    
    md += "\n## Recent Entities\n\n"
    # Sort by created or modified
    recent = sorted(nodes.items(), 
                   key=lambda x: x[1].get('created', ''), 
                   reverse=True)[:5]
    for node_id, node in recent:
        md += f"- {node.get('label', node_id)} ({node.get('type', '?')})\n"
    
    # Relation Types
    rel_types = {}
    for edge in edges:
        rel = edge.get('rel', 'unknown')
        rel_types[rel] = rel_types.get(rel, 0) + 1
    
    md += "\n## Relation Types\n\n"
    for rel, count in sorted(rel_types.items(), key=lambda x: -x[1])[:10]:
        md += f"| {rel} | {count} |\n"
    
    # Save
    Path(output_path).write_text(md)
    return md

if __name__ == "__main__":
    import sys
    kg_path = sys.argv[1] if len(sys.argv) > 1 else "kg.json"
    output = sys.argv[2] if len(sys.argv) > 2 else "kg-summary.md"
    print(generate_kgml(kg_path, output))
```

---

## 📊 NUTZEN

### 1. Morning Brief
KGML Summary in Morning Brief → Master sieht schnell was los ist

### 2. Debugging
Structure des KG auf einen Blick

### 3. Knowledge Gaps
Siehe was fehlt

---

## 🎯 NÄCHSTE SCHRITTE

1. ⏳ Script erstellen
2. ⏳ In Morning Cron integrieren
3. ⏳ KGML als Template für Memory Summary nutzen

---

*Erlernt aus: knowledge-graph-skill serialize.mjs Pattern*
