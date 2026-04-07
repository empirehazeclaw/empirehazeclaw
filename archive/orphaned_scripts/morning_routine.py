#!/usr/bin/env python3
"""
🌅 Morning Routine - Consolidated Morning Scripts
================================================
Combines: morning_brief.py + morning_bundle.py

Functions:
- Weather Report (Freiburg)
- Token Report
- Exercise of the Day
- Script Bundle Runner
"""

import json
import os
import subprocess
import fcntl
import sys
from datetime import datetime
from pathlib import Path

# ============== CONFIG ==============
WORKSPACE = "/home/clawbot/.openclaw/workspace"
WEATHER_FILE = "/home/clawbot/.openclaw/logs/weather.json"
TOKEN_FILE = "/home/clawbot/.openclaw/logs/tokens.json"
LOCK_FILE = "/home/clawbot/.openclaw/workspace/data/.morning_routine.lock"

# ============== FILE LOCKING ==============
def acquire_lock():
    """Acquire exclusive file lock to prevent race conditions"""
    lock_path = Path(LOCK_FILE)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = open(lock_path, 'w')
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        return lock_fd
    except BlockingIOError:
        print(f"[{datetime.now()}] Another instance is running. Exiting.")
        sys.exit(0)

def release_lock(lock_fd):
    """Release the file lock"""
    fcntl.flock(lock_fd, fcntl.LOCK_UN)
    lock_fd.close()

# ============== WEATHER ==============
def get_weather():
    """Get current weather for Freiburg"""
    try:
        import requests
        lat, lon = 47.99, 7.84
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        resp = requests.get(url, timeout=10).json()
        
        w = resp.get("current_weather", {})
        temp = w.get("temperature", "?")
        wind = w.get("windspeed", "?")
        code = w.get("weathercode", 0)
        
        # Weather code to emoji
        codes = {0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 48: "🌫️", 
                 51: "🌧️", 53: "🌧️", 55: "🌧️", 61: "🌧️", 63: "🌧️", 65: "🌧️",
                 71: "🌨️", 73: "🌨️", 75: "🌨️", 80: "🌦️", 81: "🌦️", 82: "🌦️", 95: "⛈️"}
        emoji = codes.get(code, "❓")
        
        return f"{emoji} {temp}°C, Wind {wind} km/h"
    except Exception as e:
        return f"❌ Weather Error: {e}"

# ============== TOKEN REPORT ==============
def get_token_report():
    """Get token usage from logs"""
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE) as f:
                data = json.load(f)
            
            total = data.get("total_tokens", 0)
            cost = data.get("total_cost", 0)
            return f"Tokens: {total:,} | Cost: ${cost:.2f}"
        return "No token data"
    except:
        return "No token data"

# ============== EXERCISE ==============
def get_exercise():
    """Get daily exercise recommendation for knee rehab"""
    import random
    exercises = [
        ("Monday", "🦵 Kniebeugen + Beinpresse"),
        ("Tuesday", "🚶 Spaziergang +平衡 Training"),
        ("Wednesday", "🏋️ Kreuzheben (leicht) + Klimmzüge"),
        ("Thursday", "🦵 Kniebeugen + Goblet Squat"),
        ("Friday", "🚶 Spaziergang + Dehnung"),
        ("Saturday", "🏋️ Full Body Workout"),
        ("Sunday", "🧘 Ruhe + Light Stretching"),
    ]
    day = datetime.now().strftime("%A")
    return exercises[[d[0] for d in exercises].index(day)][1] if day in [d[0] for d in exercises] else "🦵 Basis Übungen"

# ============== SCRIPT RUNNER ==============
def run_script(name, path):
    """Run a script and return success/fail"""
    try:
        result = subprocess.run(
            ["python3", path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=WORKSPACE
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

# ============== MAIN ==============
def main():
    lock_fd = acquire_lock()
    try:
        print("🌅 Morning Routine")
        print("=" * 40)
        
        # Get data
        weather = get_weather()
        tokens = get_token_report()
        exercise = get_exercise()
        
        print(f"\n📍 Freiburg: {weather}")
        print(f"💰 {tokens}")
        print(f"\n🦵 Training heute: {exercise}")
        
        # Run bundle scripts (optional)
        scripts = [
            ("Librarian", f"{WORKSPACE}/scripts/librarian_agent.py"),
        ]
        
        print("\n📦 Running bundle...")
        success = 0
        for name, path in scripts:
            if os.path.exists(path):
                if run_script(name, path):
                    print(f"  ✅ {name}")
                    success += 1
                else:
                    print(f"  ❌ {name}")
        
        print(f"\n✅ Morning Routine complete ({success}/{len(scripts)} scripts)")
        return True
    finally:
        release_lock(lock_fd)

if __name__ == "__main__":
    main()
