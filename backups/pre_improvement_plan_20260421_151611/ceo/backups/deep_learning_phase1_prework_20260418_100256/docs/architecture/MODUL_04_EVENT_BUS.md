# MODUL 04: Event Bus

**Modul:** Event Bus — Cross-System Kommunikation
**Status:** ✅ Dokumentiert
**Letztes Update:** 2026-04-17

---

## 4.1 OVERVIEW

Der Event Bus ist das **Kommunikations-System** zwischen allen Komponenten. Ermöglicht:
- Pub/Sub zwischen Scripts
- System-übergreifende Events
- Stagnation Detection
- Evolver Signal Bridge

### Aktuelle Stats

| Metric | Wert |
|--------|------|
| Events | ~8-9 in last run |
| Sources | 3 (stagnation_detector, evolver, unknown) |
| Subscribers | variiert |

---

## 4.2 EVENT BUS ARCHITECTUR

```
┌─────────────────────────────────────────────────────────────┐
│                        EVENT BUS                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PUBLISHERS (Sources)                                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │ Learning    │ │ Stagnation │ │ Evolver     │            │
│  │ Loop        │ │ Detector   │ │ Signal      │            │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘            │
│         │               │               │                    │
│         └───────────────┼───────────────┘                    │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────┐      │
│  │              EVENT BUS CENTRAL                    │      │
│  │  Type: system_event                               │      │
│  │  Format: JSON                                      │      │
│  └─────────────────────┬────────────────────────────┘      │
│                        │                                     │
│                        ▼                                     │
│  SUBSCRIBERS (Consumers)                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │ Evolver    │ │ KG Sync    │ │ Monitoring  │            │
│  │ Signal     │ │            │ │            │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4.3 SCRIPT

### Haupt-Script

```bash
python3 /workspace/scripts/event_bus.py
```

### Commands

```bash
# Stats
python3 /workspace/scripts/event_bus.py stats

# List events
python3 /workspace/scripts/event_bus.py list --type kg_update

# Publish event
python3 /workspace/scripts/event_bus.py publish --type test --source test

# Publish heartbeat
python3 /workspace/scripts/event_bus.py publish --type system_heartbeat --source test --severity info
```

---

## 4.4 EVENT FORMAT

### Event Structure

```json
{
  "event": {
    "id": "uuid",
    "type": "system_event",
    "source": "learning_loop",
    "timestamp": "2026-04-17T06:00:00Z",
    "data": {
      "metric": "value"
    }
  }
}
```

### Event Types

| Type | Beschreibung | Typische Source |
|------|-------------|-----------------|
| `kg_update` | KG wurde aktualisiert | kg_sync |
| `learning_signal` | Learning Loop Signal | learning_loop |
| `stagnation_detected` | Stagnation erkannt | stagnation_detector |
| `system_heartbeat` | System Heartbeat | various |
| `evolution_signal` | Evolver Signal | evolver_signal_bridge |
| `novelty_injected` | Novelty Injection | learning_loop |
| `validation_result` | Validierung Ergebnis | learning_loop |

### Severity Levels

| Level | Bedeutung |
|-------|----------|
| `debug` | Debug Info |
| `info` | Normale Info |
| `warning` | Warning |
| `error` | Error |
| `critical` | Kritisch |

---

## 4.5 INTEGRATION: EVENT BUS → OTHER SYSTEMS

### Event Bus → KG

Der KG wird bei relevanten Events aktualisiert:
```bash
python3 /workspace/scripts/learning_to_kg_sync.py --apply
```

### Event Bus → Evolver

```bash
python3 /workspace/scripts/evolver_signal_bridge.py
```

### Event Bus → Stagnation Detector

```bash
python3 /workspace/scripts/stagnation_detector.py --check all
```

---

## 4.6 STAGNATION DETECTION

### Script

```bash
python3 /workspace/scripts/stagnation_detector.py --check all
```

### Was es prüft

1. Learning Loop Score Trends
2. Gene Selection Diversity
3. Pattern Repetition
4. System-wide Stagnation

### Cron

```json
{
  "name": "Stagnation Detector",
  "schedule": "0 */6 * * *",
  "enabled": true,
  "failureAlert": {
    "after": 2,
    "channel": "telegram"
  }
}
```

---

## 4.7 EVOLVER SIGNAL BRIDGE

### Script

```bash
python3 /workspace/scripts/evolver_signal_bridge.py
```

### Was es tut

1. Liest Events vom Event Bus
2. Berechnet Evolver Strategie
3. Führt Evolver aus
4. Postet Results zurück

### Integration

```bash
# Smart Evolver mit Signal Bridge
bash /workspace/scripts/run_smart_evolver.sh
```

---

## 4.8 RECENT EVENTS (Beispiel)

```
Type: kg_update | Source: learning_loop | Count: ~5
Type: stagnation_detected | Source: stagnation_detector | Count: ~1
Type: system_heartbeat | Source: various | Count: ~2
```

---

## 4.9 BACKUP

Events werden geloggt in:
- `/workspace/logs/` (generell)
- Event-spezifische Logs in jeweiligen Scripts

---

## 4.10 BEKANNTE ISSUES

| Issue | Status | Notes |
|-------|--------|-------|
| Keine | ✅ | Event Bus funktioniert stabil |

---

*Modul 04 — Event Bus | Sir HazeClaw 🦞*
