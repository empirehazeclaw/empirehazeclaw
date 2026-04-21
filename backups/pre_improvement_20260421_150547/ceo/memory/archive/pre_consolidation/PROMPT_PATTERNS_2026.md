# AI Agent Prompt Engineering Patterns (2026)

*Researched: 2026-04-10*

## Die 10 Patterns für AI Agent Prompts

### Pattern 1: Role + Constraints
Definiere WER der Agent ist UND was er NICHT darf.

**Beispiel:**
```
Du bist Sir HazeClaw, ein autonomer AI Agent.
Deine Constraints:
- Du fragst beim Master nach BEVOR du löschst
- Du informierst proaktiv bei Problemen
- Du dokumentierst alle Änderungen
```

### Pattern 2: Chain of Verification
Agent soll Output VOR dem Ausführen verifizieren.

### Pattern 3: Structured Output
 JSON oder strukturierte Formate für klare Kommunikation.

### Pattern 4: Error Recovery
Explizit definieren was bei Fehlern passiert.

### Pattern 5: Guard Rails
Sicherheitsgrenzen definieren - was darf der Agent NICHT tun.

### Pattern 6: Tool Constraints
Explizit welche Tools der Agent nutzen darf.

### Pattern 7: Handoff Protocol
Wie der Agent eskaliert oder weitergibt.

### Pattern 8: State Management
Wie der Agent State über längere Sessions behält.

### Pattern 9: Reflection Loop
Der Agent soll eigene Entscheidungen reflektieren.

### Pattern 10: Memory Strategy
Wie der Agent irrelevante Info verwirft.

---

## Warum Agent Prompts anders sind:

1. **Persistence** - Läuft über viele LLM Calls
2. **Tool Use** - Produziert Aktionen, nicht nur Text
3. **Multi-step Reasoning** - Plant, führt aus, beobachtet, passt an

---

## Anti-Patterns zu vermeiden:

- Nur Rolle definieren ohne Constraints
- Keine Error-States definieren
- Ambiguous Instructions die sich über Zeit verstärken
