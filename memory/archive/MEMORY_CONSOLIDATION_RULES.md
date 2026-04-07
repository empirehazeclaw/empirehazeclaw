# MEMORY_CONSOLIDATION_RULES.md
*Created: 2026-03-28*
*Purpose: Define where different types of knowledge live*

---

## 🏗️ UNIFIED KNOWLEDGE HIERARCHY

```
knowledge/          → RAG vector store (permanent facts, 288 sources)
SYSTEM_CORE.md      → Current state (TODOs, priorities, what's UP/DOWN)
MEMORY.md           → Curated long-term (Nico facts, business, tools)
MASTER_MEMORY.md    → Quick reference (P1/P2/P3 priorities)
learnings/          → Lessons learned (what worked / what didn't)
memory/YYYY-MM-DD.md → Daily raw logs (auto-delete after 30 days)
memory/decisions/   → Important decisions (permanent until superseded)
memory/projects/    → Project tracking
```

---

## 📍 WHAT GOES WHERE

### 🧠 MEMORY.md (Curated Long-Term)
**When to update:** When facts about Nico or the business change permanently

**Contains:**
- Nico's profile (name, Telegram, email, background)
- Business model and products (permanent)
- Domain list and purposes
- API keys and credentials (status only)
- Key tools and their status
- Important URLs and links

**Do NOT put here:**
- Daily activity logs
- Temporary states
- One-off decisions
- TODOs or priorities

---

### ⚡ SYSTEM_CORE.md (Dynamic State)
**When to update:** Every session or when system state changes

**Contains:**
- Current system status (what's UP/DOWN right now)
- Active agents and their status
- Today's priorities
- Open issues and blockers
- Last heartbeat times
- Current TODOs for today
- Quick reference for fresh agents

**Update triggers:**
- Service goes down/up
- New agent spawned
- Daily at start of each session
- After any significant state change

---

### 📚 /knowledge/ (RAG Vector Store)
**When to update:** When permanent factual knowledge is learned

**Contains:**
- Scraped website content
- Research findings
- Product documentation
- API documentation
- Competitive analysis
- SEO content
- Technical docs

**How to add:**
```bash
# Add document to knowledge base
python3 memory/knowledge_graph.py --add "source_file.txt" --category "research"
```

---

### 📅 memory/YYYY-MM-DD.md (Daily Logs)
**When to create:** Automatically each day, or manually when significant events happen

**Contains:**
- Raw session notes
- What was accomplished today
- Problems encountered
- Quick learnings
- Activity logs

**Auto-cleanup:** DELETE files older than 30 days
```bash
# Cleanup old daily logs (run weekly)
find memory/ -name "????-??-??.md" -mtime +30 -delete
```

---

### 🎓 learnings/ (Lessons Learned)
**When to update:** After any significant success or failure

**Contains:**
- What worked (and should be repeated)
- What failed (and should be avoided)
- Process improvements
- Tool discoveries

**Format:**
```markdown
## YYYY-MM-DD
- [SUCCESS] Resend free tier: 5 emails/day limit
- [FAIL] Tavily search failed without API key
- [LEARNED] GOG CLI better than direct Gmail API
```

---

### ✅ memory/decisions/ (Decision Log)
**When to update:** When a significant decision is made

**Contains:**
- Strategic decisions
- Tool/technology choices
- Business pivots
- Priority changes

**Format:**
```markdown
# Decision: [TITLE]
Date: YYYY-MM-DD
Context: Why this was needed
Decision: What was decided
Rationale: Why this choice
Supersedes: [link to previous decision if applicable]
```

---

## 🔄 UPDATE FREQUENCY RULES

| File | Update Frequency | Trigger |
|------|-----------------|---------|
| MEMORY.md | Weekly or on change | New permanent fact about Nico/business |
| SYSTEM_CORE.md | Every session | Start of session + state changes |
| memory/YYYY-MM-DD.md | Daily | End of day or significant event |
| learnings/ | After results | Success or failure of initiative |
| memory/decisions/ | On decision | Strategic choice made |
| /knowledge/ | As needed | New permanent information discovered |

---

## 🚫 DON'TS

1. **Don't duplicate** - If it's in MEMORY.md, don't add to MASTER_MEMORY.md
2. **Don't put TODOs in MEMORY.md** - That's SYSTEM_CORE.md's job
3. **Don't put daily logs in MEMORY.md** - Use memory/YYYY-MM-DD.md
4. **Don't keep secrets/credentials in plain text** - Use encrypted storage or environment variables
5. **Don't overwrite without reading** - Always read first

---

## 🧹 AUTO-CLEANUP POLICY

### Daily Logs (memory/YYYY-MM-DD.md)
```bash
# Files older than 30 days → DELETE
find memory/ -maxdepth 1 -name "????-??-??.md" -mtime +30 -delete
```

### Knowledge (RAG)
- Review quarterly
- Remove outdated sources
- Update stale content

### Learnings
- Keep forever (lessons don't expire)
- Merge duplicates monthly

### Decisions
- Keep but mark as "SUPERSEDED" when changed
- Archive superseded decisions

---

## 🔍 MEMORY SEARCH ORDER

When a question is asked:

1. **Check SYSTEM_CORE.md** → Is this about current state?
2. **Check MEMORY.md** → Is this a permanent fact about Nico/business?
3. **Check MASTER_MEMORY.md** → Is this a P1/P2/P3 priority or quick reference?
4. **Search /knowledge/** → Is this research/factual knowledge?
5. **Check learnings/** → Is this a lesson learned?
6. **Check today's log** → Is this recent activity?

---

## 📝 NAMING CONVENTIONS

### Daily Logs
```
memory/YYYY-MM-DD.md
Example: memory/2026-03-28.md
```

### Learnings
```
learnings/YYYY-MM-DD-TOPIC.md
Example: learnings/2026-03-28-outreach-failures.md
```

### Decisions
```
memory/decisions/YYYY-MM-DD-SHORT-DESCRIPTION.md
Example: memory/decisions/2026-03-28-email-provider-change.md
```

### Projects
```
memory/projects/PROJECT-NAME.md
Example: memory/projects/tiktok-launch.md
```

---

## ⚡ MANDATORY RULES SUMMARY

| Rule | Action |
|------|--------|
| Before answering facts | Check MEMORY.md first |
| Start of session | Update SYSTEM_CORE.md |
| After decision | Save to memory/decisions/ |
| After success/failure | Add to learnings/ |
| Daily | Auto-sync to memory/YYYY-MM-DD.md |
| Weekly | Run 30-day cleanup for old logs |
| Quarterly | Review and prune /knowledge/ |

---

*These rules ensure: fast answers from correct source, no duplication, automatic cleanup of ephemeral data, permanent storage of valuable knowledge*
