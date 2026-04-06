#!/usr/bin/env python3
"""
Auto Cost Tracker - Integrates with OpenClaw sessions to track usage automatically.
Run this via cron every 5 minutes for live tracking.
"""

import json
import subprocess
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "costs.db"

# MiniMax pricing (as of 2026)
MODEL_PRICING = {
    "MiniMax-M2.5": {"input": 0.000002, "output": 0.000008},  # $2/M input, $8/M output
    "MiniMax-M2.5-Highspeed": {"input": 0.000004, "output": 0.000016},
    "MiniMax-VL-01": {"input": 0.000003, "output": 0.000015},
    "MiniMax-M2": {"input": 0.000002, "output": 0.000008},
    "GPT-4o-Mini": {"input": 0.00000015, "output": 0.0000006},  # $0.15/M input
    "Gemini-2.0-Flash": {"input": 0.0000001, "output": 0.0000004},  # Free tier pricing
    "gemini-2.0-flash": {"input": 0.0000001, "output": 0.0000004},
    "qwen2.5:3b": {"input": 0.0000000, "output": 0.0000000},  # Local/Ollama - free
    "llama3.2": {"input": 0.0000000, "output": 0.0000000},  # Local - free
    # Default fallback pricing (~$1/M input, $4/M output)
    "default": {"input": 0.000001, "output": 0.000004},
}

PROVIDER_MAP = {
    "minimax": "MiniMax",
    "openai": "OpenAI",
    "google": "Google",
    "ollama": "Ollama",
}


def get_sessions():
    """Fetch sessions from OpenClaw CLI."""
    try:
        result = subprocess.run(
            ["openclaw", "sessions", "--json", "--all-agents"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Error fetching sessions: {e}")
    return None


def init_db():
    """Initialize database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS auto_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_key TEXT,
            model TEXT,
            provider TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER,
            total_tokens INTEGER,
            estimated_cost REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session_key ON auto_usage(session_key)")
    conn.commit()
    return conn


def track_usage():
    """Track usage from OpenClaw sessions."""
    sessions_data = get_sessions()
    if not sessions_data or "sessions" not in sessions_data:
        print("No sessions data found")
        return
    
    conn = init_db()
    
    # Get existing session keys to track deltas
    existing = {}
    cursor = conn.execute("SELECT session_key, input_tokens, output_tokens FROM auto_usage")
    for row in cursor:
        existing[row[0]] = {"input": row[1], "output": row[2]}
    
    tracked = 0
    total_cost = 0.0
    
    for session in sessions_data["sessions"]:
        key = session.get("key", "")
        model = session.get("model", "unknown")
        provider = session.get("modelProvider", "unknown")
        input_tokens = session.get("inputTokens", 0)
        output_tokens = session.get("outputTokens", 0)
        
        if not model or input_tokens == 0:
            continue
        
        # Calculate cost
        pricing = MODEL_PRICING.get(model, MODEL_PRICING.get("default"))
        cost = (input_tokens / 1_000_000 * pricing["input"] + 
                output_tokens / 1_000_000 * pricing["output"])
        
        # Store current state
        conn.execute("""
            INSERT OR REPLACE INTO auto_usage 
            (session_key, model, provider, input_tokens, output_tokens, total_tokens, estimated_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (key, model, provider, input_tokens, output_tokens, input_tokens + output_tokens, cost))
        
        tracked += 1
        total_cost += cost
    
    conn.commit()
    conn.close()
    
    print(f"✅ Tracked {tracked} sessions | Total cost: ${total_cost:.4f}")
    return tracked, total_cost


if __name__ == "__main__":
    track_usage()
