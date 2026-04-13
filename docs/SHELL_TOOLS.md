# 🛠️ Shell Tools — Sir HazeClaw

**Location:** `SCRIPTS/tools/*.sh`
**Status:** Active + Cron-managed

---

## 📦 github_backup.sh

**Purpose:** Auto-commits and pushes workspace changes to GitHub daily.

**Schedule:** `0 23 * * *` (Daily at 23:00 UTC)

**Usage:**
```bash
bash /home/clawbot/.openclaw/workspace/SCRIPTS/tools/github_backup.sh
```

**What it does:**
1. Finds all changed files in workspace
2. Excludes: `.git/`, `archive/`, `node_modules/`, `*.sqlite`, `logs/`, `secrets/`
3. Auto-commits with timestamp
4. Pushes to `origin`

**Log:** `/home/clawbot/.openclaw/workspace/logs/github_backup.log`

**Exit codes:**
- `0` = No changes to commit (✅)
- `1` = Changes committed and pushed (✅)
- `2` = Not a git repository (❌)

---

## 🗄️ sqlite_vacuum.sh

**Purpose:** Weekly SQLite VACUUM + ANALYZE for all OpenClaw memory databases.

**Schedule:** `0 4 * * 0` (Weekly Sunday 04:00 UTC)

**Usage:**
```bash
bash /home/clawbot/.openclaw/workspace/SCRIPTS/tools/sqlite_vacuum.sh
```

**What it does:**
1. Iterates all `*.sqlite` files in `/home/clawbot/.openclaw/memory/`
2. Runs `VACUUM` + `ANALYZE` on each
3. Reports size before/after and bytes saved

**Sample output:**
```
Mon Apr 13 07:23:10 UTC 2026 /home/clawbot/.openclaw/memory/ceo.sqlite: 38477824B -> 38477824B (saved 0B)
```

**Log:** `/home/clawbot/.openclaw/workspace/logs/sqlite_vacuum.log`

**Why VACUUM?** SQLite doesn't automatically reclaim deleted page space. Regular VACUUM keeps databases fast and small.

---

## 🗑️ kill_day.sh

**Purpose:** Agent Consolidation Script — archives deprecated/unused agents.

**Schedule:** DISABLED by default (manual trigger only)

**Usage:**
```bash
# Dry run (preview what would be deleted)
bash /home/clawbot/.openclaw/workspace/SCRIPTS/tools/kill_day.sh --dry-run

# List all agents that would be killed
bash /home/clawbot/.openclaw/workspace/SCRIPTS/tools/kill_day.sh --list

# Execute deletion (requires confirmation)
bash /home/clawbot/.openclaw/workspace/SCRIPTS/tools/kill_day.sh --execute
```

**What it does:**
1. Moves agents to `/home/clawbot/.openclaw/workspace/archive/agents_backup/`
2. Archives entire subdirectories (e.g., `agriculture/`, `healthcare/`)
3. Requires typed confirmation `YES-DELETE` to execute

**Safety features:**
- `--dry-run` always runs first
- Backup location: `archive/agents_backup/`
- Confirmation required before any deletion
- Lists files found vs. not found

**Agents targeted:**
- Tiny stubs (<20 lines)
- Deprecated `*_llm.py` variants
- Infrastructure wrappers
- Vertical-specific agents (71+ agents)
- Duplicate/similar agents

**Log:** `/home/clawbot/.openclaw/workspace/logs/kill_day.log`

---

## 📊 Cron Jobs Summary

| Tool | Schedule | Cron ID | Status |
|------|----------|---------|--------|
| `github_backup.sh` | Daily 23:00 UTC | `55208aae-9e3a-41ec-93da-951a2e0b69a1` | ✅ Active |
| `sqlite_vacuum.sh` | Sun 04:00 UTC | `4d51210d-9f08-42dc-9032-5a424b99c4b9` | ✅ Active |
| `kill_day.sh` | Monthly (1st Sun, 03:00 UTC) | `822d0b84-ddd4-4531-87a1-e7eac5bfcbc8` | ❌ Disabled |

---

## 🚨 Troubleshooting

**github_backup.sh fails with "not a git repository":**
```bash
cd /home/clawbot/.openclaw/workspace && git init
git config user.email "clawbot@empirehazeclaw.com"
git config user.name "ClawBot"
```

**sqlite_vacuum.sh saves 0 bytes every time:**
- Normal if databases are already optimized
- VACUUM only reclaims space after significant deletes

**kill_day.sh "file not found":**
- Agent was already moved or doesn't exist
- Check `archive/agents_backup/` for previous runs

---

*Last updated: 2026-04-13 07:27 UTC*
