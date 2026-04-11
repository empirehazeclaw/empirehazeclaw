# Subagent Spawning Best Practices

**Version:** 1.0.0  
**Created:** 2026-04-11

---

## Overview

Wie man Subagents richtig spawnt mit minimalen Fehlern.

---

## ✅ Best Practice Spawning

### 1. Timeout setzen

```python
sessions_spawn(
    runtime="subagent",
    mode="run",
    runTimeoutSeconds=600,  # 10 minutes statt default
    task="..."
)
```

### 2. Nur minimax als Fallback

```python
sessions_spawn(
    runtime="subagent",
    mode="run",
    model="minimax/MiniMax-M2.7",  # Explizit nur minimax
    task="..."
)
```

### 3. Health Check vorher

```python
# Script: subagent_health_check.py
# Prüft ob spawning möglich

if __name__ == "__main__":
    health = subprocess.run(['python3', 'subagent_health_check.py'])
    if health.returncode != 0:
        # Direkt ausführen statt subagent
        print("Spawning nicht empfohlen - direkt arbeiten")
```

---

## 🎯 Task Design Prinzipien

### Gut: Kleine, abgegrenzte Tasks

```python
# GUT - Kleiner Task
sessions_spawn(
    task="Lese file X und extrahiere Y",
    runTimeoutSeconds=120
)
```

### Schlecht: Alles in einen großen Task

```python
# SCHLECHT - Großer Task
sessions_spawn(
    task="Mache alles tief: 1. Lese X, 2. Lese Y, 3. Analysiere Z...",
    runTimeoutSeconds=600
)
```

---

## 🔧 Subagent Health Check Script

```bash
python3 /home/clawbot/.openclaw/workspace/scripts/subagent_health_check.py
```

Wenn ❌:
- Subagent spawning可能会失败
- Alternative: Task direkt ausführen

---

## 📋 Spawning Checklist

Vor jedem Subagent Spawn:

- [ ] Timeout auf 600s+ setzen (bei >5min tasks)
- [ ] model="minimax/MiniMax-M2.7" explizit setzen
- [ ] Task klar abgegrenzt (nicht "mach alles")
- [ ] Health Check wenn möglich
- [ ] Fallback: Task direkt ausführen wenn Subagent failt

---

## ⚠️ Known Issues

### Issue: "No API key for openrouter"
**Cause:** Subagent sucht openrouter falls minimax failt
**Fix:** `model="minimax/MiniMax-M2.7"` explizit setzen

### Issue: "LLM request timed out"
**Cause:** Task zu groß oder minimax überlastet
**Fix:** Timeout erhöhen, Task verkleinern

### Issue: "Auth store not found"
**Cause:** Subagent hat keine eigenen API Keys
**Fix:** Parent Session Keys werden vererbt - normalerweise OK

---

## 📁 Related Files

- `/home/clawbot/.openclaw/workspace/scripts/subagent_health_check.py` - Health Check Script

---

*Last Updated: 2026-04-11*
