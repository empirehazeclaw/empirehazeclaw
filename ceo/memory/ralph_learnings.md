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
