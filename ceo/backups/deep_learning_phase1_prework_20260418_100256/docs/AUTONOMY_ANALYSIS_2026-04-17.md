# Autonomy System Analyse & Optimierungsvorschläge

**Datum:** 2026-04-17
**Analyst:** Sir HazeClaw Subagent
**Kontext:** 65 Lost Tasks (Threshold 70)

---

## 1. SYSTEM ÜBERSICHT

### Architektur (wie dokumentiert in MODUL_05_AUTONOMY.md)

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTONOMY ENGINE                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │ AUTONOMY        │    │ CRON ERROR       │              │
│  │ SUPERVISOR      │    │ HEALER           │              │
│  │ (Live, 5min)    │    │ (Auto)           │              │
│  └────────┬────────┘    └────────┬─────────┘              │
│           │                        │                         │
│           └───────────┬────────────┘                         │
│                       ▼                                      │
│           ┌────────────────────────┐                        │
│           │   AUTONOMY DECISION    │                        │
│           │       ENGINE            │                        │
│           └────────┬────────────────┘                        │
│                    │                                         │
│        ┌───────────┼───────────┐                            │
│        ▼           ▼           ▼                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                 │
│  │ Agent    │ │ Smart    │ │Stagnation │                 │
│  │ Self-    │ │ Evolver  │ │ Breaker   │                 │
│  │ Improver │ │          │ │           │                 │
│  └──────────┘ └──────────┘ └──────────┘                 │
│                                                              │
│  + Self-Healing Engine (Phase 2)                             │
│  + Graceful Degradation Manager                             │
└─────────────────────────────────────────────────────────────┘
```

### Gefundene Scripts

| Script | Status | Funktion |
|--------|--------|----------|
| `autonomy_supervisor.py` | ✅ Active | VIGIL-pattern monitoring, 5min cycle |
| `cron_error_healer.py` | ✅ Active | 4-Stage self-healing (Detect→Diagnose→Heal→Verify) |
| `agent_self_improver.py` | ✅ Active | Daily self-learning, decision tracking |
| `self_healing.py` | ✅ Active | Error-as-prompt, auto-retry, soft failure detection |
| `graceful_degradation.py` | ✅ Active | Cascade failure handling, degradation levels |
| `evolver_signal_bridge.py` | ✅ Active | Event Bus → Evolver integration |
| `evolver_stagnation_breaker.py` | ✅ Active | Gene diversity enforcement |

---

## 2. BEST PRACTICES ANALYSE

### 2.1 Self-Healing Systems (Industry Standards)

**Quelle:** Algomox, OpenAI Cookbook, Elastic Labs

| Best Practice | Implementiert | Status |
|--------------|---------------|--------|
| 4-Stage Loop (Detect→Diagnose→Heal→Verify) | ✅ cron_error_healer.py | ✅ Richtig |
| Circuit Breaker Pattern | ✅ gateway restart limit | ✅ Richtig |
| Exponential Backoff | ✅ calculate_backoff_delay() | ✅ Richtig |
| Error-as-Prompt Pattern | ✅ self_healing.py | ✅ Richtig |
| Actor-Critic Validation | ✅ validate_action() in supervisor | ✅ Richtig |
| Rollback Mechanism | ✅ _rollback() in agent_self_improver | ✅ Richtig |

### 2.2 Fault Tolerance Patterns

**Quelle:** Fractary, GeeksforGeeks, Microservices Resilience

| Pattern | Implementiert | Status |
|---------|---------------|--------|
| Graceful Degradation | ✅ graceful_degradation.py | ✅ Richtig |
| Health Probes | ⚠️ Partial (model health nur in healer) | ⚠️ Lücke |
| Stateless Recovery | ⚠️ State in JSON files | ⚠️ Risk |
| Dead Letter Queue | ❌ Nicht implementiert | ❌ Fehlt |
| Bulkhead Isolation | ❌ Nicht implementiert | ❌ Fehlt |

### 2.3 Autonomy Architecture (OpenAI Cookbook)

| Practice | Implementiert | Status |
|----------|---------------|--------|
| Retraining Loop | ⚠️ Partial (Agent Self-Improver) | ⚠️ Verbesserungsbedarf |
| Feedback Collection | ⚠️ Limited | ⚠️ Lücke |
| Observable Traces | ✅ KG integration | ✅ Gut |
| Prompt Optimization | ⚠️ Via Evolver | ⚠️ Indirekt |

---

## 3. SCHWACHSTELLEN & PROBLEME

### 🔴 KRITISCH: 65 Lost Tasks Stale Data

**Problem:** Die 65 Lost Tasks sind Altlasten, nicht aktive Fehler.

**Analyse:**
- `cron_error_healer.py` trackt Errors in `healer_state.json`
- VERIFY Phase prüft nur "war healing erfolgreich" - aber heilt keine alten Daten
- Die 65 Tasks wurden VOR dem Circuit Breaker akkumuliert
- Kein "Cleanup" Mechanismus für resolved errors

**Schema:**
```python
# healer_state.json - NUR tracking, kein cleanup
{
  "gateway_restarts": [...],  # Akkumuliert ohne Limit
  "disabled_channels": [],    # Kein re-enable nach recovery
  "retry_count_{job_id}": n   # Wird nach max retries reset, aber keine cleanup
}
```

### 🟡 MITTEL: Affective State Monitoring Gaps

**Problem:** `affective_state.json` wird beschrieben aber nie zurückgesetzt.

```python
# autonomy_supervisor.py - update_affective_on_attempt()
# Frustration steigt mit failed attempts - aber sinkt nie!
affective["frustration"]["value"] = min(1.0, current + 0.2)
```

**Issue:** Nach 5 failed heals = frustration 1.0 → System bleibt im "stressed" state auch nach recovery.

### 🟡 MITTEL: Health Check Fragmentation

**Gesundheitschecks sind verteilt:**

| Komponente | Health Check | Ort |
|-----------|--------------|-----|
| Gateway | `openclaw gateway status` | Supervisor |
| Models | `probe_model()` | cron_error_healer |
| Crons | `openclaw cron list` | Multiple |
| Memory | None | ❌ |

**Problem:** Kein zentrales Health Dashboard. Jedes Script prüft anders.

### 🟡 MITTEL: VIGIL Supervisor Read-Only Limitation

**Problem:** Supervisor ist "read-only" - er erstellt Proposals aber führt nichts aus.

```python
# autonomy_supervisor.py
# Supervisor CANNOT modify live system - only proposes
# Proposals müssen manuell implementiert werden
```

**Implikation:** Bei 65 lost tasks erstellt Supervisor Alert, aber niemand löst ihn automatisch.

### 🟢 MINOR: Dead Letter Queue Fehlt

**Problem:** Wenn ein Cron endgültig fehlschlägt, gibt es kein "parking" für später.

- Failed Cron → disable → vergessen
- Keine Retry nach Fix (z.B. Discord wieder verfügbar)

### 🟢 MINOR: Stateless Recovery Mangel

**Problem:** Recovery hängt von State-Files ab, aber bei Start wird nicht geprüft:

```
STATE_FILE.exists() → load_state() 
# Wenn corrupted JSON → crash
```

---

## 4. OPTIMIERUNGSVORSCHLÄGE

### 4.1 Lost Tasks Cleanup (PRIORITÄT: 🔴 KRITISCH)

**Add Cleanup Mechanism zu cron_error_healer.py:**

```python
def cleanup_resolved_errors():
    """
    Clean up stale lost task counts.
    Called monthly or via manual trigger.
    """
    state = load_state()
    
    # Reset gateway restart counter (keep last hour only)
    now = datetime.now()
    state["gateway_restarts"] = [
        t for t in state.get("gateway_restarts", [])
        if datetime.fromisoformat(t) > (now - timedelta(hours=1))
    ]
    
    # Reset consecutive error counts for healthy jobs
    jobs = get_cron_state()
    for job in jobs.get("jobs", []):
        if job.get("state", {}).get("lastRunStatus") != "error":
            retry_key = f"retry_count_{job['id']}"
            if retry_key in state:
                del state[retry_key]
    
    save_state(state)
```

**Add zu Autonomy Supervisor:**

```python
def check_stale_data():
    """Check for stale accumulated data."""
    state = load_state()
    
    # Gateway restarts older than 1 hour
    stale = [
        t for t in state.get("gateway_restarts", [])
        if datetime.fromisoformat(t) < (datetime.now() - timedelta(hours=1))
    ]
    
    if stale:
        return {"stale_data": True, "count": len(stale), "action": "cleanup"}
    return {"stale_data": False}
```

### 4.2 Affective State Decay (PRIORITÄT: 🟡 MITTEL)

**Add recovery decay:**

```python
def apply_affective_recovery():
    """
    Reduce stress scores when system is healthy.
    Call this in VERIFY phase when heals succeed.
    """
    state = json.loads(AFFECTIVE_STATE.read_text())
    affective = state.get("affectiveScores", {})
    
    decay_rate = 0.1  # 10% reduction per cycle
    
    for score_name in ["frustration", "escalating", "anxiety"]:
        if score_name in affective:
            current = affective[score_name].get("value", 0)
            affective[score_name]["value"] = max(0, current - decay_rate)
    
    state["affectiveScores"] = affective
    AFFECTIVE_STATE.write_text(json.dumps(state, indent=2))
```

### 4.3 Central Health Probe (PRIORITÄT: 🟡 MITTEL)

**Create unified health check:**

```python
# health_probe.py - Zentrales Health Check Script
COMPONENT_CHECKS = {
    "gateway": lambda: subprocess.run(["openclaw", "gateway", "status"], ...),
    "crons": lambda: get_cron_state(),
    "models": lambda: [probe_model(m) for m in get_configured_models()],
    "memory": lambda: check_memory_files(),
    "disk": lambda: psutil.disk_usage("/"),
}

def run_health_probe():
    results = {}
    for component, check_fn in COMPONENT_CHECKS.items():
        try:
            results[component] = {"status": "ok", "data": check_fn()}
        except Exception as e:
            results[component] = {"status": "error", "error": str(e)}
    
    # Alert if any critical component down
    critical = ["gateway", "crons"]
    for c in critical:
        if results.get(c, {}).get("status") == "error":
            alert_master(f"{c} health check failed")
    
    return results
```

### 4.4 Dead Letter Queue (PRIORITÄT: 🟡 MITTEL)

**Implement re-enable mechanism:**

```python
# In graceful_degradation.py
class DeadLetterQueue:
    """
    Park failed jobs for later retry.
    """
    def __init__(self, queue_file):
        self.queue_file = queue_file
    
    def park(self, job_id: str, reason: str, last_attempt: str):
        """Park a failed job for later."""
        entry = {
            "job_id": job_id,
            "reason": reason,
            "parked_at": datetime.now().isoformat(),
            "retry_after": None  # Set when retry scheduled
        }
        # Append to queue file
        with open(self.queue_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def retry_parked(self, job_id: str = None):
        """Retry parked jobs."""
        # Read queue, filter, re-enable matching jobs
        # Then rewrite queue without retried items
        pass
```

### 4.5 Stateless Recovery Safety (PRIORITÄT: 🟢 MINOR)

**Add try-except around state loading:**

```python
def load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Corrupted - backup and start fresh
            backup = STATE_FILE.with_suffix('.json.bak')
            STATE_FILE.rename(backup)
            return {"gateway_restarts": [], "disabled_channels": [], "circuit_breaker": {}}
    return {"gateway_restarts": [], "disabled_channels": [], "circuit_breaker": {}}
```

---

## 5. IMPLEMENTATIONS PRIORITÄT

### Phase 1: Quick Fix (Sofort)

| Fix | Impact | Effort | Risk |
|-----|--------|--------|------|
| Lost Tasks Cleanup | 🔴 Hoch | 🟢 Niedrig | 🟢 Sicher |
| Affective Decay | 🟡 Mittel | 🟢 Niedrig | 🟢 Sicher |
| State Loading Safety | 🟡 Mittel | 🟢 Niedrig | 🟢 Sicher |

### Phase 2: Short Term (1-2 Wochen)

| Fix | Impact | Effort | Risk |
|-----|--------|--------|------|
| Central Health Probe | 🟡 Mittel | 🟡 Mittel | 🟢 Mittel |
| Dead Letter Queue | 🟡 Mittel | 🟡 Mittel | 🟡 Mittel |

### Phase 3: Long Term (1 Monat)

| Fix | Impact | Effort | Risk |
|-----|--------|--------|------|
| VIGIL → Active Supervisor | 🔴 Hoch | 🔴 Hoch | 🔴 Hoch |
| KG Integration für Health | 🟡 Mittel | 🟡 Mittel | 🟢 Mittel |

---

## 6. ZUSAMMENFASSUNG

### Was gut läuft ✅

1. **4-Stage Healing Loop** - gut implementiert, industry standard
2. **Circuit Breaker** - verhindert restart loops
3. **Graceful Degradation** - 6 Degradation levels, korrekt implementiert
4. **VIGIL Supervisor Pattern** - read-only监视, aber sicher
5. **Decision Tracking** - Agent Self-Improver funktioniert

### Was gefixt werden muss 🔧

1. **65 Lost Tasks** - Stale data cleanup fehlt
2. **Affective State** - Kein Decay nach recovery
3. **Health Check** - Fragmentiert, kein central monitoring
4. **State Files** - Kein backup bei corruption

### Empfehlung

**Priorität 1:** Lost Tasks Cleanup Script
**Priorität 2:** Affective Decay implementieren
**Priorität 3:** Health Probe centralisieren

---

*Analyse erstellt: 2026-04-17 | Sir HazeClaw Subagent*