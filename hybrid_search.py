#!/usr/bin/env python3
"""
🔍 Hybrid Search - QMD Integration
Verbindet Keyword + Vector + Reranking
"""
import subprocess
import sys

MEMORY_PATH = "/home/clawbot/.openclaw/workspace/memory"

def search(query: str, mode: str = "hybrid"):
    """Search using QMD"""
    
    if mode == "hybrid":
        cmd = ["qmd", "query", query]
    elif mode == "keyword":
        cmd = ["qmd", "search", query]
    elif mode == "semantic":
        cmd = ["qmd", "vsearch", query]
    else:
        cmd = ["qmd", "query", query]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 hybrid_search.py <query>")
        print("       python3 hybrid_search.py --mode semantic <query>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    # Default: hybrid search
    mode = "hybrid"
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]
            query = query.replace(f"--mode {mode}", "").strip()
    
    print(f"🔍 Searching: {query}")
    print(f"Mode: {mode}")
    print("-" * 50)
    
    results = search(query, mode)
    print(results)

if __name__ == "__main__":
    main()
