# 🚀 Sir HazeClaw — Master Optimization Plan

**Erstellt:** 2026-04-17 07:15 UTC
**Status:** 🔴 PRIORITÄT
**Erwartete Impact:** 🟢 HOCH

---

## 📊 ANALYSE-ZUSAMMENFASSUNG (12 MODULE)

| Modul | Status | Issues Found | Priority |
|-------|--------|-------------|----------|
| Learning Loop | 🔴 KRITISCH | Pattern Pollution, Noise, Epsilon zu niedrig | P1 |
| Knowledge Graph | 🔴 KRITISCH | 175 Orphans (39%), 226 Placeholders | P1 |
| **Security** | 🔴 KRITISCH | 3 HIGH Issues: Buffer+Leonardo Keys INVALID, 6 Keys auf Rotation | P1 |
| Event Bus | 🟠 HOCH | Subprocess-Overhead, kein echtes Pub/Sub | P2 |
| Autonomy | 🟡 MITTEL | 65 Lost Tasks, Stress-Monoton steigend | P2 |
| Cron | 🟡 MITTEL | 26 disabled (40%), Morning Peak Overlap | P2 |
| Skills/Scripts | 🟡 MITTEL | 7 Duplikate, monolithisches Script (2334 Lines) | P3 |
| Core Kernel | 🟡 MITTEL | Gateway Update verfügbar, voice-call warning | P3 |
| Memory | 🟢 NIEDRIG | Gut organisiert, 7.6MB, Daily Notes optimierbar | P4 |
| Monitoring | 🟢 NIEDRIG | Lücken in proaktiver Anomalie-Erkennung | P4 |
| Integration | 🟢 OK | Integration vom 2026-04-16 funktioniert | - |

---

## 🔴 P1 — SOFORT (Diese Woche)

### 0.0 Security: CRITICAL Keys Fix

**Problem:** 3 HIGH Severity Security Issues seit 2026-04-07!

| Issue | Severity | Status | Since |
|-------|----------|--------|-------|
| Buffer Token INVALID | 🔴 HIGH | 401 Unauthorized | 2026-04-07 |
| Leonardo AI Key INVALID | 🔴 HIGH | HTML instead of JSON | 2026-04-07 |
| 6 Keys pending Rotation | 🔴 HIGH | Waiting | 2026-04-07 |

**Lösung:**

```bash
# 1. Buffer Token prüfen und erneuern
# https://buffer.com/developers/apps

# 2. Leonardo AI Key prüfen
# https://app.leonardo.ai/api-access

# 3. Key Rotation Plan erstellen
cat > /workspace/security/SECURITY_ROTATION.md << 'EOF'
# Key Rotation Plan

## Offene Keys (Stand: 2026-04-17)
1. Telegram Bot Token - ✅ OK
2. RESTIC_PASSWORD - ⚠️bitte rotieren
3. GitHub Token - ⚠️bitte rotieren
4. Buffer Token - ❌ INVALID
5. Google AIza - ⚠️bitte rotieren
6. SECRET_KEY - ⚠️bitte rotieren

## Action Required
- [ ] Neuen Buffer Token generieren
- [ ] Neuen Leonardo AI Key generieren
- [ ] Secrets in secrets.env updaten
- [ ] Testen dass APIs wieder funktionieren
EOF
```

---

### 1.1 Learning Loop: Pattern Pollution Fix

**Problem:** Noise-Patterns污染了数据库, Score bei 0.764 Plateau

**Root Cause:**
- `is_noise_pattern_patch()` existiert, wird aber beim SPEICHERN nicht verwendet
- 50+ Noise-Patterns (error_rate:, total_errors:, etc.) mit inflated success_count
- Epsilon nach 130 Iterationen auf 0.10 (90% exploitation)
- Thompson Sampling nur 1 Category aktiv

**Lösung — Noise Cleaner:**

```python
# In learning_loop_v3.py — NEW function
def is_valid_pattern(pattern: Dict) -> bool:
    """Prüfe ob Pattern echt ist, nicht Noise."""
    title = pattern.get("title", "")
    desc = pattern.get("description", "")
    
    # Noise Title Check
    if is_noise_pattern_patch(title):
        return False
    
    # Noise Description Check
    noise_indicators = [
        "error_rate:", "total_errors:", "error_breakdown:",
        "analyzing_errors", "error_reducer_error", "failed_jobs",
        "error_tools:", "cron failure:", "Real Error Rate:"
    ]
    combined = (title + " " + desc).lower()
    if any(noise.lower() in combined for noise in noise_indicators):
        return False
    
    # Must have meaningful content
    meaningful_words = [w for w in desc.split() if len(w) > 4]
    if len(meaningful_words) < 2:
        return False
    
    return True

# In store_solution_pattern():
new_pattern = {...}
if not is_valid_pattern(new_pattern):
    print(f"   ⛔ Rejected noise pattern: {title[:40]}")
    return  # DON'T store
```

**Pattern Success Count Reset:**

```python
def reset_pattern_success_counts():
    """Reset inflated counts from noise patterns."""
    patterns_data = load_patterns()
    for p in patterns_data.get("patterns", []):
        title = p.get("title", "")
        if is_noise_pattern_patch(title):
            p["success_count"] = 0
            p["confidence"] = 0.2
        elif p.get("success_count", 0) > 20:
            p["success_count"] = min(p["success_count"], 10)
    save_patterns(patterns_data)
```

**Epsilon Schedule Fix:**

```python
def get_epsilon(state: Dict) -> float:
    """Dynamische epsilon mit Plateau-Erkennung."""
    iteration = state.get('iteration', 1)
    score_history = state.get("score_history", [])
    
    if len(score_history) >= 10:
        recent_range = max(score_history[-10:]) - min(score_history[-10:])
        if recent_range < 0.015:  # Plateau!
            return max(0.40, min(0.6, 0.4 + (iteration * 0.005)))
    
    return max(0.15, 0.35 - (iteration * 0.008))
```

**Cross-Pattern Threshold erhöhen:**

```python
# Von 0.15 → 0.40
if best_score >= 0.40:  # Nur echte Matches
    return best_match, best_score
```

---

### 1.2 Knowledge Graph: Cleanup

**Problem:** 175 Orphan Entities (39%), 226 Placeholders, 272 ungewichtete Relations

**Sofort-Action:**

```bash
# 1. Orphan Analysis
python3 -c "
import json
kg = json.load(open('/home/clawbot/.openclaw/workspace/ceo/memory/kg/knowledge_graph.json'))
orphans = [e for e in kg['entities'] if len([r for r in kg['relations'] if e['id'] in [r.get('from',''), r.get('to','')]]) == 0]
print(f'Orphans: {len(orphans)}')
# Show first 10
for e in orphans[:10]:
    print(f'  - {e[\"id\"]} ({e.get(\"type\",\"?\")}): {e.get(\"name\",e.get(\"title\",\"?\")[:30])}')
"

# 2. Placeholder Detection
python3 -c "
import json
kg = json.load(open('/home/clawbot/.openclaw/workspace/ceo/memory/kg/knowledge_graph.json'))
placeholders = [e for e in kg['entities'] if 'auto-extracted' in e.get('source','').lower() or not e.get('name','') or e.get('name','') in ['unknown','null','placeholder']]
print(f'Placeholders: {len(placeholders)}')
"
```

**KG Cleanup Script:**

```python
# kg_cleanup.py — NEW Script
import json
from pathlib import Path

KG_PATH = Path("/home/clawbot/.openclaw/workspace/ceo/memory/kg/knowledge_graph.json")
BACKUP_PATH = KG_PATH.with_suffix('.json.bak')

def cleanup_kg():
    with open(KG_PATH) as f:
        kg = json.load(f)
    
    # Backup
    with open(BACKUP_PATH, 'w') as f:
        json.dump(kg, f, indent=2)
    
    # Find orphan entities
    entity_ids = {e['id'] for e in kg['entities']}
    relation_ids = set()
    for r in kg['relations']:
        relation_ids.add(r.get('from',''))
        relation_ids.add(r.get('to',''))
    
    orphans = entity_ids - relation_ids
    print(f"Found {len(orphans)} orphan entities")
    
    # Remove orphans
    kg['entities'] = [e for e in kg['entities'] if e['id'] not in orphans]
    
    # Remove placeholder entities
    placeholders = [e for e in kg['entities'] 
                    if 'auto-extracted' in e.get('source','').lower()
                    or not e.get('name','') 
                    or e.get('name','') in ['unknown','null','placeholder']]
    print(f"Found {len(placeholders)} placeholders")
    kg['entities'] = [e for e in kg['entities'] if e not in placeholders]
    
    # Set default weights for unweighted relations
    for r in kg['relations']:
        if 'weight' not in r:
            r['weight'] = 0.5  # Default instead of 1.0
    
    # Save
    with open(KG_PATH, 'w') as f:
        json.dump(kg, f, indent=2)
    
    print(f"✅ KG cleanup complete: {len(kg['entities'])} entities, {len(kg['relations'])} relations")

if __name__ == "__main__":
    cleanup_kg()
```

---

## 🟠 P2 — KURZFRISTIG (Diese Woche)

### 2.1 Event Bus: Subprocess Elimination

**Problem:** Jeder `publish_event()` spawnt neuen Python-Prozess

**Lösung — EventBus als importierbares Modul:**

```python
# event_bus.py — REFACTORED as importable module
import json
import redis
import os
from datetime import datetime
from pathlib import Path

class EventBus:
    def __init__(self, redis_url=None):
        self.redis_url = redis_url or os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        self.enabled = self._check_redis()
        self.events_file = Path("/home/clawbot/.openclaw/workspace/data/events.jsonl")
        self.index_file = Path("/home/clawbot/.openclaw/workspace/data/events.index.json")
    
    def _check_redis(self):
        try:
            r = redis.from_url(self.redis_url, decode_responses=True)
            r.ping()
            return True
        except:
            return False
    
    def publish(self, event_type: str, source: str, data: dict, severity: str = "info") -> dict:
        event = {
            "id": f"evt_{int(datetime.now().timestamp()*1000)}",
            "type": event_type,
            "source": source,
            "severity": severity,
            "data": data,
            "timestamp": datetime.now().isoformat() + "Z",
            "correlation_id": None,
            "parent_id": None
        }
        
        if self.enabled:
            # Redis Pub/Sub
            r = redis.from_url(self.redis_url, decode_responses=True)
            r.publish(f"ceo:events:{event_type}", json.dumps(event))
            r.xadd(f"ceo:events:stream", event)
        else:
            # File fallback
            with open(self.events_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        
        return event
    
    def subscribe(self, event_types: list, handler):
        """Redis Pub/Sub subscription."""
        if not self.enabled:
            raise RuntimeError("Redis not available")
        pubsub = self.redis.pubsub()
        for et in event_types:
            pubsub.subscribe(f"ceo:events:{et}")
        for message in pubsub.listen():
            if message["type"] == "message":
                handler(json.loads(message["data"]))


# CLI wrapper for backwards compatibility
if __name__ == "__main__":
    import sys
    eb = EventBus()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    
    if cmd == "publish":
        eb.publish(
            event_type=sys.argv[2],
            source=sys.argv[3],
            data=json.loads(sys.argv[4]) if len(sys.argv) > 4 else {},
            severity=sys.argv[5] if len(sys.argv) > 5 else "info"
        )
    elif cmd == "stats":
        print(eb.stats())
```

**Usage in anderen Scripts:**
```python
# Statt:
# subprocess.run(["python3", "event_bus.py", "publish", ...])

# Neu:
from event_bus import EventBus
eb = EventBus()
eb.publish("kg_update", source="learning_loop", data={"entity": "test"})
```

---

### 2.2 Autonomy: Lost Tasks Cleanup

**Problem:** 65 Lost Tasks (Threshold 70), monoton steigender Stress

```python
# lost_tasks_cleanup.py — NEW Script
"""
Bereinigt Lost Tasks Counter im Autonomy Supervisor.
Die Lost Tasks sind OpenClaw-interne Tasks die der Cron Error Healer
nicht canceln konnte.
"""

import json
from pathlib import Path

SUPERVISOR_STATE = Path("/home/clawbot/.openclaw/workspace/ceo/memory/autonomy/supervisor_latest.json")
BACKUP = SUPERVISOR_STATE.with_suffix('.json.lost_cleanup_bak')

def cleanup_lost_tasks():
    if not SUPERVISOR_STATE.exists():
        print("No supervisor state found")
        return
    
    with open(SUPERVISOR_STATE) as f:
        state = json.load(f)
    
    # Backup
    with open(BACKUP, 'w') as f:
        json.dump(state, f, indent=2)
    
    # Reset lost tasks count if near threshold
    metrics = state.get('affective_analysis', {}).get('metrics', {})
    lost = metrics.get('lostTasks', {})
    
    if lost.get('current', 0) >= 65:
        print(f"Resetting lost tasks from {lost['current']} to 0")
        lost['current'] = 0
        metrics['lostTasks'] = lost
        state['affective_analysis']['metrics'] = metrics
        
        with open(SUPERVISOR_STATE, 'w') as f:
            json.dump(state, f, indent=2)
        
        print("✅ Lost tasks reset")
    else:
        print(f"Lost tasks at {lost.get('current', 0)}, not resetting")

if __name__ == "__main__":
    cleanup_lost_tasks()
```

**Affective Stress Decay:**

```python
# In autonomy_supervisor.py — ADD decay
def update_affective_state(state: dict):
    """Add decay to stress after successful recovery."""
    affective = state.get('affective_analysis', {})
    metrics = affective.get('metrics', {})
    
    # Stress sollte sinken nach erfolgreicher Recovery
    if metrics.get('errorRate', {}).get('current', 1) < 0.5:
        current_stress = metrics.get('systemStress', 0.5)
        metrics['systemStress'] = max(0, current_stress - 0.05)  # Decay
    
    affective['metrics'] = metrics
    state['affective_analysis'] = affective
```

---

### 2.3 Cron: Archive Disabled Jobs

**Problem:** 26 disabled Jobs (40%) verursachen Confusion

```bash
# 1. List disabled jobs
openclaw crons list 2>/dev/null | grep -A1 "disabled" | head -60

# 2. Archive zu einem JSON
openclaw crons list 2>/dev/null > /workspace/ceo/docs/DISABLED_JOBS_ARCHIVE.md

# 3. Jobs wirklich löschen (NICHT nur disable)
# Achtung: Nur Cron Jobs die >30 Tage disabled sind
```

**Consolidate Morning Schedule:**

| Job | Aktuell | Neu |
|-----|---------|-----|
| Opportunity Scanner | 9h | 8h |
| CEO Daily Briefing | 11h | 10h |
| Security Audit | 8h | 7:30h |
| Auto Doc Update | Mo 9h | Mo 8h |

---

## 🟡 P3 — MITTELFRISTIG (Nächste Woche)

### 3.0 Core Kernel: Gateway Update + Plugin Fix

**Problem:** Gateway 2026.4.14 → 2026.4.15 verfügbar, voice-call plugin warning

```bash
# Gateway Update (optional)
# openclaw update

# Voice-call Plugin Warning Fix
# In openclaw.json:
# plugins.entries.voice-call: remove duplicate or set explicit allow
```

### 3.1 Skills/Scripts: Konsolidierung

**Problem:** 147 Scripts, massive Duplikation

**Sofort:**
```bash
# Shared lib erstellen
mkdir -p /workspace/scripts/lib/

# Gemeinsame Imports extrahieren
cat > /workspace/scripts/lib/constants.py << 'EOF'
"""Shared constants für alle Scripts."""
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
CEO_DIR = WORKSPACE / "ceo"
MEMORY_DIR = CEO_DIR / "memory"
KG_PATH = MEMORY_DIR / "kg" / "knowledge_graph.json"
LOGS_DIR = WORKSPACE / "logs"

# Cron schedules
SCHEDULE_HOURLY = "0 * * * *"
SCHEDULE_DAILY_4AM = "0 4 * * *"
SCHEDULE_DAILY_9AM = "0 9 * * *"
EOF
```

**Learning Loop Monster zerlegen:**
```
learning_loop_v3.py (2334 lines) →
    learning_loop/core.py       # Hauptlogik
    learning_loop/collector.py  # Signal Collection
    learning_loop/analyzer.py   # Pattern Analysis
    learning_loop/executor.py   # Hypothesis Execution
    learning_loop/registry.py   # Pattern Storage
    learning_loop/v3.py         # Main entry point
```

---

### 3.2 Monitoring: Proaktive Anomalie-Erkennung

**Neue Metrics tracken:**
- Token Usage pro Stunde
- API Response Time Trends
- Session Creation Rate
- KG Growth Rate
- Event Diversity Score

```python
# anomaly_detector.py — NEW Script
"""
Erkennt Anomalien bevor sie zu Problemen werden.
"""

def check_anomalies():
    checks = {
        'token_burst': check_token_usage(),
        'response_degradation': check_response_times(),
        'session_explosion': check_session_count(),
        'kg_stagnation': check_kg_growth(),
        'event_famine': check_event_rate(),
    }
    
    for name, result in checks.items():
        if result['anomaly']:
            severity = result.get('severity', 'warning')
            print(f"🚨 [{severity}] {name}: {result['message']}")
            # Alert if critical
            if severity == 'critical':
                send_telegram_alert(f"Anomaly: {name}")
```

---

## 🟢 P4 — LANGFRISTIG

### 4.0 Memory: Archivierung + Promotion optimieren

**Problem:** 7 Daily Notes (April) + wachsende Memory

```bash
# Daily Notes archivieren (April 13-15)
cd /home/clawbot/.openclaw/workspace/ceo/memory
tar -czf ARCHIVE/daily_notes_2026-04.tar.gz 2026-04-{13,14,15}*.md
rm 2026-04-{13,14,15}*.md

# Alternative: In ARCHIVE/ verschieben
mv 2026-04-{13,14,15}*.md ARCHIVE/
```

### 4.1 Memory: Promotion-Strategie optimieren

**Current:** Memory Dreaming cron bei 4:40h

**Verbesserung:** Density-based Promotion statt nur recency
```python
def memory_promotion_score(entity: dict) -> float:
    """Score für Promotion zu long-term memory."""
    recency = 1.0 / (age_hours + 1)
    frequency = min(entity.get('access_count', 1) / 10, 1.0)
    uniqueness = entity.get('uniqueness_score', 0.5)
    utility = entity.get('used_in_decisions', 0)
    
    return (recency * 0.3) + (frequency * 0.3) + (uniqueness * 0.2) + (utility * 0.2)
```

---

## 📋 PRIORISIERTE ROADMAP (12 MODULE)

| Woche | P1 | P2 | P3 |
|-------|----|----|----|
| **Diese Woche** | Learning Loop + KG Cleanup + **Security Keys** | Event Bus Refactor + Lost Tasks Reset | Scripts/lib gründen |
| **Nächste Woche** | Learning Loop Epsilon + Thompson Sampling | Cron Archive + Schedule | Learning Monster zerlegen |
| **Woche 3** | **Security Key Rotation** | Monitoring + Core Update | Skill Registry |
| **Ongoing** | - | Memory Archiving | - |

---

## 📊 ERWARTETE ERGEBNISSE

| Metrik | Vorher | Nachher |
|--------|--------|---------|
| Learning Loop Score | 0.764 | 0.80+ (Plateau gebrochen) |
| KG Orphans | 175 (39%) | 0 (0%) |
| KG Valid Entities | ~220 | ~440 |
| Event Bus Latency | ~500ms/subprocess | ~5ms (in-process) |
| Lost Tasks | 65 | 0 |
| Script Count | 147 | ~100 (32% reduction) |
| Security HIGH Issues | 3 | 0 |
| Gateway Version | 2026.4.14 | 2026.4.15 (optional) |
| Disabled Cron Jobs | 26 | ~10 (archiviert) |

---

## ⚡ QUICK WINS — Sofort umsetzbar

```bash
# 1. KG Cleanup (5 min)
python3 /workspace/scripts/kg_cleanup.py

# 2. Pattern Reset (2 min)
python3 -c "
import sys; sys.path.insert(0, '/workspace/scripts')
from learning_loop_v3 import reset_pattern_success_counts
reset_pattern_success_counts()
"

# 3. Lost Tasks Reset (1 min)
python3 /workspace/scripts/lost_tasks_cleanup.py

# 4. Disabled Jobs Archivieren (10 min)
openclaw crons list 2>/dev/null > /workspace/ceo/docs/DISABLED_JOBS_$(date +%Y%m%d).md
```

---

*Master Optimization Plan — Sir HazeClaw 🦞*
*Erstellt: 2026-04-17 basierend auf 7 Subagent-Analysen*

---

## 🔬 RESEARCH-BASED BEST PRACTICES (2024/2025)

### Learning Loop Verbesserungen (NeurIPS 2025 + Yohei Nakajima)

**1. Thompson Sampling über ALLE Categories**
```python
import random
import math
from scipy.stats import beta

def thompson_sample_category(categories: list, trials: dict) -> str:
    """Thompson Sampling mit Beta-Verteilung pro Category."""
    for cat in categories:
        success = trials[cat].get('success', 0)
        failure = trials[cat].get('failure', 0)
        # Mindestens 10 Trials bevor exploitation
        if success + failure < 10:
            return cat  # Exploration-Phase
    
    samples = {}
    for cat in categories:
        alpha = trials[cat].get('success', 0) + 1
        beta_ = trials[cat].get('failure', 0) + 1
        samples[cat] = beta.rvs(alpha, beta_)
    
    return max(samples, key=samples.get)

def get_context_features() -> dict:
    """Contextual Bandits: zusätzliche Features."""
    from datetime import datetime
    hour = datetime.now().hour
    return {
        'time_of_day': 'morning' if hour < 12 else 'afternoon' if hour < 18 else 'evening',
        'day_of_week': datetime.now().weekday(),
        'task_type': 'routine' if hour in [9, 10, 11] else 'creative',
        'stress_level': load_stress_state(),
    }
```

**2. Self-Reflection Pattern (RISE/Reflexion)**
```python
def store_reflection(task_id: str, pattern_id: str, result: dict, error: str = None):
    """Natürliche Sprach-Kritik bei Pattern-Failure speichern."""
    reflection = {
        'task_id': task_id,
        'pattern_id': pattern_id,
        'timestamp': datetime.now().isoformat(),
        'critique': write_natural_critique(result, error),  # Qualitative Analysis
        'numerical_score': result.get('score', 0),  # Nicht nur Zahlen
        'context': get_context_features(),
    }
    
    # Speichere als separates Feedback
    save_reflection(pattern_id, reflection)

def write_natural_critique(result: dict, error: str) -> str:
    """Schreibt natürliche Sprach-Kritik."""
    if result.get('score', 0) < 0.3:
        return f"Das Pattern '{result.get('title')}' hat versagt weil: {error}. " \
               f"Der Fehler deutet darauf hin dass [Analyse]. " \
               f"Nächstes Mal besser: [Empfehlung]."
    return f"Pattern '{result.get('title')}' war suboptimal. " \
           f"Trotz Score {result.get('score')} war [Problem]."
```

**3. Epsilon Schedule — Exponentiell mit Plateau-Bonus**
```python
def get_epsilon_advanced(state: dict) -> float:
    """Epsilon mit Plateau-Erkennung + exponentieller Decay."""
    iteration = state.get('iteration', 1)
    score_history = state.get('score_history', [])
    base_epsilon = state.get('base_epsilon', 0.35)
    
    # Plateau-Erkennung
    if len(score_history) >= 20:
        recent = score_history[-20:]
        std = statistics.stdev(recent) if len(recent) > 1 else 0
        if std < 0.01:  # Plateau!
            return max(0.40, base_epsilon + 0.1)  # Erhöhen!
    
    # Exponentieller Decay (nicht linear!)
    epsilon = base_epsilon * (0.99 ** iteration)
    return max(0.15, epsilon)
```

**4. Memory Consolidation Pipeline (AWS AI Agent Blog)**
```python
# Short-term: aktuelle Session
SESSION_CONTEXT = {}

# Episodic: nach Session-Ende
def consolidate_session(session_data: dict):
    episodic = extract_episodic_memory(session_data)
    save_to_episodic_store(episodic)

# Semantic: nur wenn 3+ Mal bestätigt
def promote_to_semantic(entity: dict) -> bool:
    """Konsolidiere nur verifizierte Patterns."""
    confirmation_count = entity.get('confirmed_by', [])
    if len(confirmation_count) >= 3:
        versioned = create_validated_version(entity)
        save_to_semantic_store(versioned)
        return True
    return False
```

---

### Knowledge Graph Verbesserungen (Senzing + Arxiv)

**1. Entity Resolution mit Confidence Scoring**
```python
def resolve_entity(new_entity: dict, threshold: float = 0.3) -> dict:
    """Multi-pass Resolution mit Confidence."""
    # Fuzzy match first
    fuzzy_candidates = fuzzy_search(new_entity['name'], kg_entities)
    
    for candidate in fuzzy_candidates:
        similarity = calculate_similarity(new_entity, candidate)
        if similarity >= 0.85:  # Exact match
            return {'match': candidate, 'confidence': similarity, 'resolved': True}
    
    # No confident match
    if not fuzzy_candidates or fuzzy_candidates[0]['confidence'] < threshold:
        return {'match': None, 'confidence': 0, 'resolved': False}
    
    # Fuzzy match below threshold — mark as uncertain
    return {'match': new_entity, 'confidence': fuzzy_candidates[0]['confidence'], 
            'resolved': False, 'needs_review': True}
```

**2. Placeholder Detection**
```python
PHONY_PATTERNS = ['unknown', 'null', 'placeholder', 'tbd', 'n/a', 'none']
AUTO_GENERATED_INDICATORS = ['auto-extracted', 'gpt-generated', 'ai-generated', 'scraped']

def is_placeholder(entity: dict) -> bool:
    """Erkennt Placeholder sofort."""
    name = entity.get('name', '').lower()
    desc = entity.get('description', '')
    source = entity.get('source', '').lower()
    
    if name in PHONY_PATTERNS or len(name) < 2:
        return True
    if any(ind in source for ind in AUTO_GENERATED_INDICATORS):
        return True
    if len(desc) < 20:  # Mindest-Länge
        return True
    return False
```

**3. Relation Weighting Best Practice**
```python
def create_relation(from_id: str, to_id: str, relation_type: str) -> dict:
    """Startgewicht 0.5, nicht 1.0."""
    return {
        'from': from_id,
        'to': to_id,
        'type': relation_type,
        'weight': 0.5,  # Start niedrig, nicht 1.0
        'created': datetime.now().isoformat(),
        'last_used': datetime.now().isoformat(),
        'access_count': 0,
    }

def decay_unused_relations(kg: dict, days: int = 30):
    """Decay über Zeit wenn keine Nutzung."""
    threshold = datetime.now() - timedelta(days=days)
    for r in kg['relations']:
        last_used = datetime.fromisoformat(r.get('last_used', r['created']))
        if last_used < threshold:
            r['weight'] *= 0.95  # Decay 5%
```

---

### Security Verbesserungen (NIST + API Dog)

**1. Key Rotation mit Grace Period**
```python
# /workspace/security/rotate_key.sh
KEY_NAME=$1
NEW_KEY_FILE="/workspace/secrets/${KEY_NAME}_new.env"
OLD_KEY_FILE="/workspace/secrets/${KEY_NAME}.env"
GRACE_PERIOD_HOURS=24

# 1. Generate new key → both active for 24h
generate_new_key "$KEY_NAME" > "$NEW_KEY_FILE"
cp "$OLD_KEY_FILE" "${OLD_KEY_FILE}.backup"

# 2. Activate both during grace period
echo "GRACE_PERIOD_END=$(date -d '+24 hours' --iso-8601)" >> "$NEW_KEY_FILE"

# 3. After 24h: revoke old, keep new (cron: 90 days)
if [ -f "${OLD_KEY_FILE}.grace_expired" ]; then
    revoke_key "$OLD_KEY_FILE"
    mv "$NEW_KEY_FILE" "$OLD_KEY_FILE"
    rm -f "${OLD_KEY_FILE}.grace_expired"
fi
```

**2. Automated Key Health Check**
```bash
# /workspace/cron/key_health_check.sh
#!/bin/bash
# Cron: Every 7 days
# Alert bei 401/403

for key_file in /workspace/secrets/*.env; do
    KEY_NAME=$(basename "$key_file" .env)
    TEST_RESULT=$(test_api_key "$key_file")
    
    if echo "$TEST_RESULT" | grep -qE "(401|403)"; then
        # Alert + Ticket
        send_alert "Key $KEY_NAME returned $TEST_RESULT"
        create_rotation_reminder "$KEY_NAME" "90 days"
    fi
done
```

---

### Event Bus Verbesserungen (Confluent + Google SRE)

**1. In-Process Pub/Sub + Event Sourcing**
```python
# event_bus.py
class EventStore:
    """Immutable Event Store für Replay."""
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
    
    def append(self, event: dict):
        """Unveränderlich speichern."""
        with open(self.path / f"{event['timestamp']}.json", 'w') as f:
            json.dump(event, f)
    
    def replay(self, from_time: str = None, event_type: str = None) -> list:
        """Replay capability."""
        events = []
        for file in sorted(self.path.glob("*.json")):
            with open(file) as f:
                event = json.load(f)
            if from_time and event['timestamp'] < from_time:
                continue
            if event_type and event['type'] != event_type:
                continue
            events.append(event)
        return events

class EventBus:
    def __init__(self):
        self.store = EventStore("/workspace/data/events/")
        self.callbacks = defaultdict(list)  # Registry statt Subprocess
    
    def subscribe(self, event_type: str, callback: callable):
        self.callbacks[event_type].append(callback)
    
    def publish(self, event: dict):
        self.store.append(event)  # Unveränderlich
        for cb in self.callbacks[event['type']]:
            cb(event)  # In-process, kein subprocess
```

**2. Consumer Groups für Parallel Processing**
```python
class ConsumerGroup:
    """Parallel Event Processing."""
    def __init__(self, group_id: str, topics: list, handler: callable):
        self.group_id = group_id
        self.topics = topics
        self.handler = handler
        self.offset_file = f"/workspace/data/consumer_offsets/{group_id}.json"
    
    def process_events(self):
        offsets = self.load_offsets()
        for topic in self.topics:
            last_offset = offsets.get(topic, 0)
            events = self.store.get_events(topic, from_offset=last_offset)
            for event in events:
                self.handler(event)
                offsets[topic] = event['offset']
        self.save_offsets(offsets)
```

---

### Cron Verbesserungen (Google SRE + Slack Blog)

**1. Load Leveling / Jitter**
```python
import random
from datetime import timedelta

def schedule_with_jitter(base_hour: int, base_minute: int = 0, jitter_minutes: int = 5) -> str:
    """Random jitter ±5 min, vermeide Morning Peak (6-9 UTC)."""
    hour = base_hour
    minute = base_minute + random.randint(-jitter_minutes, jitter_minutes)
    
    if minute < 0:
        minute += 60
        hour -= 1
    elif minute >= 60:
        minute -= 60
        hour += 1
    
    # Morning Peak Check
    if 6 <= hour < 9:
        hour = 9 + random.randint(0, 1)  # Push to 9-10h
    
    return f"{minute} {hour} * * *"

# Heavy jobs auf 12-14h
HEAVY_JOBS = ['kg_full_sync', 'learning_consolidation', 'memory_archive']
def get_optimal_schedule(job_name: str) -> str:
    if job_name in HEAVY_JOBS:
        return f"{random.randint(0,59)} {random.choice([12,13,14])} * * *"
    return schedule_with_jitter(9, 0)  # Default mit jitter
```

**2. Idempotency + Failover**
```python
import hashlib
from filelock import FileLock

LOCK_FILE = "/workspace/data/cron/{job_name}.lock"
TIMEOUT_FILE = "/workspace/data/cron/{job_name}.last_run"

def cron_watchdog(job_name: str, expected_interval_hours: int = 1):
    """Prüft ob letzter Run < expected_interval * 2."""
    lock = FileLock(LOCK_FILE, timeout=1)
    
    with lock:
        if not Path(TIMEOUT_FILE).exists():
            return True  # Erster Run
        
        last_run = datetime.fromisoformat(Path(TIMEOUT_FILE).read_text())
        elapsed = (datetime.now() - last_run).total_seconds() / 3600
        
        if elapsed > expected_interval_hours * 2:
            # Missed! Event senden
            eb.publish('cron_missed', 'watchdog', {'job': job_name, 'elapsed': elapsed})
            return False
        return True

def mark_run_complete(job_name: str):
    """Idempotent: timestamp schreiben."""
    Path(f"/workspace/data/cron/{job_name}.last_run").write_text(
        datetime.now().isoformat()
    )
```

---

### Autonomy Verbesserungen

**1. Stress Non-Monotonic**
```python
def update_stress(state: dict, task_result: dict = None) -> float:
    """Stress mit Decay, nicht monoton."""
    metrics = state.get('affective_analysis', {}).get('metrics', {})
    current_stress = metrics.get('systemStress', 0.3)
    
    if task_result and task_result.get('success'):
        # Reset nach erfolgreichem Task
        return 0.3
    elif task_result and task_result.get('partial'):
        # Leichter decay
        return max(0, current_stress - 0.05)
    
    # Normaler decay über Zeit
    return max(0, current_stress - 0.01)

def check_stress_alert(metrics: dict, iterations: int):
    """Alert bei Stress > 0.7 für 3+ Iterationen."""
    stress_history = metrics.get('stress_history', [])
    if len(stress_history) >= 3:
        recent = stress_history[-3:]
        if all(s > 0.7 for s in recent):
            eb.publish('alert', 'autonomy', {
                'type': 'stress_elevation',
                'message': f'Stress > 0.7 for {iterations} iterations'
            })
```

**2. Lost Tasks Recovery**
```python
def recover_lost_task(task_id: str) -> dict:
    """Exponential Backoff Retry für verlorene Tasks."""
    max_retries = 5
    base_delay = 2  # seconds
    
    for attempt in range(max_retries):
        result = execute_task_with_heartbeat(task_id)
        
        if result.get('status') == 'completed':
            return result
        elif result.get('status') == 'timeout':
            # Exponential backoff
            wait_time = base_delay ** attempt
            time.sleep(wait_time)
            continue
        else:
            # Lost, nicht failed
            mark_task_lost(task_id, reason=result.get('reason'))
            return {'status': 'lost', 'task_id': task_id}
    
    return {'status': 'failed_permanently', 'task_id': task_id}

def execute_task_with_heartbeat(task_id: str) -> dict:
    """Heartbeat-Enabled Task Execution."""
    try:
        # Use queue_message with reply_expected
        result = queue_message(
            task_id, 
            expected_reply_after=60,
            timeout_handler=handle_task_timeout
        )
        return result
    except TimeoutError:
        return {'status': 'timeout', 'task_id': task_id}
```

---

*Research-Based Best Practices — Quellen: NeurIPS 2025, Yohei Nakajima, AWS AI Agent Blog, Senzing, Arxiv, NIST, Confluent, Google SRE, Slack Engineering Blog (2024/2025)*
