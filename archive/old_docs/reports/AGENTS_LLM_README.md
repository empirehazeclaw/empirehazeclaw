# 🎯 LLM Routing für alle Agents

## Schnellstart

Jeder Agent kann ab jetzt den LLM Router nutzen:

```python
# In jedem Agent Script:
from llm_config import get_llm_response, quick_response, best_response, code_response

# Einfache Query
result = get_llm_response("Deine Frage", priority="speed")

# Convenience Functions
result = quick_response("Schnelle Frage")      # Speed priority
result = best_response("Komplexe Analyse")      # Quality priority  
result = cheap_response("Budget Query")         # Cost priority
result = code_response("Schreibe Python Code")  # Coding optimized
result = analysis_response("Analysiere dies")  # Reasoning optimized
```

## Priority Optionen

| Priority | Wann nutzen | Modelle |
|----------|-------------|--------|
| `speed` | Schnelle Antworten | Gemini 2.5 Flash |
| `quality` | Beste Qualität | Gemini 2.5 Pro, Claude |
| `cost` | Kosten sparen | Gemini 2.5 Flash (kostenlos) |
| `balanced` | Standard (default) | Mix |

## Features

- ✅ **Automatischer Fallback** - Wenn ein Model failt, probiert er das nächste
- ✅ **Caching** - Queries werden 1 Stunde gecached
- ✅ **Load Balancing** - 4 Strategien verfügbar
- ✅ **Analytics** - Usage Tracking

## Beispiel: Content Agent

```python
#!/usr/bin/env python3
from llm_config import get_llm_response, code_response

def write_blog(topic):
    prompt = f"Schreibe einen Blog Post über: {topic}"
    result = get_llm_response(prompt, priority="balanced")
    
    if result["success"]:
        print(result["response"])
        print(f"\n✅ Von: {result['model']}")
    else:
        print("❌ Fehler")

write_blog("KI für Restaurants")
```

## Beispiel: Sales Agent

```python
#!/usr/bin/env python3
from llm_config import get_llm_response

def qualify_lead(company):
    prompt = f"Qualifiziere diesen Lead: {company}"
    result = get_llm_response(prompt, priority="quality")
    return result["response"] if result["success"] else None

def write_outreach_email(company, name):
    prompt = f"Schreibe eine Outreach Email an {name} von {company}"
    result = get_llm_response(prompt, priority="balanced")
    return result["response"] if result["success"] else None
```

## Cache nutzen

```python
# Cache ist standardmäßig aktiviert
result = get_llm_response("Häufige Frage")  # wird gecached

# Cache deaktivieren wenn nötig
result = get_llm_response("Neue Analyse", use_cache=False)
```

## Analytics

```bash
# Usage Stats
python3 scripts/llm_analytics.py

# Cache Stats  
python3 scripts/llm_router.py --cache-stats

# HTML Dashboard
python3 scripts/llm_dashboard.html
```
