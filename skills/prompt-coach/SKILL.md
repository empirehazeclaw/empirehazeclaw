# Prompt Coach — SKILL.md

## Purpose
**Always-on Prompt Co-Pilot** — intercepts every message from Nico, optimizes it with context, asks clarifying questions when needed, then hands off to CEO for execution. Also monitors execution feedback.

## How It Works

```
Nico → [OpenClaw Session Routing] → Prompt Coach Session
                                        ↓
                              [Analyze + Enhance]
                                        ↓
                        ┌───────────────┴───────────────┐
                        ↓                               ↓
                   Clear enough?                  Unclear/Ambiguous?
                        ↓                               ↓
            [Optimize + Send to CEO]          [Ask clarifying questions]
                        ↓                               ↓
                  CEO executes                   Nico answers
                        ↓                               ↓
               Prompt Coach monitors          [Loop until clear]
                        ↓                               ↓
                   CEO result to Nico         [Then optimize + execute]
```

## Features

### 1. Input Analysis
- Extracts intent from Nico's message
- Loads relevant context from MEMORY.md, KG, recent sessions
- Identifies ambiguity / missing information

### 2. Clarifying Questions
- When intent is unclear → ask specific questions
- When context is missing → request it
- When tone/mode is ambiguous → confirm approach

### 3. Prompt Optimization
- Enhance prompt with context
- Adjust tone (technical/casual/detailed)
- Add relevant constraints/deadlines
- Format for CEO execution

### 4. Execution Monitoring
- Track CEO's execution
- Validate output quality
- Ask Nico if results meet expectations
- Loop for refinements if needed

## Session Structure

- **Prompt Coach session**: `session:prompt-coach` (persistent)
- **Transfer to CEO**: After coaching complete, spawn CEO with optimized prompt
- **Feedback loop**: CEO result comes back to Prompt Coach for evaluation

## Routing Configuration

In OpenClaw, configure session routing so ALL Nico messages go to prompt-coach first:
```json
{
  "routes": {
    "prompt-coach": {
      "match": "sender:5392634979",
      "handler": "prompt-coach"
    }
  }
}
```

## Example Flow

**Nico:** "mach was mit dem zeug"

**Prompt Coach:** 
```
 🤔 Verstehe ich richtig?
 
 A) Thema aus gestern (Session-Analyse)?
 B) Neue Aufgabe?
 C) Etwas aus unserem Chat-Verlauf?
 
 Bitte wähle A, B oder C.
```

**Nico:** "B"

**Prompt Coach:**
```
 🆕 Neue Aufgabe — bitte beschreibe:
 
 1. Was genau soll passieren?
 2. Gibt es Deadline oder Priorität?
 3. Technischer Kontext vorhanden (Dateien, Systeme)?
```

**Nico:** "server monitoring dashboard bauen mit grafana"

**Prompt Coach:**
```
 ✅ Prompt optimiert:
 
 "Erstelle ein Server-Monitoring-Dashboard mit Grafana.
  Features: CPU, RAM, Disk, Network, Alerts.
  Systeme: srv1432586 (187.124.11.27).
  Output: Konfiguration + Anleitung."
 
 → Starte CEO...
```

**CEO:** [executes, returns result]

**Prompt Coach:** [monitors + evaluates]
```
 📊 CEO hat ausgeführt:
 - Dashboard config erstellt ✅
 - Grafana provisioning script ✅
 
 ⭐ Ergebnis gut?
 
 [ ] Ja, passt so
 [ ] Anpassung needed — was ändern?
 [ ] Detailierter bitte
```

## Quality Gates

Prompt Coach fragt NIEMALS einfach nur "ist das gut?". Stellt spezifische Fragen:
- "Soll das Dashboard Auto-Refresh haben?"
- "Welche Alert-Thresholds?"
- "Nur Linux-Server oder Windows auch?"

## Configuration

- `context_lookback_days`: 7 (how far back to search MEMORY/kg for context)
- `clarification_threshold`: 0.6 (0-1, how ambiguous before asking questions)
- `monitoring_enabled`: true

## Files
- `index.js` — main skill logic
- `context_loader.js` — loads MEMORY.md, KG, session history
- `question_engine.js` — generates clarifying questions
- `prompt_optimizer.js` — enhances prompts

## Status
- Created: 2026-04-12
- Status: ACTIVE — running as always-on layer
- Next: Configure OpenClaw session routing