#!/usr/bin/env python3
"""Load memory DB at startup"""
import sys
sys.path.insert(0, 'scripts')
from memory_db import search_memory, get_priority, seed_master_memory

def morning_memory_check():
    """What runs every morning"""
    print("=== 🧠 MORNING MEMORY CHECK ===")
    
    # Load P1 items
    p1 = get_priority("P1")
    print(f"\n🔴 P1 (Must Know): {len(p1)} items")
    for item in p1[:2]:
        print(f"  - {item[:100]}...")
    
    # Check recent decisions
    results = search_memory("today")
    print(f"\n🟡 Recent: {len(results)} items")
    
    return "Memory loaded!"

if __name__ == "__main__":
    morning_memory_check()
