#!/usr/bin/env python3
"""
Research Cache - Speichert Research-Ergebnisse für X Stunden
"""

import os
import json
import hashlib
from datetime import datetime, timedelta

CACHE_DIR = "/home/clawbot/.openclaw/workspace/memory/cache"
CACHE_HOURS = 24  # Cache für 24 Stunden

def get_cache_key(query):
    """Erstelle Cache-Key aus Query"""
    return hashlib.md5(query.encode()).hexdigest()

def get_cache_path(key):
    """Pfad zur Cache-Datei"""
    return f"{CACHE_DIR}/{key}.json"

def is_valid_cache(key):
    """Prüfe ob Cache noch gültig"""
    path = get_cache_path(key)
    if not os.path.exists(path):
        return False
    
    try:
        with open(path) as f:
            data = json.load(f)
            timestamp = datetime.fromisoformat(data["timestamp"])
            age = datetime.now() - timestamp
            return age < timedelta(hours=CACHE_HOURS)
    except:
        return False

def get_cached(key):
    """Hole gecachtes Ergebnis"""
    path = get_cache_path(key)
    if is_valid_cache(key):
        with open(path) as f:
            return json.load(f)
    return None

def set_cached(key, data):
    """Speichere Ergebnis im Cache"""
    data["timestamp"] = datetime.now().isoformat()
    path = get_cache_path(key)
    with open(path, "w") as f:
        json.dump(data, f)

def clear_old_cache():
    """Lösche alte Cache-Einträge"""
    if not os.path.exists(CACHE_DIR):
        return
    
    for filename in os.listdir(CACHE_DIR):
        if filename.endswith(".json"):
            path = os.path.join(CACHE_DIR, filename)
            try:
                with open(path) as f:
                    data = json.load(f)
                    timestamp = datetime.fromisoformat(data["timestamp"])
                    age = datetime.now() - timestamp
                    if age > timedelta(hours=CACHE_HOURS):
                        os.remove(path)
            except:
                pass

if __name__ == "__main__":
    clear_old_cache()
    print(f"✅ Cache cleaned (max age: {CACHE_HOURS}h)")
