#!/usr/bin/env python3
"""
API Key Monitor - Check API key balances and usage
"""

import os
import requests
import json
from datetime import datetime

# API Keys
KEYS = {
    "LEONARDO": os.getenv("LEONARDO_API_KEY", "45ac842f-e8b8-44f9-bd8e-0ce9ad9dd599"),
    "OPENAI": os.getenv("OPENAI_API_KEY", ""),
    "GEMINI": os.getenv("GEMINI_API_KEY", ""),
}

LOG_FILE = "/home/clawbot/.openclaw/logs/api_monitor.json"

def check_leonardo():
    """Check Leonardo.ai tokens"""
    try:
        url = "https://cloud.leonardo.ai/api/rest/v1/me"
        headers = {"Authorization": f"Bearer {KEYS['LEONARDO']}"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            user = data.get("user_details", [{}])[0].get("user", {})
            return {
                "name": "Leonardo",
                "paid_tokens": user.get("apiPaidTokens", 0),
                "subscription_tokens": user.get("subscriptionTokens", 0),
                "status": "OK" if user.get("apiPaidTokens", 0) > 100 else "LOW"
            }
    except Exception as e:
        return {"name": "Leonardo", "status": "ERROR", "error": str(e)}
    return {"name": "Leonardo", "status": "UNKNOWN"}

def check_openai():
    """Check OpenAI usage"""
    # OpenAI needs a date parameter - check if we have key
    if not KEYS['OPENAI']:
        return {"name": "OpenAI", "status": "NO_KEY"}
    
    try:
        # Just check if key is valid
        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {KEYS['OPENAI']}"}
        r = requests.get(url, headers=headers, timeout=10)
        return {
            "name": "OpenAI",
            "status": "OK" if r.status_code == 200 else "INVALID"
        }
    except Exception as e:
        return {"name": "OpenAI", "status": "ERROR", "error": str(e)}

def check_gemini():
    """Check Gemini quota"""
    if not KEYS['GEMINI']:
        return {"name": "Gemini", "status": "NO_KEY"}
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models?key={KEYS['GEMINI']}"
        r = requests.get(url, timeout=10)
        return {
            "name": "Gemini",
            "status": "OK" if r.status_code == 200 else "INVALID"
        }
    except Exception as e:
        return {"name": "Gemini", "status": "ERROR", "error": str(e)}

def check_all():
    """Check all APIs"""
    results = []
    
    results.append(check_leonardo())
    results.append(check_openai())
    results.append(check_gemini())
    
    # Log
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=2)
    
    # Check for low/warning
    warnings = []
    for r in results:
        if r.get("status") == "LOW":
            warnings.append(f"⚠️ {r['name']}: Nur noch {r.get('paid_tokens', 0)} Tokens")
        elif r.get("status") == "ERROR":
            warnings.append(f"❌ {r['name']}: {r.get('error', 'Error')}")
    
    return warnings

if __name__ == "__main__":
    warnings = check_all()
    
    if warnings:
        print("\n".join(warnings))
    else:
        print("✅ Alle API Keys OK")
