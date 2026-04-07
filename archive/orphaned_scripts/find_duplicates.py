#!/usr/bin/env python3
"""
Duplicates Finder
Findet .md Files mit ähnlichem Inhalt
"""
import os
import hashlib
from pathlib import Path
from collections import defaultdict

MEMORY_DIR = Path("/home/clawbot/.openclaw/workspace/memory")

def get_file_hash(filepath):
    """Berechnet MD5 Hash eines Files"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def find_duplicates():
    """Findet doppelte Files"""
    print(f"🔍 Scanne memory/ nach Duplikaten...")
    
    # Files nach Hash gruppieren
    hash_to_files = defaultdict(list)
    
    for root, dirs, files in os.walk(MEMORY_DIR):
        # Skip archive
        if 'archive' in root:
            continue
        
        for f in files:
            if not f.endswith('.md'):
                continue
            
            filepath = Path(root) / f
            try:
                file_hash = get_file_hash(filepath)
                rel_path = str(filepath.relative_to(MEMORY_DIR))
                hash_to_files[file_hash].append(rel_path)
            except:
                pass
    
    # Nur Duplikate anzeigen
    duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
    
    if duplicates:
        print(f"\n⚠️ {len(duplicates)} Duplikate gefunden:\n")
        for files in duplicates.values():
            print(f"   📄 {files[0]}")
            for f in files[1:]:
                print(f"      → Duplikat: {f}")
            print()
    else:
        print("   ✅ Keine Duplikate gefunden!")
    
    # Ähnliche Namen finden
    print("\n🔍 Ähnliche Dateinamen:")
    names = defaultdict(list)
    for root, dirs, files in os.walk(MEMORY_DIR):
        for f in files:
            if f.endswith('.md'):
                base = f.replace('.md', '').lower()
                names[base].append(str(Path(root).relative_to(MEMORY_DIR) / f))
    
    similar = {n: files for n, files in names.items() if len(files) > 1}
    if similar:
        for name, files in similar.items():
            print(f"   📁 {name}:")
            for f in files:
                print(f"      → {f}")
    else:
        print("   ✅ Keine ähnlichen Namen!")

if __name__ == "__main__":
    print(f"{'='*50}")
    print(f"🔎 DUPLICATES FINDER")
    print(f"{'='*50}")
    find_duplicates()
