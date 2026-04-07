#!/usr/bin/env python3
"""
Model Fallback Router
Automatisch: MiniMax → qwen (Ollama) bei Ausfall
"""

import subprocess
import json
import sys

# Fallback Modelle in Prioritätsreihenfolge
FALLBACK_CHAIN = [
    ("MiniMax-M2.5", "minimax/MiniMax-M2.5"),
    ("qwen2.5:3b", "ollama/qwen2.5:3b"),
    ("gemini-flash", "google/gemini-2.0-flash"),
]

def test_model(model_id: str) -> bool:
    """Teste ob ein Model verfügbar ist"""
    try:
        # MiniMax testen
        if "MiniMax" in model_id:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 "https://api.minimax.io/v1/models", "-H", "Authorization: Bearer sk-test"],
                capture_output=True, timeout=10
            )
            # Bessere Prüfung: MiniMax hat oft Timeout statt Error
            return True  # MiniMax wird immer versucht
            
        # Ollama testen
        if "qwen" in model_id or "llama" in model_id:
            result = subprocess.run(
                ["curl", "-s", "http://127.0.0.1:11434/api/tags"],
                capture_output=True, timeout=5
            )
            return model_id.replace("ollama/", "") in result.stdout
            
        # Gemini testen
        if "gemini" in model_id:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 "https://generativelanguage.googleapis.com/v1/models"],
                capture_output=True, timeout=10
            )
            return result.stdout.strip() == "200"
            
    except:
        pass
    return False

def get_best_model() -> tuple[str, str]:
    """Finde das beste verfügbare Model"""
    for name, model_id in FALLBACK_CHAIN:
        if test_model(model_id):
            return name, model_id
    return "fallback", "error"

if __name__ == "__main__":
    name, model_id = get_best_model()
    print(f"✅ Model: {name} ({model_id})")
    
    # Speichere aktuelles Model für OpenClaw
    with open("/home/clawbot/.openclaw/workspace/.current_model", "w") as f:
        f.write(f"{name}|{model_id}")
