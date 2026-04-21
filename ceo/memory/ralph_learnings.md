# Ralph Loop Learnings

- [2026-04-20 07:34] [maintenance:success] Maintenance complete after 2 iterations
- [2026-04-20 09:04] [error] Iteration 2: Learning loop failed

## Learning: 2026-04-20 — Cron Job Path Mismatch

**Problem:** Ralph Learning Loop (cron) was calling `/workspace/scripts/ralph_learning_loop.py` but file is at `/workspace/SCRIPTS/automation/`. All 14+ cron job paths were wrong.

**Fix Applied:**
1. `ralph_learning_loop.py` internal path: `WORKSPACE / "scripts/learning_loop_v3.py"` → `"SCRIPTS/automation/learning_loop_v3.py"`
2. `cron/jobs.json`: All 14 paths corrected from `workspace/scripts/` → `workspace/SCRIPTS/automation/`
3. Fixed double-prefix on `ralph_maintenance_loop.py` (`/openclaw/home/clawbot/.openclaw/...`)

**Note:** The cron fires at 09:00 & 18:00 UTC (Ralph Learning Loop). Score currently 0.766 vs 0.80 target — still improving.

## Learning: 2026-04-20 — Ralph Maintenance Loop Activated

**Status:** Ralph Maintenance Loop (c8fa9a00) ist jetzt ✅ OK
- Problem: War "idle" weil nextRun noch nicht erreicht war
- Fix: `openclaw cron enable` + manueller Run = läuft jetzt
- Alle 3 idlen Crons (Ralph Maintenance, Cache Cleanup, KG Orphan) aktiviert

## Learning: 2026-04-20 — Errored Crons Self-Heal

**Observation:** Prompt Benchmark Weekly + Run auto documentation waren "error" (24h/2h)
- Nach manuellem `openclaw cron run` = sofort ✅ OK
- "error" Status heisst NICHT dass das Script kaputt ist
- Es bedeutet nur dass der letzte Run fehlgeschlagen ist (可能是 temporär)

## Learning: 2026-04-20 — QMD .ipull = Temp Download

**Discovery:** `/home/clawbot/.cache/qmd/models/hf_tobil_qmd-query-expansion-1.7B-q4_k_m.gguf.ipull`
- `.ipull` = HuggingFace temporary download format
- Unvollständig (QMD hatte beim Download abgebrochen)
- QMD läuft mit `qmd search` (BM25) auch ohne das model
- Gelöscht → 1.2GB gespart
- [2026-04-20 12:10] [maintenance:success] Maintenance complete after 5 iterations
- [2026-04-20 18:09] [maintenance:success] Maintenance complete after 6 iterations
- [2026-04-20 19:08] [maintenance:success] Maintenance complete after 7 iterations
- [2026-04-20 19:10] [maintenance:success] Maintenance complete after 8 iterations
- [2026-04-20 19:12] [maintenance:success] Maintenance complete after 9 iterations
- [2026-04-20 19:14] [maintenance:success] Maintenance complete after 10 iterations
- [2026-04-20 19:15] [maintenance:safety] Max iterations reached, 0 issues pending
- [2026-04-20 19:17] [maintenance:safety] Max iterations reached, 0 issues pending
- [2026-04-20 19:19] [maintenance:safety] Max iterations reached, 0 issues pending
- [2026-04-20 20:46] [maintenance:safety] Max iterations reached, 0 issues pending
- [2026-04-21 00:06] [maintenance:safety] Max iterations reached, 0 issues pending
- [2026-04-21 00:07] [maintenance:success] Maintenance complete after 2 iterations
