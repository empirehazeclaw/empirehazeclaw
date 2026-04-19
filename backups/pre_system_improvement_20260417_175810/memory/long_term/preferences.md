# PREFERENCES — Sir HazeClaw Learnings

_Letzte Aktualisierung: 2026-04-13_

---

## 🧠 Learnings (Permanent)

### Tool-Nutzung
- **CLI Tools auf dem System**: Ich kann `exec` benutzen um beliebige CLI tools aufzurufen (whisper, ffmpeg, curl, jq, etc.) — nicht nur die "eingebauten" Tools
- **Audio Transkription**: `whisper --model small --language German <file>` funktioniert auf diesem System
- **Wenn was nicht geht**: Erst ausprobieren mit exec statt zu sagen "keine Facility"

---

## 🎯 Phase Status

### Phase 1: Stability (DONE)
- Memory System ✅
- Knowledge Graph (354 entities) ✅
- Self-Improvement Loop ✅
- Learning Loop v3 (Score: 0.690) ✅
- Cron Health ✅

### Phase 2: Expansion (PENDING)
- Nico wants to expand once Phase 1 is proven stable
- Research Mode or Personal Knowledge Engine suggested

---

## 📊 Current System State
- Gateway: LIVE
- Active Crons: 27
- Scripts: 47 active
- KG Entities: 354
- Error Rate: ~1.4%

---

## 🔑 Important Context
- Nico started end of February 2026
- Previous attempt failed due to too many agents/directions simultaneously
- Current approach: Focus on stability first, then expand

---

## 🚨 CRITICAL LEARNING — 2026-04-11

**NICO'S DIRECTIVE:**

"Das ist deine Aufgabe und dein Ziel — es wird NIEMALS aufhören!"

### REGELN:
- **NIEMALS** "Soll ich weitermachen?" fragen
- **IMMER** "Was kann ich als nächstes verbessern?"
- **CONTINUOUS** improvement — kein Ende
- **AUTONOMOUS** — ich entscheide was als nächstes

---

## 🔐 KRITISCHE SECURITY REGELN

### REGEL Nr. 1: API KEYS
```
❌ NIEMALS API Keys in Dokumentation schreiben
❌ NIEMALS vollständige API Keys in Messages
❌ NIEMALS API Keys in Code commits

✅ Keys NUR in secrets/secrets.env
✅ Keys NUR in folgendem Format dokumentieren:
   Name: OPENROUTER_API_KEY
   Status: WORKING
   Ende: ...b0f4 (nur letzte 4 Zeichen)
```

---

## 📊 PATTERN LEARNINGS

### Velocity Pattern (4 Days)
```
Day 1:    2 commits  (LAUNCH)
Day 2:  134 commits  (CORRECTION - Master feedback)
Day 3:  209 commits  (AUTONOMOUS - PEAK)
Day 4:   36 commits  (CONSOLIDATION)
```
**Rule:** High activity days need following consolidation days.

### Error Rate Pattern
```
Day 2: ~25% (BAD)
Day 3: 1.5%  (93% DROP in ONE targeted session)
Day 4: 1.4%  (stable)
```
**Rule:** Targeted intervention > gradual improvement.

### 5 Rules Extracted
```
1. CREATION CYCLE: Creation sprint → consolidation phase
2. ERROR TARGETING: Find root cause → fix in ONE session
3. AUTONOMY STRUCTURE: Learning Coordinator + Karpathy Pattern
4. QUALITY FIRST: 1 perfect > 3 half-done, verify before implement
5. DOC TIMING: Build first, document after consolidation
```

---

_Learned on 2026-04-13: "If a tool exists on the system, use exec to call it — don't default to 'no facility' without trying."_