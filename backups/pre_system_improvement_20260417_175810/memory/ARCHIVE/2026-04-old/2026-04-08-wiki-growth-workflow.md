# Wiki Growth Workflow — Automatische Wiki-Pflege

**Erstellt:** 2026-04-08 20:10 UTC
**Status:** ✅ AKTIV
**Kategorie:** System / Memory / Workflow

---

## 🎯 Das Problem

Die Wiki-Infrastruktur existiert (Cron-Jobs, Scripts, Ordner), aber:
- evening_capture.py erstellt nur leere Templates
- Niemand füllt sie aus
- Das Wiki wächst nicht automatisch

**Ergebnis:** 2 Tage Stillstand (7.-8. April)

---

## ✅ Die Lösung: Zwei-Wege-Automatisierung

### Weg 1: Nach jeder Session → Note erstellen

```
WANN: Nach jeder delegierten Task ODER nach einer längeren Arbeits-Session
WER: Der Agent der gerade gearbeitet hat
WAS:
  1. Erstelle Note in notes/permanent/ oder notes/fleeting/
  2. Format: YYYY-MM-DD-{topic}.md
  3. Inhalt: Was wurde gemacht, Learnings, Nächste Schritte
  4. Wiki-index.md updaten
  5. Wiki-log.md appenden
```

### Weg 2: Tägliches Auto-Capture (verbessert)

```
WANN: 21:00 UTC (evening_capture.py)
WAS:
  - Session-Transcripts der letzten 24h analysieren
  - Key-Takeaways extrahieren
  - Automatisch fleeting Note erstellen MIT Inhalt
  - NICHT nur leere Templates
```

---

## 🔄 Wer macht was?

| Agent | Verantwortung | Wann |
|-------|---------------|------|
| CEO ([SYSTEM-ORCHESTRATOR]) | Koordiniert, prüft, erstellt Daily Notes | Nach jeder [USER]-Session |
| Builder | Notes zu Code/Builds | Nach jedem Build |
| Security Officer | Notes zu Security/Audits | Nach jedem Audit |
| Data Manager | Notes zu Data/DB/Index | Nach jeder Data-Task |
| Research | Notes zu Research-Themes | Nach jeder Recherche |
| QC Officer | Notes zu Quality/Testing | Nach jedem QC-Check |

---

## 📝 Notiz-Template (Standard)

```markdown
# {Datum} — {Was wurde gemacht}

**Agent:** {Agent-Name}
**Kategorie:** {Category}
**Session:** {mit wem, wenn relevant}

---

## 🎯 Task
> Was war die Aufgabe?

## ✅ Ergebnis
> Was wurde erreicht?

## 💡 Learnings
> - Learning 1
> - Learning 2

## 🔜 Next Steps
> Was kommt als nächstes?

## 📂 Files Created/Modified
- file1.md
- file2.js

---

*Erstellt: {YYYY-MM-DD HH:MM} UTC*
```

---

## 🚀 Implementation

### Für Agent SOUL.md hinzufügen:

```markdown
## 📝 Wiki-Pflege (NEU)
Nach jeder Task:
1. Erstelle Note in /workspace/memory/notes/{category}/
2. Update wiki-index.md (neue Page hinzufügen)
3. Update wiki-log.md (## [DATE] ingest | Description)
4. Sende Report an CEO mit Note-Pfad
```

### Cron-Trigger (optional):

```
# Täglich um 21:30 - Auto-Capture von Today's Learnings
30 21 * * * /home/clawbot/.openclaw/workspace/scripts/auto_session_capture.py
```

---

## 📊 Erfolg-Metriken

| Metrik | Ziel |
|--------|------|
| Notes pro Tag | ≥3 |
| Wiki-index Pages | Wachsend |
| Knowledge Graph Entities | Wachsend |
| wiki-log Einträge | Jeder Tag dokumentiert |

---

## 🔧 Auto-Capture Script (TODO)

Ein Script das:
1. Die letzten 24h Session-Transcripts liest
2. Key-Takeaways extrahiert (per LLM)
3. Automatisch fleeting Note erstellt MIT Inhalt

**Status:** ❌ Noch nicht implementiert
**Owner:** Builder (via CEO Delegation)

---

*Zuletzt aktualisiert: 2026-04-08 20:10 UTC*
