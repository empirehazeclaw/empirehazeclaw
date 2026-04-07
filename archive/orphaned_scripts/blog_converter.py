#!/usr/bin/env python3
"""
📝 BLOG POST CONVERTER
=====================
Konvertiert Markdown Blog Posts automatisch nach HTML.
"""

import os
import re
import sys

def md_to_html(md_path, output_path=None):
    """Convert markdown to HTML blog post"""
    
    with open(md_path, 'r') as f:
        md_content = f.read()
    
    # Extract title from first # heading
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Blog Post"
    
    # Extract description if exists
    desc_match = re.search(r'^##\s+(.+)$', md_content, re.MULTILINE)
    description = desc_match.group(1) if desc_match else f"Article about {title}"
    
    html = f'''---
title: "{title}"
description: "{description}"
date: 2026-03-21
---

<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - EmpireHazeClaw</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background: #0a0a0f; color: #fff; line-height: 1.7; padding: 2rem; max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #00ff88; font-size: 2.5rem; margin-bottom: 1rem; }}
        h2 {{ color: #fff; margin-top: 2rem; }}
        p {{ color: #aaa; margin-bottom: 1rem; }}
        li {{ color: #aaa; margin-bottom: 0.5rem; }}
        a {{ color: #00ff88; }}
        .back {{ display: inline-block; margin-bottom: 2rem; color: #888; text-decoration: none; }}
        .back:hover {{ color: #00ff88; }}
    </style>
</head>
<body>
    <a href="/" class="back">← Zurück</a>
    <article>
        <h1>{title}</h1>
'''
    
    # Simple markdown conversion
    lines = md_content.split('\n')
    in_list = False
    in_table = False
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('# '):
            continue
            
        if line.startswith('## '):
            if in_list:
                html += '</ul>\n'
                in_list = False
            if in_table:
                html += '</table>\n'
                in_table = False
            html += f'<h2>{line[3:]}</h2>\n'
        elif line.startswith('### '):
            html += f'<h3>{line[4:]}</h3>\n'
        elif line.startswith('- '):
            if not in_list:
                html += '<ul>\n'
                in_list = True
            # Process bold
            item = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line[2:])
            html += f'<li>{item}</li>\n'
        elif '|' in line and line.startswith('|'):
            if not in_table:
                html += '<table><tr>'
                in_table = True
            cols = [c.strip() for c in line.split('|') if c.strip()]
            for c in cols:
                html += f'<td>{c}</td>'
            html += '</tr>\n'
        else:
            if in_list:
                html += '</ul>\n'
                in_list = False
            if in_table:
                html += '</table>\n'
                in_table = False
            # Process bold
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            html += f'<p>{line}</p>\n'
    
    if in_list:
        html += '</ul>\n'
    if in_table:
        html += '</table>\n'
    
    html += '''
    </article>
</body>
</html>'''
    
    # Determine output path
    if not output_path:
        filename = os.path.basename(md_path).replace('.md', '.html')
        output_path = f'/var/www/empirehazeclaw-info/posts/{filename}'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 blog_converter.py <markdown_file.md>")
        sys.exit(1)
    
    md_file = sys.argv[1]
    output = md_to_html(md_file)
    print(f"✅ Konvertiert: {output}")
