# OpenClaw University — Self-Improvement Loop Architecture
## Version 1.0 | 2026-04-08

---

## 🎯 Vision

Die OpenClaw University soll ein **selbstlernendes System** werden, das sich autonom verbessert:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SELF-IMPROVEMENT LOOP                            │
│                                                                     │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│   │  SCOUT   │───▶│ PROFESSOR│───▶│ EXAMINER │───▶│ ANALYSIS │   │
│   │(Research)│    │(Curriculum│   │ (Quiz)   │    │(Feedback)│   │
│   └──────────┘    └──────────┘    └──────────┘    └────┬─────┘   │
│         ▲                                              │         │
│         │            FEEDBACK LOOP                    │         │
│         └──────────────────────────────────────────────┘         │
│                                                                     │
│   [Nico macht Quiz] ──▶ Schwachstellen werden identifiziert       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Loop-Phasen (Detailliert)

### Phase 1: SCOUT (Research Agent)
**Aufgabe:** Neue Topics und Trends recherchieren

```
Scout Arbeitsablauf:
─────────────────────
1. Scanne Security-Feed (OWASP, CVE, Security Blogs)
2. Prüfe neue Angriffstechniken
3. Evaluiere Relevanz für OpenClaw University
4. Erstelle Topic-Vorschläge mit Priorität
5. Speichere in: /university/research/topics_pending.md
```

**Output:** `topics_pending.md` — Liste neuer Topics mit:
- Titel
- Relevanz-Score (1-10)
- Quellen
- Vorschlag (New Lesson / Update Existing / New Quiz)

---

### Phase 2: PROFESSOR (Curriculum Agent)
**Aufgabe:** Neue Lektionen erstellen oder bestehende aktualisieren

```
Professor Arbeitsablauf:
────────────────────────
1. Lese topics_pending.md
2. Prüfe bestehende Lessons auf Überlappung
3. Erstelle/aktualisiere Lesson-Dateien
4. Speichere in: /university/lessons/
5. Update curriculum_v1.md
6. Markiere Topic als "Lesson Created"
```

**Output:** Neue/aktualisierte Lesson-Files + curriculum_v1.md aktualisiert

---

### Phase 3: EXAMINER (Quiz Agent)
**Aufgabe:** Quizze für neue/aktualisierte Lektionen generieren

```
Examiner Arbeitsablauf:
────────────────────────
1. Prüfe neue Lessons seit letztem Loop
2. Generiere Quiz mit 5-10 Fragen pro Lesson
3. Erstelle auch Solutions-File
4. Speichere in: /university/quiz_module_X.md
5. Speichere Solutions in: /university/solutions_quiz_module_X.md
```

**Output:** `quiz_module_X.md` + `solutions_quiz_module_X.md`

---

### Phase 4: ANALYSIS (Data Manager)
**Aufgabe:** Quiz-Ergebnisse analysieren und Schwachstellen finden

```
Analysis Arbeitsablauf:
───────────────────────
1. Lese Quiz-Results von Nico
   → /university/results/quiz_results.json
2. Berechne Score pro Topic/Modul
3. Identifiziere Schwachstellen (Score < 70%)
4. Erstelle Feedback-Report
5. Loop zurück zu Scout mit priorisierten Topics
```

**Output:** `results/analysis_report.md` mit:
- Modul-Scores
- Schwachstellen (Topics mit niedrigem Score)
- Priorisierte Verbesserungsvorschläge

---

## 📊 Datenfluss & Storage

### File-Struktur
```
university/
├── SELF_IMPROVEMENT_PLAN.md      # Dieses Dokument
├── research/
│   ├── topics_pending.md         # Neue Topic-Vorschläge
│   └── topics_completed.md       # Bereits bearbeitete Topics
├── lessons/                      # Alle Lektionen
├── quiz_module_X.md              # Quizze
├── solutions_quiz_module_X.md    # Lösungen
├── results/
│   ├── quiz_results.json         # Nicis Quiz-Ergebnisse
│   └── analysis_report.md        # Analyse-Report
├── curriculum_v1.md              # Curriculum (auto-updated)
└── loop_state.json               # Aktueller Loop-Status
```

### Quiz Results Format (quiz_results.json)
```json
{
  "date": "2026-04-08T14:30:00Z",
  "quiz_module": 3,
  "score": 75,
  "weak_areas": [
    "Tool-Input-Validation Patterns",
    "Sanitization Edge Cases"
  ],
  "time_spent_minutes": 45,
  "notes": "Brauche mehr Beispiele für Edge Cases"
}
```

---

## ⏰ Cron-Job Definition

### Loop-Trigger

| Trigger | Zeit | Was passiert |
|---------|------|--------------|
| **Weekly Loop** | Sonntag 18:00 UTC | Vollständiger Loop (Scout → Professor → Examiner) |
| **Quiz-Trigger** | Nach jedem Quiz | Analysis Phase → Feedback an Scout |
| **Manual Trigger** | Auf Anfrage | CEO startet Loop manuell |

### Cron-Job IDs (für openclaw cron)

```bash
# Wöchentlicher Self-Improvement Loop
openclaw cron create \
  --id "university_weekly_loop" \
  --schedule "0 18 * * 0" \
  --agent "ceo" \
  --prompt "Starte University Self-Improvement Loop"

# Nach-Quiz-Analyse Trigger (wenn quiz_results.json updated wird)
openclaw cron create \
  --id "university_quiz_analysis" \
  --schedule "*/30 * * * *" \
  --agent "ceo" \
  --prompt "Prüfe ob neue Quiz-Ergebnisse vorliegen"
```

---

## 🔗 Agent-Koordinations-Plan

### Kommunikationsweg

```
┌─────────────────────────────────────────────────────────────┐
│                         CEO                                 │
│              (Orchestriert den Loop)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
          sessions_send an jeweiligen Agent
                      │
        ┌─────────────┼─────────────┬─────────────┐
        ▼             ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌─────────┐
   │  SCOUT  │  │ PROFESSOR│  │ EXAMINER  │  │  DATA   │
   │(Research│  │(Curricul.)│  │  (Quiz)   │  │(Analysis│
   └────┬────┘  └────┬─────┘  └─────┬─────┘  └────┬────┘
        │            │              │              │
        └────────────┴──────────────┴──────────────┘
                       │
                       ▼
              Reports zurück an CEO
                       │
                       ▼
              CEO informiert Nico
```

### Session-Keys für Agenten
```javascript
agent:research:telegram:direct:5392634979   // Scout
agent:curriculum:telegram:direct:5392634979 // Professor  
agent:examiner:telegram:direct:5392634979   // Examiner
agent:data:telegram:direct:5392634979       // Data Manager
```

### Koordinations-JSON (loop_state.json)
```json
{
  "current_phase": "SCOUT",
  "loop_number": 1,
  "started_at": "2026-04-08T18:00:00Z",
  "scout_status": "in_progress",
  "professor_status": "pending",
  "examiner_status": "pending",
  "analysis_status": "pending",
  "next_action": "Run Scout to find new topics"
}
```

---

## 🔙 Feedback-Loop Design

### Der kritische Feedback-Pfad

```
Quiz-Ergebnis (Nico)
        │
        ▼
Data Manager analysiert
        │
        ▼
Schwachstellen gefunden? ──NO───▶ Loop pausiert
        │
       YES
        │
        ▼
Priorisierte Topics erstellen
        │
        ▼
Scout erforscht Schwachstellen-Bereich
        │
        ▼
Professor erstellt verbesserte Lesson
        │
        ▼
Examiner generiert neues Quiz
        │
        ▼
Nico macht Quiz erneut
        │
        ▼
[Neue Analyse]
```

### Feedback-Gewichtung

| Nico's Quiz-Score | Aktion |
|-------------------|--------|
| **< 50%** | Hohe Priorität: Lesson komplett überarbeiten |
| **50-70%** | Mittlere Priorität: Additional Exercises hinzufügen |
| **70-85%** | Geringe Priorität: Nur Quiz aktualisieren |
| **> 85%** | Keine Aktion nötig, Topic gilt als "Mastered" |

---

## 📋 Beantwortung der Fragen

### 1. Wie oft soll der Loop laufen?
**Antwort:** Wöchentlich (Sonntag 18:00 UTC) + nach jedem Quiz

**Begründung:**
- Wochenrythmus gibt genug Zeit für neue Content-Entwicklung
- Quiz-Trigger ermöglicht schnelles Feedback bei Problemen
- Nicht zu aggressiv (kein täglicher Loop nötig)

---

### 2. Trigger? Cron-basiert oder nach Quiz-Ergebnis?
**Antwort:** Beides — Hybrid-Ansatz

```
Cron-Job (Sonntag 18:00 UTC)
    │
    └──▶ Weekly Full Loop

ODER

Nico macht Quiz
    │
    └──▶ Data Manager analysiert sofort
              │
              └──▶ Bei Schwachstellen: Scout wird getriggert
```

---

### 3. Scope? Nur Cybersecurity oder auch andere Topics?
**Antwort:** Aktuell Cybersecurity, aber Architektur ist **erweiterbar**

```
university/
├── cybersecurity/      # Aktuell: Security Track
├── programming/        # Zukunft: Programming Topics
├── devops/             # Zukunft: DevOps & Infrastructure
└── ai_ml/              # Zukunft: AI/ML Fundamentals
```

**Nico entscheidet:** Scope bleibt vorerst bei Cybersecurity.

---

### 4. Wo werden Quiz-Results gespeichert?
**Antwort:** `/university/results/quiz_results.json`

**Format:**
```json
{
  "date": "ISO-8601",
  "quiz_module": "number",
  "score": "percentage",
  "weak_areas": ["array of topic names"],
  "time_spent_minutes": "number",
  "notes": "optional user feedback"
}
```

---

### 5. Wie weiß Professor was Scout gefunden hat?
**Antwort:** Via `topics_pending.md` + `loop_state.json`

```
Scout schreibt → topics_pending.md
                      │
                      ▼
Professor liest → topics_pending.md
                      │
                      ▼
Professor markiert in loop_state.json: "professor_status": "done"
```

**Keine direkte Kommunikation nötig** — Dateien als Kommunikationsmedium.

---

## 🚦 Implementierungs-Status

| Komponente | Status | Notizen |
|------------|--------|---------|
| Architektur-Dokument | ✅ DONE | Dieses Dokument |
| File-Struktur | ✅ DONE | Existiert bereits |
| research/ Ordner | ⏳ OFFEN | Muss erstellt werden |
| results/ Ordner | ⏳ OFFEN | Muss erstellt werden |
| loop_state.json | ⏳ OFFEN | Muss erstellt werden |
| Scout Agent | ⏳ OFFEN | Sessions-Skill fehlt |
| Professor Agent | ⏳ OFFEN | Sessions-Skill fehlt |
| Examiner Agent | ⏳ OFFEN | Sessions-Skill fehlt |
| Data Manager Skill | ⏳ OFFEN | Analysis-Skill fehlt |
| Cron-Jobs | ⏳ OFFEN | CEO muss Cron definieren |

---

## 🎯 Nächste Schritte (für CEO)

1. **Ordner erstellen:**
   - `/university/research/`
   - `/university/results/`

2. **Loop-State initialisieren:**
   - `/university/loop_state.json` erstellen

3. **Agent-Sessions aktivieren:**
   - Scout, Professor, Examiner als reale Agenten einrichten
   - Oder: CEO übernimmt alle Rollen vorerst

4. **Cron-Jobs definieren:**
   - Weekly Loop (Sonntag 18:00 UTC)
   - Quiz-Analysis Watcher

5. **Ersten Loop testen:**
   - CEO startet manuell
   - Ergebnis an Nico rapportieren

---

## 📝 Changelog

| Datum | Änderung |
|-------|----------|
| 2026-04-08 | Initial erstellt (v1.0) |

---

*Architektur entwickelt für OpenClaw University Self-Improvement System*
*Verantwortlich: CEO Agent | CEO v2*
