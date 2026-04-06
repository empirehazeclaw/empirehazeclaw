#!/usr/bin/env python3
"""
Token Usage Tracker - Reads session stats and tracks tokens
"""

import json
import os
from datetime import datetime, date

TOKEN_FILE = "/home/clawbot/.openclaw/logs/tokens.json"

# Cost per 1M tokens
COSTS = {
    "minimax/MiniMax-M2.5": {"input": 0.30, "output": 1.20, "currency": "€"},
    "minimax/MiniMax-M4": {"input": 1.00, "output": 4.00, "currency": "€"},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60, "currency": "$"},
    "openai/gpt-4o": {"input": 2.50, "output": 10.00, "currency": "$"},
    "google/gemini-2.0-flash-001": {"input": 0.0, "output": 0.0, "currency": "$"},
    "google/gemini-2.0-flash": {"input": 0.0, "output": 0.0, "currency": "$"},
    "ollama/qwen2.5:3b": {"input": 0.0, "output": 0.0, "currency": "€"},
    "ollama/*": {"input": 0.0, "output": 0.0, "currency": "€"},
    "default": {"input": 0.0, "output": 0.0, "currency": "€"},
}

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return {"daily": {}, "history": []}

def save_tokens(data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2)

def track(model, input_tokens=0, output_tokens=0):
    """Manually track token usage"""
    data = load_tokens()
    today = str(date.today())
    
    cost_info = COSTS.get(model, COSTS["default"])
    input_cost = (input_tokens / 1_000_000) * cost_info["input"]
    output_cost = (output_tokens / 1_000_000) * cost_info["output"]
    total_cost = input_cost + output_cost
    
    # Daily tracking
    if today not in data["daily"]:
        data["daily"][today] = {}
    
    if model not in data["daily"][today]:
        data["daily"][today][model] = {"input": 0, "output": 0, "cost": 0}
    
    data["daily"][today][model]["input"] += input_tokens
    data["daily"][today][model]["output"] += output_tokens
    data["daily"][today][model]["cost"] += total_cost
    
    # History
    data["history"].append({
        "date": today,
        "model": model,
        "input": input_tokens,
        "output": output_tokens,
        "cost": round(total_cost, 4)
    })
    
    # Keep last 30 days
    data["history"] = data["history"][-1000:]
    
    save_tokens(data)
    return total_cost

def estimate_from_sessions():
    """Estimate token usage from session activity"""
    data = load_tokens()
    today = str(date.today())
    
    # Rough estimates based on session count
    # Each session = ~10k-50k tokens depending on activity
    # This is rough - for exact tracking we'd need API callbacks
    
    return None  # Not implemented yet

def report():
    """Generate daily report"""
    data = load_tokens()
    today = str(date.today())
    
    if today not in data["daily"]:
        return f"No data for {today}"
    
    day_data = data["daily"][today]
    
    total_input = sum(d["input"] for d in day_data.values())
    total_output = sum(d["output"] for d in day_data.values())
    total_cost = sum(d["cost"] for d in day_data.values())
    
    # Calculate EUR
    eur_cost = total_cost  # Already in EUR for most
    
    lines = [f"📊 Token Report - {today}"]
    lines.append(f"Input: {total_input:,} tokens")
    lines.append(f"Output: {total_output:,} tokens")
    lines.append(f"Cost: €{eur_cost:.2f}")
    lines.append("")
    lines.append("By Model:")
    
    for model, d in day_data.items():
        lines.append(f"  {model}: {d['input']+d['output']:,} tokens (€{d['cost']:.2f})")
    
    return "\n".join(lines)

def compare_days(days=7):
    """Compare with previous days"""
    data = load_tokens()
    today = str(date.today())
    
    results = []
    for i in range(days):
        from datetime import timedelta
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        if d in data["daily"]:
            total = sum(x["cost"] for x in data["daily"][d].values())
            results.append((d, total))
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "report":
            print(report())
        elif sys.argv[1] == "track" and len(sys.argv) == 5:
            model = sys.argv[2]
            inp = int(sys.argv[3])
            out = int(sys.argv[4])
            track(model, inp, out)
            print(f"Tracked: {model} {inp}+{out}")
        elif sys.argv[1] == "compare":
            for d, c in compare_days(7):
                print(f"{d}: €{c:.2f}")
        else:
            print("Usage: token_tracker.py [report|track MODEL IN OUT|compare]")
    else:
        # Show today's report
        print(report())
