# Phase 8: LLM Self-Reward Pattern

**Letzte Aktualisierung:** 2026-04-17 11:55 UTC

## Ziel
System soll eigene Outputs bewerten BEVOR Validation — mit echtem LLM statt rule-based.

## Zwei Optionen implementiert

### Option A: LLM für Ideen-Evaluation
- `evaluate_with_llm()` in `self_evaluator.py`
- Bewertet Improvement-Ideen (Titel + Beschreibung)
- **Problem:** LLM ist zu kritisch weil Ideen noch keine Details haben

### Option B: LLM für Code-Evaluation (AKTUELL)
- `code_generator.py` generiert tatsächlichen Python Code
- `evaluate_code()` in `self_evaluator.py` bewertet den Code
- **Funktioniert:** Code wird generiert, LLM evaluatiert

## Architecture

```
Learning Loop
    ↓
Phase 4: Improvement Selection
    ↓
Phase 4.5: Code Generation (NEU)
    ↓ 生成 Python Code mit LLM
Phase 5: Validation Gate
    ↓
LLM evaluate_code() prüft den Code
```

## Komponenten

| Script | Status | Funktion |
|--------|--------|----------|
| `scripts/code_generator.py` | ✅ | Generiert Python Code via LLM |
| `scripts/self_evaluator.py` | ✅ | `evaluate_with_llm()` + `evaluate_code()` |
| `learning_loop_v3.py` | ✅ | Phase 4.5 Integration |

## API Endpoint

MiniMax API (funktioniert):
```
https://api.minimax.io/anthropic/v1/messages
Model: MiniMax-M2.7
Format: Anthropic Messages API
```

## Problem: Unvollständiger Code

**Symptom:** LLM generiert Code der bei `def a` oder `get_summary()` endet.

**Ursache:** `max_tokens` zu niedrig (2500-4000)

**Lösung:** 
- Prompt verbessern: "Der Code muss vollständig sein"
- `max_tokens` erhöhen auf 5000+
- Oder: Kürzeren, fokussierteren Code generieren

## Test Results (5 Runs)

| Run | Code Gen | LLM Eval | Self-Eval | Score |
|-----|----------|----------|-----------|-------|
| 1 | ❌ Fail | — | 0.80 | 0.762 |
| 2 | ✅ | 0.40 REVISE | 0.30 | — |
| 3 | ✅ | 0.20 REVISE | 0.50 | — |
| 4 | ✅ | 0.40 REVISE | 0.00 | 0.762 |
| 5 | ❌ Fail | — | 0.75 | 0.762 |

**Erkenntnis:** 
- Code Generation ist erfolgreich wenn LLM vollständigen Code generiert
- LLM Evaluation fängt unvollständigen Code ab ( REVISE/SKIP)
- Manchmal schlägt API Call fehl (timeout, rate limit)

## Backups

- `phase8_llm_final_20260417_111115.tar.gz`
- `phase8_llm_self_reward_20260417_105032.tar.gz`

## Nächste Schritte

1. **max_tokens erhöhen** (5000+) für vollständigeren Code
2. **Retry Logic** hinzufügen wenn API Call fehlschlägt
3. **Hybrid Evaluation** — wenn LLM fails, fallback auf rule-based

## Usage

```bash
# Test code generator
python3 scripts/code_generator.py generate \
  --title "Fix Cron Watchdog timeout" \
  --description "Fix timeout error"

# Test self-evaluator with LLM
python3 scripts/self_evaluator.py evaluate \
  --improvement '{"title": "Fix timeout"}'
```
