# 💾 SESSION MEMORY / MEMORY FLUSH

**Type:** OpenClaw Hook (automatic session persistence)
**Status:** ✅ CONFIGURED
**Session Memory Path:** `/workspace/memory/sessions/`

---

## 🎯 WHAT IS SESSION MEMORY?

Session Memory is OpenClaw's **automatic mechanism** to persist session context when compaction triggers. It ensures that important context from sessions isn't lost during compaction cycles.

---

## ⚙️ CONFIGURATION

### OpenClaw Config (`~/.openclaw/openclaw.json`)
```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "session-memory": {
          "enabled": true,
          "persist": true,
          "path": "memory/sessions/"
        }
      }
    }
  },
  "compaction": {
    "mode": "safeguard"
  }
}
```

### Compaction Modes
| Mode | Behavior |
|------|----------|
| `safeguard` (default) | Auto-flush when context approaches limit |
| `never` | Disable compaction |
| `always` | Compact aggressively |

---

## 📁 DIRECTORY STRUCTURE

```
workspace/
└── memory/
    └── sessions/
        └── [session dumps - JSON files]
```

**Location:** `/home/clawbot/.openclaw/workspace/memory/sessions/`
**Created:** 2026-04-12 (manually, was auto-created on first use)

---

## 🔄 HOW IT WORKS

```
1. Session Active
   ↓ (conversational context builds up)
2. Context approaches limit (~180k tokens)
   ↓
3. Compaction triggered (safeguard mode)
   ↓
4. Session memory hook activates
   ↓
5. Key context → memory/sessions/[session_id].json
   ↓
6. Session continues with compacted context
   ↓
7. On session end/load: memory restored from sessions/
```

---

## 📊 CURRENT STATUS

| Metric | Value |
|--------|-------|
| Directory | `/workspace/memory/sessions/` |
| Files | None yet (new installation) |
| Last Created | 2026-04-12 06:57 UTC |
| Hook Status | ✅ Enabled |

---

## 🛠️ MANUAL COMMANDS

### Force Compaction
```bash
# Via OpenClaw CLI
openclaw session compact
```

### List Sessions
```bash
ls -la memory/sessions/
```

### Clear Old Sessions
```bash
# Remove sessions older than 30 days
find memory/sessions/ -name "*.json" -mtime +30 -delete
```

---

## 🔗 INTEGRATION POINTS

| System | Integration |
|--------|-------------|
| OpenClaw Gateway | Automatic via hook |
| memory-core plugin | Shares memory/ directory |
| KG (Knowledge Graph) | Different purpose (long-term vs short-term) |

---

## 📝 ROLES IN MEMORY ARCHITECTURE

Session Memory is **short-term** like a scratchpad:

| Memory Type | Duration | Location | Purpose |
|------------|----------|----------|---------|
| **Session Memory** | Current session | memory/sessions/ | Scratchpad |
| **Core Memory** | Until compacted | RAM | Active context |
| **File Memory** | Until deleted | memory/*.md | Daily logs |
| **KG Memory** | Permanent | knowledge_graph.json | Learnings |
| **SQLite Memory** | Semi-permanent | ~/.openclaw/memory/ | Vector search |

---

## ⚠️ NOTES

- Session memory files are **JSON** (machine-readable)
- They contain **compacted session context**
- NOT the same as daily notes (`memory/YYYY-MM-DD.md`)
- Designed for **recovery after compaction**, not for long-term storage

---

*Letztes Update: 2026-04-12 06:57 UTC*
*Session Memory — Configured and Ready*
