#!/usr/bin/env python3
"""
Embedding Generator — Sir HazeClaw
===================================
Generates embeddings for memory files and stores them in semantic/ folder.

Usage:
    python3 embedding_generator.py --all          # Generate all embeddings
    python3 embedding_generator.py --file <path>  # Generate single file
    python3 embedding_generator.py --daily        # Generate today's daily notes
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
CEO_MEMORY = WORKSPACE / "ceo/memory"
SEMANTIC_DIR = CEO_MEMORY / "semantic"
MODEL_NAME = "all-MiniLM-L6-v2"
DIM = 384

def get_embedding(text: str, model) -> list:
    """Generate embedding for text."""
    return model.encode([text], normalize_embeddings=True)[0].tolist()

def get_file_hash(filepath: Path) -> str:
    """Get MD5 hash of file content + mtime for cache invalidation."""
    stat = filepath.stat()
    key = f"{filepath}:{stat.st_size}:{stat.st_mtime}"
    return hashlib.md5(key.encode()).hexdigest()[:12]

def should_recompute(embed_file: Path, source_file: Path) -> bool:
    """Check if embedding needs recomputation."""
    if not embed_file.exists():
        return True
    embed_data = json.load(open(embed_file))
    if embed_data.get("source_mtime") != source_file.stat().st_mtime:
        return True
    return False

def generate_for_file(filepath: Path, model) -> dict:
    """Generate embedding for a single file."""
    content = filepath.read_text()
    
    # Split into chunks (max 512 tokens for MiniLM)
    chunks = []
    lines = content.split("\n")
    current_chunk = ""
    
    for line in lines:
        if len(current_chunk) + len(line) > 2000:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line[:2000]
        else:
            current_chunk += "\n" + line
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # Generate embedding for first chunk (summary)
    summary_emb = get_embedding(chunks[0] if chunks else "", model)
    
    return {
        "file": str(filepath),
        "hash": get_file_hash(filepath),
        "source_mtime": filepath.stat().st_mtime,
        "generated_at": datetime.now().isoformat(),
        "chunks": len(chunks),
        "embedding": summary_emb,
        "first_lines": "\n".join(chunks[:3])[:500]
    }

def scan_memory_files() -> list:
    """Scan all memory files that should be embedded."""
    files = []
    
    # Daily notes
    for f in CEO_MEMORY.glob("????-??-??.md"):
        files.append(f)
    
    # Long term knowledge
    for subdir in ["long_term", "short_term", "notes", "episodes"]:
        sub = CEO_MEMORY / subdir
        if sub.exists():
            files.extend(sub.glob("*.md"))
    
    return files

def main():
    print("🚀 Sir HazeClaw — Embedding Generator")
    print(f"   Model: {MODEL_NAME} (dim={DIM})")
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "--all"
    
    print("   Loading model...")
    model = SentenceTransformer(MODEL_NAME)
    print("   ✅ Model loaded")
    
    if mode == "--all":
        print("\n📚 Scanning memory files...")
        files = scan_memory_files()
        print(f"   Found {len(files)} files")
        
        for i, filepath in enumerate(files):
            embed_file = SEMANTIC_DIR / f"{filepath.stem}.emb.json"
            
            if not should_recompute(embed_file, filepath):
                print(f"   [skip] {filepath.name}")
                continue
            
            print(f"   [{i+1}/{len(files)}] Processing {filepath.name}...", end=" ", flush=True)
            try:
                data = generate_for_file(filepath, model)
                embed_file.write_text(json.dumps(data, indent=2))
                print("✅")
            except Exception as e:
                print(f"❌ {e}")
        
        print(f"\n✅ Done! Embeddings in {SEMANTIC_DIR}")
        
    elif mode == "--file" and len(sys.argv) > 2:
        filepath = Path(sys.argv[2])
        embed_file = SEMANTIC_DIR / f"{filepath.stem}.emb.json"
        data = generate_for_file(filepath, model)
        embed_file.write_text(json.dumps(data, indent=2))
        print(f"✅ Saved to {embed_file}")
    
    elif mode == "--daily":
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = CEO_MEMORY / f"{today}.md"
        if filepath.exists():
            data = generate_for_file(filepath, model)
            embed_file = SEMANTIC_DIR / f"{today}.emb.json"
            embed_file.write_text(json.dumps(data, indent=2))
            print(f"✅ {today}.md embedded")
        else:
            print(f"❌ No daily notes for {today}")
    
    else:
        print("Usage: embedding_generator.py [--all|--file <path>|--daily]")

if __name__ == "__main__":
    main()
