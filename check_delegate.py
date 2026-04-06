#!/usr/bin/env python3
"""
Quick Delegation Check - Für schnelle Tasks
Nutzung: python3 check_delegate.py "Dein Task hier"
Return Codes:
    0 = delegieren (Confidence > 30%)
    1 = selber machen
"""
import sys

DELEGATE_KEYWORDS = [
    "research", "recherchiere", "suche", "analyse", "finden",
    "code", "python", "script", "entwickeln", "programmieren", "fix", "bauen", "erstelle", "erstellst",
    "blog", "post", "schreiben", "artikel", "content", "text",
    "twitter", "x.com", "social", "tiktok", "engagement",
    "sales", "outreach", "lead", "kunde", "email", "crawl",
    "backup", "monitoring", "alert", "server", "infrastruktur", "deployment",
    "dashboard", "ui", "frontend", "webseite", "website",
    "sicherheit", "security", "audit", "dsgvo"
]

SELF_KEYWORDS = [
    "hallo", "hi", "hey", "wie geht", "was machst", 
    "danke", "bitte", "ok", "ja", "nein",
    "stop", "stopp", "abbrechen",
    "erkläre", "was ist", "wer ist",
    "memory", "remember", "vergiss",
    "weiter", "machen", "was willst", "wie gehts"
]

def check_task(task):
    task_lower = task.lower()
    
    # Self first
    for kw in SELF_KEYWORDS:
        if kw in task_lower:
            return False, "SELF: Simple greeting/command"
    
    # Then check delegation
    for kw in DELEGATE_KEYWORDS:
        if kw in task_lower:
            return True, f"DELEGATE: Keyword '{kw}' found"
    
    # Long tasks = delegate
    words = len(task.split())
    chars = len(task)
    if words > 5 or chars > 80:
        return True, f"DELEGATE: Complex ({words} words, {chars} chars)"
    
    return False, f"SELF: No keyword match ({words} words, {chars} chars)"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: check_delegate.py 'Dein Task'")
        sys.exit(2)
    
    task = " ".join(sys.argv[1:])
    should_delegate, reason = check_task(task)
    
    print(f"{reason}")
    print(f"Result: {'DELEGATE' if should_delegate else 'SELF'}")
    
    sys.exit(0 if should_delegate else 1)
