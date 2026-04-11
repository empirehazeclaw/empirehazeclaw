# 📋 SIR HAZECLAW — TODO LIST
## Structured Improvement Plan v2
**Created:** 2026-04-11 21:32 UTC
**Priority:** HIGH

---

## 🎯 PILLAR 3: SELF-HEALING ARCHITECTURE (START NOW!)

### Phase 1: Fix cron_error_healer.py ✅ DONE v2
- [x] Enable real healing execution (not "Would")
- [x] Add Verify phase (闭环 - closed loop)
- [x] Add Circuit Breaker pattern
- [x] Test on non-critical cron first

### Phase 2: Error Action Matrix
- [ ] Map our errors to 7 categories
- [ ] Implement exponential backoff for timeouts
- [ ] Add path verification for permission errors
- [ ] Add rate limiting for Telegram API

### Phase 3: 4-Stage Loop
- [ ] Integrate Detect → Diagnose → Heal → Verify
- [ ] Add cascade failure prevention
- [ ] Add graceful degradation

---

## 📋 PILAR 1: SCRIPT CONSOLIDATION

### Immediate ✅ DONE
- [x] Create scripts/README_ORGANIZATION.md
- [x] Identify scripts for archive

### This Week
- [ ] Consolidate health_check scripts (4 → 1)
- [ ] Consolidate error_analysis scripts (3 → 1)
- [ ] Consolidate metrics scripts (3 → 1)
- [ ] Archive 14 unused scripts
- [ ] Physical moves only after reference check

---

## 📋 PILAR 2: TEST COVERAGE

- [ ] Create test_core_scripts.py
- [ ] Add tests for MEMORY_API.py
- [ ] Add tests for memory_cleanup.py
- [ ] Add tests for cron_error_healer.py (especially execution!)
- [ ] Target: 100+ tests

---

## 📋 PILAR 4: KG QUALITY

### 🚨 CRITICAL PROBLEMS FOUND:
- [x] **access_count = 0** — KG wird NIE für Retrieval verwendet!
- [x] **4405/4659 (95%)** Relations sind `shares_category` → Category Spam
- [x] **93 entities** auto-extracted ohne klare Quelle

### Phase 1: KG Integration in Retrieval
- [ ] Integrate KG in memory_hybrid_search.py
- [ ] Add KG access_count tracking
- [ ] Test KG retrieval

### Phase 2: Relation Quality
- [ ] Stop excessive shares_category generation
- [ ] Add semantic relation types (causes, enables, prevents)
- [ ] Remove duplicate/transitive relations

### Phase 3: Usage Tracking
- [ ] Track KG queries
- [ ] Log KG hit rate
- [ ] Identify most useful entity types

---

## 📋 PILAR 5: SKILLS INTEGRATION

- [ ] Audit all 18 skills
- [ ] Create skills/INDEX.md
- [ ] Archive unused skills
- [ ] Document active skills

---

## 📋 PILAR 6: DASHBOARD

- [ ] Create mission_control.py
- [ ] Show: Error Rate, KG, Cron Health, Learning Loop
- [ ] Make Telegram-friendly

---

## 📊 METRICS TRACKING

| Metric | Before | Target | Status |
|--------|--------|--------|--------|
| Error Recovery | "Would" | REAL | 🔴 |
| Healing Verification | ❌ | ✅ | 🔴 |
| Circuit Breaker | ❌ | ✅ | 🔴 |
| Test Coverage | 52 | 100+ | ⚠️ |
| Scripts | 83 | ~40 | ⚠️ |
| KG Quality | Unknown | Scored | ⚠️ |

---

*Last Updated: 2026-04-11 21:32 UTC*
*Plan: STRUCTURED_IMPROVEMENT_PLAN.md*
