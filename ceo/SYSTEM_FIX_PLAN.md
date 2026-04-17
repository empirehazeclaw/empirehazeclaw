# 🔧 System Fix Plan — 2026-04-17 20:54 UTC

## Prioritized Actions

### P1: Gateway Memory (CRITICAL)
**Problem:** Gateway 1.8 GB RSS (normal: 100-200 MB)
**Action:** Restart gateway
**Command:** openclaw gateway restart
**Risk:** Medium (brief downtime)
**Expected:** Memory drops to ~100-200 MB

### P1: KG Entity IDs (CRITICAL)
**Problem:** 194 entities without `id` field in entity objects
**Status:** Dict-key pattern - entities keyed by name, but internal `.id` missing
**Action:** Add `id` field to entities (copy key as id)
**Script:** kg_fix_ids.py (create + run)
**Risk:** Low (additive change)

### P2: Evolver Solidify State (CRITICAL)
**Problem:** last_solidify=null but we did 28 solidifies yesterday
**Action:** Verify actual solidify state from memory_graph, update state file
**Script:** fix_evolver_state.py (create + run)
**Risk:** Low

### P2: Event Bus Stale (HIGH)
**Problem:** No events since April 15
**Action:** Check event_bus.py location and publisher
**Command:** python3 /home/clawbot/.openclaw/workspace/scripts/event_bus.py stats

### P3: Backup Bloat (HIGH)
**Problem:** 11 GB backups
**Action:** Delete old phase backups (keep recent 2)
**Cmd:** rm -rf backups/phase4_* backups/phase5_*
**Risk:** Low (backups are obsolete)

### P3: Signal Flow Inactive (HIGH)
**Problem:** Only 1 signal tracked in signal_feedback.json
**Action:** Run signal_bridge.py --inject to verify injection
**Command:** python3 /home/clawbot/.openclaw/workspace/ceo/scripts/signal_bridge.py --inject

### P4: Idle Crons (MED)
**Problem:** 4 crons never run (Mad-Dog, KG Auto-Prune, etc.)
**Action:** Check cron schedule alignment
**Command:** openclaw cron list

---

## Execution Order
1. Gateway Restart (P1 - CRITICAL memory)
2. KG ID Fix (P1 - data quality)
3. Evolver State Fix (P2)
4. Event Bus Check (P2)
5. Backup Cleanup (P3)
6. Signal Injection (P3)
7. Cron Check (P4)