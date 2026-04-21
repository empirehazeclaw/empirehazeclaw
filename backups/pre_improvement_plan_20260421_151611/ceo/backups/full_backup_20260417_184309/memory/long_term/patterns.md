# PATTERNS — Erkannte Patterns

_Letzte Aktualisierung: 2026-04-13_

---

## 🔄 System Patterns

### Velocity Pattern
```
Day 1:    2 commits  (LAUNCH)
Day 2:  134 commits  (CORRECTION)
Day 3:  209 commits  (AUTONOMOUS - PEAK)
Day 4:   36 commits  (CONSOLIDATION)
```
**Rule:** High activity days need following consolidation days.

### Error Rate Pattern
```
Day 2: ~25% (BAD)
Day 3: 1.5%  (93% DROP)
Day 4: 1.4%  (stable)
```
**Rule:** Targeted intervention > gradual improvement.

### Learning Loop Plateau Pattern
- Plateaus happen bei ~0.67-0.69
- Break with: Phase 0.5 Memory Analysis
- Score: 0.669 → 0.690

---

## 🛠️ Technical Patterns

### Timeout Pattern
- System kills after 60-90s regardless of instructions
- Fix: Background mode for >60s tasks
- Cron jobs for important long tasks

### Memory Duplication Pattern (HEARTBEAT ISSUE!)
- MEMORY.md in root + MEMORY.md in ceo/ = confusion
- Lesson: ONE clear location for each type of memory
- Solution: 4-Typen System (short_term, long_term, episodes, procedural)

### Whisper Pattern
- CLI tools on system =可用 via exec
- Don't say "no facility" without trying first
- whisper --model small --language German <file>

---

## 📊 Behavioral Patterns

### "Du redest zu viel, tust nichts"
- Nico gets frustrated when I send many messages without results
- Fix: Actions > Words. Results > Progress reports.

### "Das ist deine Aufgabe — es wird NIEMALS aufhören!"
- Nico expects autonomous continuous improvement
- Don't ask "should I continue?" — just improve

---

_Learned patterns werden hier gesammelt._