# 🚀 Self-Reflection Engine — Phase 5 Implementation Plan

**Erstellt:** 2026-04-17 09:40 UTC  
**Status:** 🔴 PRIORITÄT — basiert auf NeurIPS 2025 + Yohei Nakajima Research  
**Erwartete Impact:** 🟢 HOCH — Plateau brechen, Learning Loop Score 0.76 → 0.80+

---

## 📋 EXECUTIVE SUMMARY

Aktuelles Problem:
- Learning Loop Plateau bei 0.763 — keine Verbesserung mehr
- System lernt nicht aus eigenen Fehlern
- Nur externe Feedback-Signale werden genutzt

Lösung:
- **Self-Reflection Engine** nach RISE/Reflexion Pattern (NeurIPS 2024/2025)
- System soll eigene Fehler analysieren, natürliche Sprach-Kritik schreiben
- Diese "Reflection" fließt in nächsten Learning Loop ein

---

## 🔬 RESEARCH SUMMARY (NeurIPS 2024/2025 + Yohei Nakajima)

### 1. Reflexion Pattern (Shinn et al., 2023)
```
Agent löst Task → Task failed → natürliche Sprach-Kritik schreiben → 
Reflexion speichern → nächsten Versuch mit Feedback
```
- **Pros:** Kein weight update, billig, für jedes LLM
- **Cons:** Ephemer wenn nicht persistiert, kann schlechte Reflexionen verstärken
- **Result:** HumanEval pass@1 von ~66% → ~91%

### 2. RISE — Recursive Introspection (Qu et al., 2024)
```
Fine-tune auf multi-turn traces: falsche Antwort → Feedback → korrigierte Antwort
```
- Nach Training: Model kann Introspection intern simulieren
- Verbessert Multi-Step Math Reasoning ohne explizites scaffolding

### 3. STaR — Self-Taught Reasoner (Zelikman et al., 2022)
```
Solutions generieren → korrekte filtern → auf Reasoning-Pfade fine-tunen
```
- Kleine Models werden starke Reasoner — durch eigene generierte Proofs

### 4. Self-Refine (Madaan et al., 2023)
```
Generate → Critique → Revise → repeat until convergence
```
- Für Text und Code, verbessert Quality über single-shot

---

## 📊 DESIGN FÜR SIR HAZECLAW

### Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                    SELF-REFLECTION ENGINE                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐  │
│  │ Task Failed │───▶│  Reflect()  │───▶│ Critique Store │  │
│  └─────────────┘    │              │    └────────────────┘  │
│                     │  "Was habe   │           │            │
│                     │   ich falsch │           ▼            │
│                     │   gemacht?"  │    ┌────────────────┐  │
│                     └──────────────┘───▶│ Next Attempt   │  │
│                                         │ with Critique  │  │
│                                         └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **Reflection Generator**
   - Input: Fehlgeschlagener Task + Context + Result
   - Output: Natürliche Sprach-Kritik (was lief schief, warum, was anders machen)
   - Wird nach Failure-Reaction ausgeführt

2. **Critique Store** (persistent)
   - Speichert alle Reflections mit:
     - Timestamp
     - Task Type
     - Fehler-Kategorie
     - Korrigierte Action
     - Confidence Score

3. **Critique Retrieval** (bei neuem Task)
   - Suche nach ähnlichen vergangenen Fehlern
   - Hole relevante Reflections als Kontext
   - Füge hinzu zu Task-Prompt

### Implementation Phasen

```
Phase 1: Reflection Generator (Core)
Phase 2: Critique Store + Persistence
Phase 3: Critique Retrieval Integration
Phase 4: Learning Loop Integration
Phase 5: Self-Reward + Self-Evaluation
```

---

## 📋 IMPLEMENTATION DETAIL

### Phase 1: Reflection Generator

```python
# reflection_engine.py — NEW Script

class ReflectionEngine:
    """
    Generates natural-language self-critique after task failures.
    
    Based on Reflexion (Shinn et al., 2023) + RISE (Qu et al., 2024):
    - When task fails → generate critique
    - Store critique for future retrieval
    - Use as context for next similar task
    """
    
    def __init__(self):
        self.store = ReflectionStore()
        self.max_reflections = 100
    
    def reflect(self, task: dict, result: dict, context: dict) -> str:
        """
        Generate self-critique for a failed task.
        
        Args:
            task: The failed task details
            result: What happened (error, wrong output, etc.)
            context: Additional context (session, time, etc.)
        
        Returns:
            Natural language critique string
        """
        prompt = self._build_reflection_prompt(task, result, context)
        critique = self._generate_critique(prompt)
        self.store.add(critique, task, result)
        return critique
    
    def _build_reflection_prompt(self, task, result, context) -> str:
        """Build prompt for LLM reflection generation."""
        return f"""
Du bist ein selbst-reflektierendes System. Analysiere den fehlgeschlagenen Task.

FEHLGESCHLAGENER TASK:
- Type: {task.get('type', 'unknown')}
- Description: {task.get('description', 'N/A')}
- Expected: {task.get('expected', 'N/A')}

FEHLER RESULTAT:
- Error: {result.get('error', 'N/A')}
- Output: {result.get('output', 'N/A')[:200] if result.get('output') else 'N/A'}
- Why it failed: {result.get('reason', 'N/A')}

KONTEXT:
- Session: {context.get('session', 'N/A')}
- Time: {context.get('time', 'N/A')}

AUFGABE:
Schreibe eine präzise Selbstkritik (3-5 Sätze):
1. Was ist konkret schief gelaufen?
2. Warum ist es schief gelaufen?
3. Was hätte ich anders machen sollen?
4. Wie kann ich es nächstes Mal besser machen?

Format: Natürliche Sprache, keine Bullet Points im Text.
"""
    
    def _generate_critique(self, prompt: str) -> str:
        """Call LLM to generate critique."""
        # Use MiniMax or fallback to rule-based
        # Implementation depends on API availability
        pass
```

### Phase 2: Critique Store

```python
class ReflectionStore:
    """
    Persistent storage for self-reflections.
    
    Based on NeurIPS 2025 best practices:
    - Store full context (task + result + critique)
    - Tag by category for fast retrieval
    - Time-decay for old reflections
    """
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.reflections = self._load()
    
    def add(self, critique: str, task: dict, result: dict):
        """Add a new reflection to the store."""
        entry = {
            'id': f'reflect_{int(time.time() * 1000)}',
            'timestamp': datetime.now().isoformat(),
            'critique': critique,
            'task_type': task.get('type', 'unknown'),
            'task_description': task.get('description', '')[:100],
            'error_type': result.get('error_type', 'unknown'),
            'resolved': False,
            'use_count': 0,
        }
        self.reflections.append(entry)
        self._prune()
        self._save()
    
    def get_relevant(self, task_type: str, error_type: str = None, limit: int = 3) -> list:
        """
        Retrieve relevant past reflections for a task type.
        
        Uses semantic similarity when KG embeddings available.
        Falls back to exact type matching.
        """
        candidates = [r for r in self.reflections 
                      if r['task_type'] == task_type and not r.get('resolved')]
        
        if error_type:
            candidates = [r for r in candidates if r.get('error_type') == error_type]
        
        candidates.sort(key=lambda x: (x['use_count'], x['timestamp']), reverse=True)
        return candidates[:limit]
```

### Phase 3: Learning Loop Integration

```python
# Integration in learning_loop_v3.py

def run_learning_cycle():
    """Modified learning cycle with self-reflection."""
    # ... existing code ...
    
    # After validation fails → trigger reflection
    if validation_failed:
        reflection = reflection_engine.reflect(task, result, context)
        print(f"🔍 Self-Reflection: {reflection[:100]}...")
        
        # Add to next attempt context
        relevant_reflections = store.get_relevant(task['type'])
        for ref in relevant_reflections:
            context['past_reflections'].append(ref)
```

---

## 🎯 EXPECTED OUTCOMES

| Metric | Current | Expected |
|--------|---------|----------|
| Learning Loop Score | 0.763 | 0.80+ |
| Plateau Status | Stuck at 0.76 | Broken (exploration > exploitation) |
| Self-Correction | None | Built-in via Reflection |
| Reflection Reuse | N/A | 3-5 relevant per Task Type |

---

## ⚠️ RISKS & MITIGATIONS

| Risk | Severity | Mitigation |
|------|----------|------------|
| LLM hallucinating reflections | MEDIUM | Validate against actual error logs |
| Storage bloat | LOW | Prune after 100 reflections |
| Reflection loops | MEDIUM | Max 1 reflection per task attempt |
| Poor quality critique | MEDIUM | Human-in-loop for first 10, then auto |

---

## 📊 METRICS TO TRACK

- `reflection_count`: Number of reflections generated
- `reflection_reuse_rate`: How often reflections are retrieved and used
- `reflection_quality`: Score from human evaluation (first 10)
- `learning_loop_score_delta`: Change in score after reflection integration
- `plateau_broken`: Boolean — did we break 0.77?

---

## 📋 PHASE 5 ROADMAP (basierend auf Research)

| Phase | Task | Priority | Status |
|-------|------|----------|--------|
| **5.1** | Reflection Generator Script | P1 | ✅ DONE |
| **5.2** | Critique Store (JSON persistence) | P1 | ✅ DONE |
| **5.3** | KG Integration (store in KG) | P2 | ✅ DONE |
| **5.4** | Learning Loop Integration | P2 | ✅ DONE |
| **5.5** | Thompson Sampling + Contextual Features | P2 | ✅ DONE |
| **5.6** | Self-Reward Pattern | P3 | TODO |

---

## 🔗 REFERENCES

- Reflexion (Shinn et al., 2023): Verbal RL → +25% on HumanEval
- RISE (Qu et al., 2024): Multi-turn traces for self-correction
- Self-Refine (Madaan et al., 2023): Generate → Critique → Revise
- STaR (Zelikman et al., 2022): Self-generated reasoning traces
- Yohei Nakajima Survey (2025): Better Ways to Build Self-Improving AI Agents

---

_Letzte Aktualisierung: 2026-04-17 09:40 UTC_
_Sir HazeClaw — Phase 5 Implementation Plan_
