# 📋 EVOLVER IMPROVEMENT TODO — 2026-04-11
**Quelle:** Capability Evolver Report 2026-04-11

---

## 🚨 PRIORITY 1: Blast Radius Control (CRITICAL)

**Problem:** 4.4x drift (88 files actual vs 20 estimated)

### Tasks:
- [ ] Create blast_radius_estimator.py
- [ ] Track estimated vs actual for all changes
- [ ] Calculate accuracy ratio per evolution
- [ ] Alert if drift > 2x
- [ ] Retrain estimation model if accuracy < 70%

---

## 🚨 PRIORITY 2: Gene Diversity (HIGH)

**Problem:** gene_gep_repair_from_errors selected 4x+ times (stagnation)

### Tasks:
- [ ] Log gene usage per evolution
- [ ] Track gene selection history
- [ ] Force different gene if same selected 3x+
- [ ] Add "try different gene" rule to evolver
- [ ] Research new genes to diversify pool

---

## 🚨 PRIORITY 3: Evolution Stagnation (HIGH)

**Problem:** stable_success_plateau detected, no progress

### Tasks:
- [ ] Implement innovation trigger at stagnation
- [ ] Create "force innovation" mode
- [ ] Add gene shuffling when stuck
- [ ] Track innovation score per evolution
- [ ] Set target: 3+ new approaches per week

---

## 📊 PRIORITY 4: Performance Dashboard

**Problem:** No historical data for analysis

### Tasks:
- [x] Create performance_dashboard.py ✅
- [ ] Log first 10 evolutions
- [ ] Calculate baseline metrics
- [ ] Set target thresholds
- [ ] Add stagnation detection

---

## 📋 PRIORITY 5: Code Stats Integration

**Problem:** No visibility into repo complexity

### Tasks:
- [x] Create code_stats.py ✅
- [x] Create code_stats.md skill ✅
- [ ] Run weekly complexity analysis
- [ ] Track complexity over time
- [ ] Alert on sudden complexity spikes

---

## 📝 PRIORITY 6: Todo Manager

**Problem:** TODOs in code are forgotten

### Tasks:
- [x] Create todo_manager.md skill ✅
- [ ] Create todo_manager.py script
- [ ] Run TODO extraction
- [ ] Create actionable task list
- [ ] Track TODO completion rate

---

## 🎯 SUCCESS METRICS

| Metric | Current | Target | Deadline |
|--------|---------|--------|----------|
| Blast Radius Accuracy | 4.4x drift | <1.5x | 1 week |
| Gene Diversity | 1 gene | 5+ genes | 1 week |
| Innovation Score | 0 | Growing | 2 weeks |
| Success Rate | 0% | >70% | 2 weeks |
| Evolution Count | 0 logged | 10 logged | 1 week |

---

## 📅 DAILY CHECKLIST

- [ ] Run code_stats.py
- [ ] Check performance_dashboard.py --check
- [ ] Log evolution result
- [ ] Review gene usage
- [ ] Detect stagnation signals

---

*Created: 2026-04-11 16:27 UTC*
*Sir HazeClaw — Autonomous Improver 🚀*
