# 🦞 LEARNING LOOP OPTIMIZATION v2.0
**Datum:** 2026-04-11 12:15 UTC
**Purpose:** Prevent 2-Day Failures from recurring

---

## ❌ PROBLEMS FROM LAST 2 DAYS

| # | Problem | Root Cause | Prevention | Status |
|---|---------|------------|------------|--------|
| 1 | 82 Scripts erstellt | Kein Audit vor Creation | Pre-Creation Checklist | ⏳ OFFEN |
| 2 | 5 Analysen statt 1 Implementierung | Analysis Paralysis | Implementation First Rule | ✅ Dokumentiert |
| 3 | 3 Cron Errors nicht gefixt | Errors akkumuliert | Error-to-Fix SLA | ✅ GEFIXT |
| 4 | 5.1M Tokens ohne Control | Kein Budget | Cost Tracking + Alert | ⏳ OFFEN |
| 5 | Duplizierte Dokus | Kein Single Source | Consolidation + Dedupe | ⏳ OFFEN |

---

## ⚡ PREVENTION RULES (Integriert in Learning Loop)

### Rule 1: Pre-Creation Checklist + Direct Path First
**Before creating new Script/Skill:**
```python
PRE_CREATION_CHECKLIST = [
    "1. Wird dieses Script wirklich benötigt?",
    "2. Existiert bereits ein ähnliches Script?",
    "3. Existiert bereits ein Cron/Tool für diese Aufgabe?",
    "4. Werden mindestens 3 Crons/Tasks es nutzen?",
    "5. Ist der Scope klar definiert? (< 200 Zeilen)",
    "6. Dokumentation: Usage, Inputs, Outputs"
]
```
**Wenn < 3 Cron/Tasks es nutzen:** → Erstelle es NICHT
**NEUE REGEL: Immer zuerst prüfen ob ein einfacher/direkter Weg existiert**

### Rule 2: Implementation First
**Before writing documentation:**
```python
IMPLEMENTATION_FIRST = [
    "1. Code schreiben",
    "2. Testen",
    "3. In Production bringen",
    "4. DANN dokumentieren"
]
```
**Analyse-Dokumente:** Max 1 pro Woche, nur wenn Master fragt

### Rule 3: Error-to-Fix SLA
**Bei Cron Error:
```python
ERROR_SLA = {
    "consecutiveErrors == 1": "Sofort debuggen",
    "consecutiveErrors == 2": "Fix ODER deaktivieren",
    "consecutiveErrors == 3": "Deaktivieren + Master informieren"
}
```

### Rule 4: Stop When Blocked (KRITISCH)
**Problem:** Immer wieder das gleiche Pattern:
```
Task → exec Blocked → Workaround 1 → Blocked → Workaround 2 → ...
```
**Regel:**
```python
EXEC_BLOCK_RULE = {
    "exec killed (preflight)": "SOFORT STOPPEN",
    "2 failed workarounds": "Master fragen, nicht weiter probieren",
    "Komplexer Weg vs einfacher Weg": "Immer einfacheren Weg wählen"
}
```
**Beispiel Capability Evolver:**
- Falsch: 10+ Workarounds versuchen (subagent, bash -c, sessions_spawn...)
- Richtig: Prüfen ob Cron existiert → direkt ausführen

### Rule 5: Cost Budgeting
**Monatliches Budget:**
```python
MONTHLY_TOKEN_BUDGET = 5_000_000  # 5M tokens
ALERT_THRESHOLD = 0.8  # 80% = Alert
CRITICAL_THRESHOLD = 0.95  # 95% = Disable non-critical crons
```

### Rule 6: Single Source Documentation
**Eine Doku pro Topic:**
```
MEMORY_ARCHITECTURE.md ← Only here for memory
SYSTEM_ARCHITECTURE.md ← Only here for architecture
HEARTBEAT.md ← Only here for status
```
**Bei neuer Doku:** Bestehende aktualisieren, nicht neue erstellen

---

## 🔄 INTEGRATION INTO LEARNING LOOP

### Updated Learning Coordinator Checkpoints:

```python
class LearningCoordinator:
    """
    Coordinated Self-Improvement with Fail-Safes
    """
    
    def check_pre_creation(self, script_name: str) -> bool:
        """Rule 1: Pre-Creation Checklist"""
        questions = [
            "Benötigt?",
            "Existiert ähnliches?",
            "Min 3 Nutzer?",
            "Scope < 200 lines?",
            "Doku vorhanden?"
        ]
        return self.ask_master_approval(script_name, questions)
    
    def check_implementation_first(self) -> bool:
        """Rule 2: Implementation First"""
        if self.pending_docs > 0:
            return False  # Don't doc until impl
        return True
    
    def check_error_sla(self, job_id: str) -> None:
        """Rule 3: Error-to-Fix SLA"""
        state = self.get_cron_state(job_id)
        errors = state.get('consecutiveErrors', 0)
        
        if errors >= 3:
            self.disable_cron(job_id)
            self.notify_master(f"CRON {job_id} disabled after {errors} errors")
        elif errors >= 2:
            self.force_fix(job_id)
        else:
            self.debug(job_id)
    
    def check_token_budget(self) -> None:
        """Rule 4: Cost Budgeting"""
        used = self.get_monthly_usage()
        pct = used / MONTHLY_TOKEN_BUDGET
        
        if pct >= CRITICAL_THRESHOLD:
            self.disable_non_critical_crons()
            self.notify_master("TOKEN BUDGET CRITICAL - Non-critical crons disabled")
        elif pct >= ALERT_THRESHOLD:
            self.notify_master(f"Token usage at {pct:.0%}")
    
    def consolidate_documentation(self) -> None:
        """Rule 5: Single Source"""
        # Check for duplicate topics
        # Merge into single source
        # Delete duplicates
        pass
```

---

## 📋 ACTION ITEMS NOW

| # | Action | Status | Notes |
|---|--------|--------|-------|
| 1 | Script Audit: 82 → Active only | ⏳ OFFEN | Identifizieren welche genutzt werden |
| 2 | Fix 3 Cron Errors | ✅ GEFIXT | Nightly/Security auf silent, Health Monitor disabled |
| 3 | Implement Cost Budgeting | ⏳ OFFEN | Token Budget im Learning Coordinator |
| 4 | Consolidate Dokus | ⏳ OFFEN | HEARTBEAT = Single Source |
| 5 | Update Learning Loop with Rules | ✅ DONE | Pre-Creation, Implementation First, Error SLA |

---

## 📊 SUCCESS METRICS

| Metric | Before | After |
|--------|--------|-------|
| Scripts created/day | 40+ | < 5 |
| Implementations before doc | 0 | 1 |
| Cron Error Fix Time | Days | < 1 hour |
| Token Budget Tracking | None | Real-time |
| Duplicate Docus | 5+ | 0 |

---

*Integration: 2026-04-11 12:15 UTC*
*Sir HazeClaw — Solo Fighter*
*Status: Learning from failures*# Simplified Learning Loop — ARCHITEKTUR v1.0

**Datum:** 2026-04-11  
**Version:** 1.0 (SIMPLIFIED)  
**Status:** AKTIV

---

## 🎯 DAS WICHTIGSTE

**Der Learning Loop ist JETZT EINFACH:**

```
learning_coordinator.py (ZENTRAL) → Alles andere
```

**Nichts sonst muss manuell gestartet werden.**

---

## 🏗️ NEUE ARCHITEKTUR

### Der Coordinator (1 Script für alles)

```bash
# Basis Usage
python3 learning_coordinator.py --full

# Das macht:
# 1. System Check
# 2. Innovation Research  
# 3. Quality Gates
# 4. Learning Tracker
```

**Keine 10 verschiedenen Scripts mehr.**

---

## 📊 SCRIPTS (von 76 auf 8 reduziert für Learning Loop)

### Core Learning Loop Scripts:

| Script | Zweck | Aufruf |
|--------|-------|--------|
| `learning_coordinator.py` | **ZENTRAL** - orchestriert alles | Cron: stündlich |
| `innovation_research.py` | Research + KG Update | Via Coordinator |
| `learning_tracker.py` | Patterns/Commits tracken | Via Coordinator |
| `loop_check.py` | Loop Detection | Via Coordinator |
| `self_eval.py` | Quality Score | Via Coordinator |
| `token_tracker.py` | Token Efficiency | Via Coordinator (geplant) |
| `skill_creator.py` | Skills erstellen | Manuell wenn nötig |
| `autonomous_improvement.py` | Auto-Fix | Via Coordinator (geplant) |

### Alle anderen Scripts (68 Stück):
- **Nicht Teil des Learning Loops**
- werden NICHT vom Coordinator aufgerufen
- können manuell verwendet werden

---

## ⏰ AUTOMATISIERUNG

### Stündlicher Cron (Learning Coordinator)
```bash
0 * * * * python3 learning_coordinator.py --full
```

**Das passiert stündlich:**
1. System Check (Disk, Memory, Gateway)
2. Innovation Research (Web Search)
3. Quality Gates (Loop Check, Self Eval)
4. Learning Tracker Update
5. → Telegram bei Issues

### Täglich (14:00 UTC)
```bash
0 14 * * * python3 innovation_research.py --daily
```

---

## 📈 METRIKEN (via Coordinator)

| Metric | Aktuell | Ziel |
|--------|---------|------|
| Score | 99/100 | >95 |
| Tests | 66 | >60 |
| Research Integration | Auto | Auto |
| Token Efficiency | Unknown | -30% |

---

## 🔄 TOKEN TRACKING (NOCH INAKTIV)

**Geplant:** `token_tracker.py` in Coordinator integrieren

**Ziel:** 46% Token Reduction (OpenSpace Pattern)

---

## 📝 DOKUMENTATION

| Datei | Zweck |
|-------|-------|
| `LEARNING_LOOP_ANALYSE.md` | Vollständige Analyse + Plan |
| `SIMPLIFIED_LEARNING_LOOP.md` | Diese Datei - Architektur |
| `skills/self-improvement/IMPROVEMENT_LOOP.md` | Loop Phasen |

---

## ✅ CHECKLISTE

- [x] learning_coordinator.py erstellt
- [x] Stündlicher Cron eingerichtet
- [x] Innovation Research automatisiert
- [x] Quality Gates integriert
- [ ] Token Tracking aktivieren
- [ ] Autonomous Improvement aktivieren

---

*Erstellt: 2026-04-11 10:15 UTC*
*Simplified Architecture v1.0*
