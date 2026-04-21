#!/usr/bin/env python3
"""
Code Generator — Sir HazeClaw Phase 8 Option B
==============================================
Generates actual Python code from improvement ideas.

Usage:
    python3 code_generator.py --generate --title "Fix timeout" --description "..."
    python3 code_generator.py --from-json --file improvement.json

Phase 8 of Self-Improvement Plan
"""

import os
import sys
import json
import re
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
GENERATED_DIR = WORKSPACE / "SCRIPTS" / "automation" / "generated"


def get_api_key() -> str:
    """Get MiniMax API key."""
    try:
        secrets_path = Path("/home/clawbot/.openclaw/secrets.env")
        if secrets_path.exists():
            for line in secrets_path.read_text().split('\n'):
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    if k == 'MINIMAX_API_KEY':
                        return v
    except:
        pass
    return os.environ.get('MINIMAX_API_KEY', '')


def extract_code_from_response(content_text: str) -> str:
    """Extract Python code from LLM response text."""
    code = content_text.strip()
    
    # Remove markdown code block markers
    if code.startswith('```python'):
        code = code[9:]
    elif code.startswith('```'):
        code = code[3:]
    
    if code.endswith('```'):
        code = code[:-3]
    
    return code.strip()


def generate_code(issue: str, context: Dict) -> Tuple[str, str]:
    """Generate Python code using LLM."""
    api_key = get_api_key()
    if not api_key:
        return '', ''
    
    base_name = context.get('base_name', 'generated_script')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{base_name}_{timestamp}.py"
    
    prompt = f"""Du bist ein Python-Programmierer. Erstell ein komplettes, ausführbares Python-Script:

PROBLEM: {issue}

Anforderungen:
- Das Script muss vollständig sein (keine unvollständigen Funktionen)
- Error handling mit try/except
- Hauptfunktion mit if __name__ == "__main__":
- python3 kompatibel
- Unter 500 Zeilen

Antworte mit dem kompletten Code, nichts anderes."""

    try:
        data = {
            'model': 'MiniMax-M2.7',
            'max_tokens': 12000,  # Higher limit for comprehensive code generation
            'messages': [{'role': 'user', 'content': prompt}]
        }
        
        req = urllib.request.Request(
            'https://api.minimax.io/anthropic/v1/messages',
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            # Extract text from response - handle both 'text' and 'thinking' types
            content_text = ''
            for c in result.get('content', []):
                if isinstance(c, dict):
                    # Skip thinking blocks, look for actual text content
                    if c.get('type') == 'text' and 'text' in c:
                        content_text = c.get('text', '')
                        break
            
            # If no text found, check if there's thinking content we should parse
            if not content_text:
                for c in result.get('content', []):
                    if isinstance(c, dict) and c.get('type') == 'thinking':
                        # The thinking block might contain the code at the end after "Thus final answer"
                        thinking = c.get('thinking', '')
                        # Look for code block markers in thinking
                        if '```python' in thinking:
                            # Extract code from thinking
                            content_text = thinking
                            break
            
            code = extract_code_from_response(content_text)
            return code, filename
            
    except Exception as e:
        print(f"Error generating code: {e}")
        return '', ''


def save_code(code: str, filename: str) -> Optional[str]:
    """Save generated code to file."""
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    filepath = GENERATED_DIR / filename
    try:
        filepath.write_text(code)
        return str(filepath)
    except Exception as e:
        print(f"Error saving code: {e}")
        return None


def generate_for_improvement(improvement: Dict) -> Dict:
    """Generate code for an improvement idea."""
    title = improvement.get('title', '')
    description = improvement.get('description', improvement.get('title', ''))
    
    base_name = re.sub(r'[^a-zA-Z0-9]', '_', title.lower())[:30]
    
    code, filename = generate_code(
        issue=f"{title}. {description}",
        context={'base_name': base_name}
    )
    
    if not code:
        return {'success': False, 'error': 'Code generation failed'}
    
    filepath = save_code(code, filename)
    if not filepath:
        return {'success': False, 'error': 'Failed to save code'}
    
    # Verify syntax
    try:
        import py_compile
        py_compile.compile(filepath, doraise=True)
        syntax_ok = True
    except:
        syntax_ok = False
    
    return {
        'success': True,
        'code': code,
        'filename': filename,
        'filepath': filepath,
        'syntax_ok': syntax_ok
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Code Generator")
    subparsers = parser.add_subparsers(dest="command")
    
    gen_parser = subparsers.add_parser("generate", help="Generate code")
    gen_parser.add_argument("--title", required=True)
    gen_parser.add_argument("--description", default="")
    gen_parser.add_argument("--type", default="automation")
    
    json_parser = subparsers.add_parser("from-json", help="Generate from JSON")
    json_parser.add_argument("--file", required=True)
    
    args = parser.parse_args()
    
    if args.command == "generate":
        improvement = {
            'title': args.title,
            'description': args.description or args.title,
            'type': args.type
        }
        result = generate_for_improvement(improvement)
        
        if result['success']:
            print(f"✅ Generated: {result['filename']}")
            print(f"   Syntax OK: {result['syntax_ok']}")
            print(f"   Path: {result['filepath']}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    
    elif args.command == "from-json":
        with open(args.file) as f:
            improvement = json.load(f)
        result = generate_for_improvement(improvement)
        
        if result['success']:
            print(f"✅ Generated: {result['filename']}")
            print(f"   Syntax OK: {result['syntax_ok']}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
