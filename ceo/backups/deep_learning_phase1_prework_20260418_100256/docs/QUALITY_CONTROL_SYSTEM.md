# Quality Control System — Sir HazeClaw

**Letzte Aktualisierung:** 2026-04-17 12:10 UTC

## Überblick

Das Learning Loop System hat **5 Layer Quality Control** um sicherzustellen, dass nur qualitativ hochwertiger Code produziert wird:

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: Self-Evaluation (rule-based)                       │
│ → Bewertet Improvements vor Code-Generierung               │
│ → Score < 0.3 → SKIP (zu riskant)                          │
│ → Score 0.3-0.65 → REVISE (Korrektur nötig)                 │
│ → Score > 0.65 → PROCEED                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: Code Generation (LLM)                             │
│ → Generiert Python Code via MiniMax M2.7                    │
│ → Syntax Check nach Generierung                             │
│ → Fehler → wird nicht verwendet                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: LLM Code Evaluation                               │
│ → Bewertet den GENERIERTEN Code                            │
│ → Prüft auf: Vollständigkeit, Logik, Syntax               │
│ → Score < 0.3 → SKIP (Code质量问题)                        │
│ → Score 0.3-0.65 → REVISE (LLM empfiehlt Überarbeitung)     │
│ → Score > 0.65 → PROCEED                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 4: Validation Gate                                   │
│ → 3 Tests: Syntax, Error Reducer, Cron Health             │
│ → Mindestens 2/3 müssen passen                              │
│ → Error Delta muss < 0.1% sein                             │
│ → Cron Health darf nicht blockieren (wenn nicht cron-bezogen)│
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 5: Pattern Decay Engine                              │
│ → Veraltete Patterns werden entfernt                       │
│ → Confidence sinkt über Zeit                               │
│ → Zu niedrige Confidence → Pattern archiviert              │
└─────────────────────────────────────────────────────────────┘
```

## Quality Gates im Detail

### Layer 1: Self-Evaluation (rule-based)
**Datei:** `scripts/self_evaluator.py`

**Checks:**
- Syntax Check: Ist der Code syntaktisch korrekt?
- Logic Check: Offensichtliche Logik-Fehler?
- Impact Check: Addressiert das Issue wirklich?
- History Check: Hat ähnliches vorher funktioniert?
- Risk Check: Gefährliche Operationen?

**Schwellenwerte:**
```python
SELF_REWARD_THRESHOLD = 0.65  # Minimum to proceed
SELF_REWARD_CONFIDENCE = 0.45  # Skip if below this
```

### Layer 2: Code Generation
**Datei:** `scripts/code_generator.py`

**Prozess:**
1. Prompt an LLM mit Issue-Beschreibung
2. Generierter Code wird extrahiert
3. Syntax-Check mit `py_compile`
4. Bei Fehler → Code wird nicht verwendet

**Prompt (verbessert):**
```
Du bist ein Python-Programmierer. Erstell ein komplettes, ausführbares Python-Script:
- Das Script muss vollständig sein (keine unvollständigen Funktionen)
- Error handling mit try/except
- Hauptfunktion mit if __name__ == "__main__":
- python3 kompatibel
- Unter 500 Zeilen
```

### Layer 3: LLM Code Evaluation
**Datei:** `scripts/self_evaluator.py` → `evaluate_code()`

**Bewertungskriterien:**
- Korrigiert der Code das beschriebene Problem?
- Sind Logik und Syntax korrekt?
- Kann dieser Code das System verbessern?

**Output:**
```python
{
    'score': 0.0-1.0,
    'decision': 'PROCEED' | 'REVISE' | 'SKIP',
    'reasoning': 'Erklärung auf Deutsch'
}
```

### Layer 4: Validation Gate
**Datei:** `SCRIPTS/automation/learning_loop_v3.py` → `validation_gate()`

**Tests:**
1. **error_reducer_check**: Kritische Fehler?
2. **syntax_check**: Python Syntax valid?
3. **cron_health**: Cron Jobs gesund?

**Regeln:**
- 2/3 Tests müssen passieren
- Error Delta < 0.1%
- Cron Health nur blockierend wenn cron-bezogen

### Layer 5: Pattern Decay
**Datei:** `scripts/pattern_decay.py`

**Regeln:**
- Confidence sinkt jede Stunde leicht
- Bei 3+ aufeinanderfolgenden Fehlern → Pattern wird deprecated
- Confidence < 0.2 → Pattern wird archiviert

## Test Results

### Integration Test (3 Runs)
```
Run 1: Code ✅ | LLM 0.30 REVISE | Self 0.85
Run 2: Code ❌ | LLM — | Self 0.40 REVISE
Run 3: Code ✅ | LLM 0.35 REVISE | Self 0.85
```

### Erkenntnisse
1. **Code Generation**: Funktioniert, aber LLM generiert manchmal unvollständigen Code
2. **LLM Evaluation**: Fängt unvollständigen Code zuverlässig ab (REVISE)
3. **Self-Evaluation**: Fallback wenn Code Gen fehlschlägt
4. **Validation Gate**: Prüft finale Qualität

## Quality Flow bei einem Run

```
1. Issue detected: "Cron Watchdog timeout"
   ↓
2. Self-Evaluation: Score 0.85 → PROCEED
   ↓
3. Code Generation: Generiert Python Script
   ↓
4. Syntax Check: OK
   ↓
5. LLM Code Evaluation: Score 0.35 → REVISE
   "Code ist unvollständig"
   ↓
6. Improvement wird nicht für Validation freigegeben
   (oder muss überarbeitet werden)
```

## Offene Issues

1. **Unvollständiger Code**: LLM generiert manchmal Code der bei `def a` endet
   - Ursache: `max_tokens` zu niedrig oder API timeout
   - Lösung: Retry Logic + höherer max_tokens

2. **API Rate Limits**: Manchmal schlägt API Call fehl
   - Lösung: Exponential Backoff Retry

## Verbesserungen geplant

1. **max_tokens erhöhen** auf 5000+
2. **Retry Logic** mit exponential backoff
3. **Code Vollständigkeits-Check** bevor LLM Evaluation
4. **Hybrid Mode**: LLM + rule-based kombinieren

## Confidence

**Wir sind ~80% sicher dass das System funktioniert:**

✅ Layer 1-5 implementiert und testbar
✅ Quality Gates verhindern schlechten Code
⚠️ Unvollständiger Code manchmal (truncation)
⚠️ API reliability (manchmal timeouts)

**Nächste Schritte:**
1. max_tokens erhöhen
2. Retry Logic implementieren
3. Mehr Tests fahren
