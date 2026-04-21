#!/usr/bin/env python3
"""
QMD Search — Sir HazeClaw
=========================
Wrapper for QMD CLI to provide search capabilities.
Usage:
  python3 qmd_search.py "query"
  python3 qmd_search.py "query" --collection ceo_memory
  python3 qmd_search.py "query" --files
"""

import sys
import json
import subprocess
from pathlib import Path

QMD_COLLECTIONS = {
    'ceo_memory': '/home/clawbot/.openclaw/workspace/ceo/memory',
    'obsidian_vault': '/home/clawbot/obsidian-vault',
    'workspace': '/home/clawbot/.openclaw/workspace',
}

def run_qmd(args: list) -> str:
    """Run qmd command and return output."""
    try:
        result = subprocess.run(
            ['qmd'] + args,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Error: QMD command timed out"
    except FileNotFoundError:
        return "Error: qmd not found. Install with: npm install -g @tobilu/qmd"
    except Exception as e:
        return f"Error: {e}"

def search(query: str, collection: str = 'ceo_memory', max_results: int = 10) -> dict:
    """Search using QMD."""
    if collection not in QMD_COLLECTIONS:
        return {"error": f"Unknown collection: {collection}. Available: {list(QMD_COLLECTIONS.keys())}"}
    
    # Use qmd query with collection filter
    output = run_qmd(['query', query, '-c', collection, '-n', str(max_results), '--json'])
    
    try:
        return json.loads(output)
    except:
        # Fallback to text search
        output = run_qmd(['search', query, '-c', collection, '-n', str(max_results)])
        return {"results": output, "format": "text"}

def status() -> dict:
    """Get QMD status."""
    output = run_qmd(['status'])
    return {"status_output": output}

def main():
    if len(sys.argv) < 2:
        print("Usage: qmd_search.py <query> [--collection <name>] [--files] [--status]")
        print(f"Collections: {list(QMD_COLLECTIONS.keys())}")
        sys.exit(1)
    
    query = sys.argv[1] if not sys.argv[1].startswith('--') else None
    collection = 'ceo_memory'
    files_only = '--files' in sys.argv
    status_only = '--status' in sys.argv
    
    if status_only:
        result = status()
        print(json.dumps(result, indent=2))
        sys.exit(0)
    
    for i, arg in enumerate(sys.argv[1:]):
        if arg == '--collection' and i+2 < len(sys.argv):
            collection = sys.argv[i+2]
        if arg == '--files':
            files_only = True
    
    if not query:
        print("Error: No query provided")
        sys.exit(1)
    
    result = search(query, collection, max_results=20)
    
    if files_only:
        # Just return file paths
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    print(item.get('file', item.get('path', 'unknown')))
        else:
            print(result.get('results', result))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
