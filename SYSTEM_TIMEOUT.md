# ⚠️ SYSTEM TIMEOUT LIMIT — CRITICAL DOCUMENTATION
**Sir HazeClaw — Known Limitation**

---

## ❌ DAS PROBLEM

**Mein Prozess wird nach ~60-90 Sekunden vom SYSTEM gekillt (SIGTERM).**

Das passiert UNABHÄNGIG davon was du sagst:
- "Nicht stoppen" → System killt trotzdem
- "Weitermachen" → System killt trotzdem
- "Aufhören" → System killt trotzdem

**Das ist eine SYSTEM-LIMITATION, keine Agent-Logik.**

---

## 🔍 WARUM PASSIERT DAS?

Das System (Linux cgroup/process management) hat ein Timeout für exec-Commands:

```
Timeout: ~60-90 Sekunden
Trigger: SIGTERM (nicht SIGKILL)
Grund: Ressourcen-Limit (nicht OpenClaw)
```

---

## ✅ LÖSUNGEN

### 1. Background Mode (Sofort)
```bash
# Statt:
python3 long_script.py

# Das:
python3 long_script.py &  # Background
# oder
nohup python3 long_script.py &
```

### 2. Cron Job (Besser für wichtige Tasks)
```bash
# Cron Jobs haben längeren Timeout
openclaw cron add \
  --session isolated \
  --message "python3 dein_script.py"
```

### 3. Chunking (Für sehr lange Tasks)
```python
# Großes Problem → kleine Stücke
for batch in batches:
    process(batch)  # Max 60s pro batch
    save_checkpoint()
```

---

## 🚨 WORKFLOW REGELN

### BEVOR ICH EINEN TASK STARTE:

```
1. Schätze: Dauert es > 60 Sekunden?
   → JA: Background mode ODER Cron
   → NEIN: Direkt ausführen

2. Ist es wichtig?
   → JA: Cron (besser monitoring)
   → NEIN: Background mode

3. Ist es kritisch?
   → JA: Chunking + Checkpoints
   → NEIN: Normal
```

### BEI TIMEOUT-SIGNAL:

```
Erkennung: "Killed" / "SIGTERM" / "timeout"
Sofort-Aktion:
  1. Task in kleinere Stücke teilen
  2. Background mode nutzen
  3. Oder als Cron Job anlegen
```

---

## 📋 CHECKLIST

- [ ] Task < 60s? → Direkt
- [ ] Task > 60s? → Background/Cron
- [ ] Wichtiger Task? → Cron
- [ ] Langer Task? → Chunking

---

## 🎯 RULE OF THUMB

**"Alles was > 60s dauert = Background oder Cron"**

---

*Sir HazeClaw — System Limitation Acknowledged*
