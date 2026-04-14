# MEMORY.md — Sir HazeClaw Core Memory

**Letzte Aktualisierung:** 2026-04-14 16:58 UTC
**Struktur:** Memory Blocks (nicht flach)

---

## 🧱 CORE MEMORY BLOCKS

### 🔵 USER PROFILE
```
Label: Nico — Primary User
Key Facts:
- Name: Nico | Telegram: 5392634979 | Sprache: Deutsch
- Background: KFZ Mechatroniker → Ingenieur Werkstoffkunde
- Started: Ende Februar 2026
- Communication: Direkt, kurz, Ergebnis-fokussiert
- NICHT: "Master", kein "habe ich gemacht" ohne Output
- WICHTIG: "hast du das wirklich gelernt" → dokumentieren!
```

### 🔵 SYSTEM CONFIG
```
Label: System Configuration
Key Facts:
- Gateway: OpenClaw 2026.4.12 | Port 18789
- Model: MiniMax M2.7
- Workspace: /home/clawbot/.openclaw/workspace/ceo/
- Scripts: 55 active in /workspace/scripts/
- Crons: 51 total (27 enabled)
- KG: ~360 entities, ~520 relations
- Node.js: v22.22.2
```

### 🔴 ACTIVE ISSUES
```
Label: Known Issues — Last Updated 2026-04-14
Cron Errors (7):
- KG Access Updater: Timeout (2x consecutive)
- REM Feedback Integration: Telegram @heartbeat not found (2x)
- GitHub Backup: Timeout
- Token Budget Tracker: Timeout
- CEO Weekly Review: Message failed
- Opportunity Scanner: Message failed
- Cron Watchdog: Timeout

Other:
- 65 Lost Tasks (orphans from Cron Error Healer — cannot cancel)
- Opportunity Scanner script works, cron delivery fails

Resolved This Session:
- Voice Note False Trigger: TOOLS.md korrigiert
- Over-active inference: SOUL.md "Assume no input" Regel
- Proactive code commit: AGENTS.md "NEVER without explicit approval"
```

### 🟡 RECENT LEARNINGS
```
Label: Key Learnings — Last Updated 2026-04-14
This Session:
- Voice Notes: Transcribe ONLY when audio file received, not proactive
- Inference: "I think" / "I assume" / "I noticed" without evidence = STOP
- Proaktiv: Commit/push/extern senden = BRAUCHT explizite Erlaubnis
- Guardrails: Pre/Post LLM checks in /workspace/skills/guardrails/

Earlier:
- Cron Error: Meist Timeout → Scripts brauchen Optimierung oder timeoutSeconds erhöhen
- MiniMax Overload (HTTP 529): Normal, nicht Config-Problem
- DB Size 371MB: Normal (embedding_cache dominiert)
```

### 🟢 WORKSPACE RULES
```
Label: Workspace Operational Rules
Trigger-Regel (CRITICAL):
- Jede Aktion braucht ECHTEN Auslöser: File, Message, Cron-Run, Explicit Request
- Keine Aktion auf "vielleicht", "probably", "ich denke"
- Wenn unsicher → FRAGEN, nicht HANDELN

Anti-Halluzination Check (vor jeder Aktion):
1. Habe ich einen ECHTEN Auslöser gesehen? (nicht angenommen)
2. Ist der Auslöser in diesem Context dokumentiert?
3. Falls unsicher → Aktion gestoppt, nachgefragt

Externe Aktionen (IMMER erst fragen):
- Commit/Push Code
- Nachrichten senden
- Externe Systeme ändern
- E-Mails / Tweets / Public Posts
```

---

## 📊 RECALL MEMORY INDEX

| Frage | Lese aus |
|-------|----------|
| Fakten über Nico | `memory/long_term/facts.md` |
| Nico's Preferences | `memory/long_term/preferences.md` |
| Erkannte Patterns | `memory/long_term/patterns.md` |
| Was heute passiert | `memory/2026-04-14.md` |
| Was gestern war | `memory/2026-04-13.md` |
| KG Info | `memory/kg/` |
| Skills | `memory/procedural/skills.md` |
| Workflows | `memory/procedural/workflows.md` |

---

## ⚠️ TRUST-BUT-VERIFY

**HEARTBEAT.md zeigt NUR echte letzte-Run-States.**
Wenn Cron nicht aktuell → `?` statt ✅.

**MEMORY.md zeigt NUR verifizierte Fakten.**
Wenn unsicher → `memory_search` nutzen oder nachfragen.

---

*MEMORY.md = Core Memory Block. Strukturierte Facts, keine Romane.*
*Flüchtige Details → daily notes. Langfristiges → long_term/*.md*
