#!/usr/bin/env python3
"""
Auto-Documentation Generator
Generates SCRIPTS.md from all scripts in the workspace.
"""
import os
import re
import sys

SCRIPTS_DIR = "/home/clawbot/.openclaw/workspace/scripts"
OUTPUT_FILE = "/home/clawbot/.openclaw/workspace/SCRIPTS.md"

def get_script_description(filepath):
    """Extract docstring from script."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Try to find docstring
        match = re.search(r'"""(.+?)"""', content, re.DOTALL)
        if match:
            desc = match.group(1).strip().split('\n')[0]
            return desc[:80]  # Truncate
        
        # Try to find comment-based description
        match = re.search(r'^#\s*(.+?)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()[:80]
            
    except Exception:
        pass
    return "No description"

def get_script_category(filename):
    """Determine category based on filename."""
    name = filename.lower()
    
    if any(x in name for x in ['social', 'twitter', 'tiktok', 'trend', 'viral', 'engagement']):
        return "Social Media"
    elif any(x in name for x in ['pod', 'etsy', 'printify', 'product']):
        return "POD/E-Commerce"
    elif any(x in name for x in ['trading', 'crypto', 'forex', 'portfolio']):
        return "Trading"
    elif any(x in name for x in ['backup', 'restore']):
        return "Backup"
    elif any(x in name for x in ['health', 'monitor', 'stats', 'dashboard']):
        return "Monitoring"
    elif any(x in name for x in ['security', 'shield', 'sanitizer']):
        return "Security"
    elif any(x in name for x in ['memory', 'knowledge', 'rag']):
        return "Memory/Knowledge"
    elif any(x in name for x in ['learning', 'optimizer', 'self_']):
        return "Learning"
    elif any(x in name for x in ['debug', 'repair', 'fix']):
        return "Debugging"
    elif any(x in name for x in ['test']):
        return "Testing"
    else:
        return "Utilities"

def generate_docs():
    """Generate SCRIPTS.md"""
    
    # Collect scripts
    scripts = []
    for filename in os.listdir(SCRIPTS_DIR):
        if filename.endswith('.py') and not filename.startswith('__'):
            filepath = os.path.join(SCRIPTS_DIR, filename)
            category = get_script_category(filename)
            description = get_script_description(filepath)
            scripts.append({
                'name': filename,
                'category': category,
                'description': description
            })
    
    # Group by category
    by_category = {}
    for s in scripts:
        cat = s['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(s)
    
    # Generate markdown
    md = """# 📜 Scripts Reference

*Auto-generated documentation - Updated automatically*

---

"""
    
    for category in sorted(by_category.keys()):
        md += f"## {category}\n\n"
        md += "| Script | Description |\n"
        md += "|--------|-------------|\n"
        for s in sorted(by_category[category], key=lambda x: x['name']):
            md += f"| `{s['name']}` | {s['description']} |\n"
        md += "\n"
    
    # Footer
    md += f"""---

*Total Scripts: {len(scripts)}*

*Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    # Write
    with open(OUTPUT_FILE, 'w') as f:
        f.write(md)
    
    print(f"✅ Generated {OUTPUT_FILE}")
    print(f"   Total scripts: {len(scripts)}")
    print(f"   Categories: {len(by_category)}")

if __name__ == "__main__":
    generate_docs()
