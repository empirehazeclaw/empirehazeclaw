#!/usr/bin/env python3
"""
Smart Model Router - v4 (INTELLIGENT)
Optimiert für Kosten, Qualität & Speed

Neue Modelle:
- hunter-alpha: meta-llama/llama-3.3-70b-instruct (kostengünstig, schnell)
- healer-alpha: anthropic/claude-3.5-sonnet (beste Qualität)
- minimax-m2.5: MiniMax M2.5 (kostenlos via Portal)
"""

import json
from typing import Dict, List, Optional

# Task-Definitionen mit Keywords
TASK_KEYWORDS = {
    "coding": [
        "code", "script", "programm", "schreibe", "python", "bash", "debug", 
        "fix", "funktion", "html", "css", "js", "java", "api", "build",
        "erstelle eine", "webseite", "app", "software", "deploy"
    ],
    "research": [
        "recherchiere", "suche", "analyse", "vergleiche", "was ist", 
        "wie funktioniert", "finde", "information", "trends", "markt",
        "调查", "research", "analyze"
    ],
    "trading": [
        "trade", "aktie", "kurs", "bitcoin", "invest", "börse", 
        "signal", "chart", "markt", "preis", "prognose", " trading"
    ],
    "creative": [
        "bild", "design", "erstelle bild", "generate", "zeichnen", 
        "art", "logo", "video", "musik", "text", "gedicht", "geschichte",
        "write a", "create", "generate", "bild", "art"
    ],
    "analysis": [
        "erkläre", "bewerte", "empfehle", "strategie", "plan", "konzept",
        "automatisiere", "optimiere", "verstehe", "why", "warum",
        "ausführlich", "detailiert", "analyse"
    ],
    "quick": [
        "zeit", "uhr", "datum", "status", "test", "ping", "hi", "hallo", 
        "ja", "nein", "ok", "wie geht", "danke", "thanks", "help"
    ],
    "long_context": [
        "dokument", "pdf", "buch", " lange", "zusammenfassung", "whole",
        "komplett", "全面", "analyze this document"
    ],
    "safety_critical": [
        "sicherheit", "security", "password", "api key", "secret",
        "vertraulich", "sensitive", "protect", "encryption"
    ]
}

# Kosten pro 1M tokens (USD)
MODEL_COSTS = {
    "hunter-alpha": {"input": 0.10, "output": 0.10},      # Llama 3.3
    "healer-alpha": {"input": 3.00, "output": 15.00},     # Claude 3.5
    "minimax-m2.5": {"input": 0, "output": 0},           # Kostenlos (Portal)
    "gemini-flash": {"input": 0.10, "output": 0.10},     # Gemini 2.0
    "gpt-4o": {"input": 2.50, "output": 10.00},         # GPT-4o
    "ollama/qwen2.5:3b": {"input": 0, "output": 0},     # KOSTENLOS (lokal)
}

# Context Limits
MODEL_CONTEXT = {
    "hunter-alpha": 128000,
    "healer-alpha": 200000,
    "minimax-m2.5": 200000,
    "gemini-flash": 1048576,  # 1M!
    "gpt-4o": 128000,
}

# INTELLIGENT Model Chains - Optimized mit MAXIMALER SICHERHEIT
# Immer: [primary] → [minimax (kostenlos)] → [ollama qwen (lokal, €0)]
MODEL_CHAINS = {
    "coding": {
        "primary": "hunter-alpha",
        "fallbacks": ["minimax-m2.5", "ollama/qwen2.5:3b"],
        "reason": "Schnell + günstig für Code"
    },
    "research": {
        "primary": "gemini-flash", 
        "fallbacks": ["minimax-m2.5", "ollama/qwen2.5:3b"],
        "reason": "Größte Knowledge Base"
    },
    "trading": {
        "primary": "gemini-flash",
        "fallbacks": ["minimax-m2.5", "ollama/qwen2.5:3b"],
        "reason": "Schnelle aktuelle Daten"
    },
    "creative": {
        "primary": "healer-alpha",
        "fallbacks": ["minimax-m2.5", "ollama/qwen2.5:3b"],
        "reason": "Beste Kreativität"
    },
    "analysis": {
        "primary": "healer-alpha",
        "fallbacks": ["minimax-m2.5", "ollama/qwen2.5:3b"],
        "reason": "Beste Analyse-Fähigkeiten"
    },
    "quick": {
        "primary": "minimax-m2.5",
        "fallbacks": ["hunter-alpha", "ollama/qwen2.5:3b"],
        "reason": "Kostenlos + schnell"
    },
    "long_context": {
        "primary": "gemini-flash",
        "fallbacks": ["minimax-m2.5", "ollama/qwen2.5:3b"],
        "reason": "1M Context!"
    },
    "safety_critical": {
        "primary": "healer-alpha",
        "fallbacks": ["minimax-m2.5", "ollama/qwen2.5:3b"],
        "reason": "Beste Security"
    }
}

# Alias Mapping
MODEL_ALIASES = {
    "hunter-alpha": "meta-llama/llama-3.3-70b-instruct",
    "healer-alpha": "anthropic/claude-3.5-sonnet", 
    "minimax-m2.5": "minimax/MiniMax-M2.5",
    "gemini-flash": "google/gemini-2.0-flash-001",
    "gpt-4o": "openai/gpt-4o",
    "ollama/qwen2.5:3b": "ollama/qwen2.5:3b",
}

def classify(text: str) -> str:
    """Classify message to task type"""
    text_lower = text.lower()
    
    scores = {}
    for task, keywords in TASK_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[task] = score
    
    if not scores:
        return "quick" if len(text) < 100 else "analysis"
    
    return max(scores, key=scores.get)

def get_model(text: str, budget_mode: bool = False) -> Dict:
    """Get optimized model for task"""
    task = classify(text)
    text_len = len(text)
    
    # Check for long context
    if text_len > 50000:
        task = "long_context"
    
    # Check for safety
    if any(kw in text.lower() for kw in TASK_KEYWORDS["safety_critical"]):
        task = "safety_critical"
    
    chain = MODEL_CHAINS.get(task, MODEL_CHAINS["analysis"])
    
    # Budget mode: prefer free models
    if budget_mode:
        primary = "minimax-m2.5" if task != "safety_critical" else "healer-alpha"
    else:
        primary = chain["primary"]
    
    return {
        "task": task,
        "primary": primary,
        "primary_full": MODEL_ALIASES.get(primary, primary),
        "fallbacks": chain["fallbacks"],
        "reason": chain["reason"],
        "context_needed": min(text_len * 1.5, 500000),
        "recommended_context": MODEL_CONTEXT.get(primary, 128000),
        "estimated_cost": MODEL_COSTS.get(primary, {"input": 0, "output": 0})
    }

def get_cost_estimate(text: str, model: str) -> float:
    """Estimate cost for a request"""
    tokens_approx = len(text) / 4  # rough estimate
    costs = MODEL_COSTS.get(model, {"input": 0, "output": 0})
    return (tokens_approx / 1_000_000) * costs["input"]

# CLI
if __name__ == "__main__":
    import sys
    
    args = sys.argv[1:]
    
    if not args:
        print("Usage: python message_router_v4.py <message> [--budget]")
        sys.exit(0)
    
    budget = "--budget" in args
    text = " ".join([a for a in args if a != "--budget"])
    
    result = get_model(text, budget_mode=budget)
    
    print(f"\n📊 Routing Result:")
    print(f"  Task: {result['task']}")
    print(f"  Model: {result['primary']}")
    print(f"  Full Name: {result['primary_full']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Fallbacks: {result['fallbacks']}")
    print(f"  Context: {result['recommended_context']:,}")
    print(f"  Est. Cost: ${result['estimated_cost']['input']:.4f}/1K tokens")
    print()
