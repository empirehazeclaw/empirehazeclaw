#!/usr/bin/env python3
"""
Sir HazeClaw Auto Documentation Generator
Generiert automatisch Dokumentation aus Script-Metadaten.

Usage:
    python3 auto_doc.py
    python3 auto_doc.py --scripts-dir scripts
    python3 auto_doc.py --update-readme
"""

import os
import re
import ast
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
README_FILE = WORKSPACE / "scripts/README.md"

def extract_docstring(filepath):
    """Extrahiert Docstring aus Python Script."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Try to parse as AST
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Module) and ast.get_docstring(node):
                    return ast.get_docstring(node)
        except:
            pass
        
        # Fallback: regex für docstring
        match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if match:
            doc = match.group(1).strip().split('\n')[0]
            return doc if doc else None
        
        return None
    except:
        return None

def extract_functions(filepath):
    """Extrahiert Functions und ihre Docs aus Script."""
    functions = []
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                doc = ast.get_docstring(node)
                functions.append({
                    'name': node.name,
                    'doc': doc.split('\n')[0] if doc else None,
                    'args': [a.arg for a in node.args.args if not a.arg.startswith('_')]
                })
    except:
        pass
    
    return functions

def get_script_info(filepath):
    """Sammelt alle Infos über ein Script."""
    stat = filepath.stat()
    
    try:
        rel_path = str(filepath.relative_to(WORKSPACE))
    except:
        rel_path = str(filepath)
    
    info = {
        'name': filepath.name,
        'path': rel_path,
        'size_kb': stat.st_size / 1024,
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d'),
        'docstring': extract_docstring(filepath),
        'functions': extract_functions(filepath),
        'has_test': filepath.name.startswith('test_') or (WORKSPACE / 'scripts' / 'test' / f'test_{filepath.stem}.py').exists(),
    }
    
    return info

def generate_script_entry(info):
    """Generiert Markdown-Eintrag für ein Script."""
    lines = []
    
    # Header mit Status
    status = '✅' if info['has_test'] else '⚠️'
    lines.append(f"### {status} `{info['name']}`")
    lines.append("")
    
    if info['docstring']:
        lines.append(f"_{info['docstring']}_")
        lines.append("")
    
    # Functions
    if info['functions']:
        lines.append("**Functions:**")
        for f in info['functions'][:5]:  # Max 5
            args = ', '.join(f['args'][:3]) if f['args'] else ''
            doc = f' — {f["doc"][:50]}' if f['doc'] else ''
            lines.append(f"- `{f['name']}({args})`{doc}")
        lines.append("")
    
    # Meta
    lines.append(f"| Modified | Size |")
    lines.append(f"|----------|------|")
    lines.append(f"| {info['modified']} | {info['size_kb']:.1f}KB |")
    lines.append("")
    
    return '\n'.join(lines)

def generate_readme(scripts):
    """Generiert komplette README.md."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    
    # Sort by modified date
    scripts.sort(key=lambda x: x['modified'], reverse=True)
    
    lines = []
    lines.append("# Sir HazeClaw Scripts")
    lines.append("")
    lines.append(f"_Generated: {now}_")
    lines.append("")
    lines.append(f"**Total Scripts:** {len(scripts)}")
    lines.append(f"**With Tests:** {sum(1 for s in scripts if s['has_test'])}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📁 Scripts by Category")
    lines.append("")
    
    # Group by prefix
    categories = {}
    for s in scripts:
        name = s['name']
        if '_' in name:
            prefix = name.split('_')[0]
        else:
            prefix = 'other'
        
        if prefix not in categories:
            categories[prefix] = []
        categories[prefix].append(s)
    
    for cat in sorted(categories.keys()):
        cat_scripts = categories[cat]
        lines.append(f"### {cat.title()}")
        lines.append("")
        lines.append(f"_{len(cat_scripts)} scripts_")
        lines.append("")
        for s in cat_scripts[:10]:
            status = '✅' if s['has_test'] else '⚠️'
            doc = f" — {s['docstring'][:60]}" if s['docstring'] else ""
            lines.append(f"- {status} `{s['name']}`{doc}")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("## 📊 All Scripts")
    lines.append("")
    
    for s in scripts:
        lines.append(generate_script_entry(s))
    
    lines.append("")
    lines.append("---")
    lines.append(f"_Auto-generated by Sir HazeClaw_")
    
    return '\n'.join(lines)

def update_script_docs():
    """Updated Script-spezifische Docs."""
    updated = []
    
    for script in SCRIPTS_DIR.glob('*.py'):
        if script.name.startswith('_'):
            continue
        
        content = script.read_text()
        
        # Check if has proper docstring
        if '"""' not in content[:500]:
            # Script braucht Dokumentation
            doc = f'"""{script.stem.replace("_", " ").title()}"""'
            
            if not content.startswith('#!'):
                new_content = f'#!/usr/bin/env python3\n"""{script.stem.replace("_", " ").title()}"""\n\n' + content
            else:
                new_content = content
        
        updated.append(script.name)
    
    return updated

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto Documentation Generator')
    parser.add_argument('--scripts-dir', default='scripts', help='Scripts directory')
    parser.add_argument('--update-readme', action='store_true', help='Update README.md')
    args = parser.parse_args()
    
    scripts_dir = WORKSPACE / args.scripts_dir
    
    print(f"📄 Auto Documentation Generator")
    print(f"   Scripts Dir: {scripts_dir}")
    print()
    
    # Collect script info
    scripts = []
    for script in sorted(scripts_dir.glob('*.py')):
        if script.name.startswith('_') or script.name in ['__init__.py']:
            continue
        
        info = get_script_info(script)
        scripts.append(info)
        print(f"  {'✅' if info['has_test'] else '⚠️'} {info['name']}")
    
    print()
    print(f"Total: {len(scripts)} scripts")
    print(f"With tests: {sum(1 for s in scripts if s['has_test'])}")
    
    if args.update_readme:
        print()
        print("📝 Generating README.md...")
        readme = generate_readme(scripts)
        
        readme_path = scripts_dir / 'README.md'
        readme_path.write_text(readme)
        print(f"  ✅ Updated: {readme_path}")
        
        # Also update workspace README if exists
        workspace_readme = WORKSPACE / 'README.md'
        if workspace_readme.exists():
            # Just note that scripts README was updated
            pass
    
    print()
    print("✅ Auto-documentation complete")

if __name__ == "__main__":
    main()
