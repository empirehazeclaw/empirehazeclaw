#!/usr/bin/env python3
"""
KGML Summary Generator
Wandelt Knowledge Graph in lesbare Markdown Summary um.

Verwendung:
    python3 kgml_summary.py [kg_json] [output_md]
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def generate_kgml(kg_path: str = "/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json", 
                  output_path: str = "kg-summary.md") -> str:
    """Generiert KGML Summary aus KG JSON."""
    
    if not Path(kg_path).exists():
        return f"# KGML Summary\n\n*No knowledge graph found at {kg_path}*\n"
    
    with open(kg_path) as f:
        kg = json.load(f)
    
    nodes = kg.get('nodes', {})
    edges = kg.get('edges', [])
    meta = kg.get('meta', {})
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    
    # Header
    md = f"""# Knowledge Graph Summary

Generated: {now}
Entities: {len(nodes)}
Relations: {len(edges)}

"""
    
    if not nodes:
        md += "*No entities in knowledge graph*\n"
        return md
    
    # Entity Types
    types = {}
    for node in nodes.values():
        t = node.get('type', 'unknown')
        types[t] = types.get(t, 0) + 1
    
    md += "## Entity Types\n\n"
    for t, count in sorted(types.items(), key=lambda x: -x[1]):
        md += f"- **{t}**: {count}\n"
    
    # Recent Entities
    md += "\n## Recent Entities\n\n"
    recent = sorted(
        nodes.items(), 
        key=lambda x: x[1].get('created', ''), 
        reverse=True
    )[:10]
    for node_id, node in recent:
        label = node.get('label', node_id)
        ntype = node.get('type', '?')
        created = node.get('created', '?')
        md += f"- **{label}** ({ntype}) - {created}\n"
    
    # Top Entities by References
    md += "\n## Top Entities\n\n"
    by_refs = sorted(nodes.items(), 
                     key=lambda x: len(x[1].get('refs', [])), 
                     reverse=True)[:10]
    for node_id, node in by_refs:
        refs = len(node.get('refs', []))
        if refs > 0:
            md += f"- **{node.get('label', node_id)}**: {refs} refs\n"
    
    # Relation Types
    if edges:
        rel_types = {}
        for edge in edges:
            rel = edge.get('rel', 'unknown')
            rel_types[rel] = rel_types.get(rel, 0) + 1
        
        md += "\n## Relation Types\n\n"
        md += "| Relation | Count |\n|---------|-------|\n"
        for rel, count in sorted(rel_types.items(), key=lambda x: -x[1])[:10]:
            md += f"| {rel} | {count} |\n"
    
    # Meta info
    if meta:
        md += "\n## Meta\n\n"
        for k, v in meta.items():
            if k not in ['entityCount', 'edgeCount']:
                md += f"- **{k}**: {v}\n"
    
    # Save
    Path(output_path).write_text(md)
    return md

def main():
    kg_path = sys.argv[1] if len(sys.argv) > 1 else "/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json"
    output = sys.argv[2] if len(sys.argv) > 2 else "kg-summary.md"
    
    print(f"Generating KGML from {kg_path}...")
    result = generate_kgml(kg_path, output)
    print(f"✅ KGML Summary written to {output}")
    print(f"\nPreview:\n{result[:500]}...")

if __name__ == "__main__":
    main()
