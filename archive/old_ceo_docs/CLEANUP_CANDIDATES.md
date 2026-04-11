# Cleanup Candidates - 2026-04-10

## Dead Scripts (0 references, >7 days old)

| Script | Size | Last Modified | Action |
|--------|------|---------------|--------|
| whisper_daemon.py | 8.0K | 2026-03-29 | Candidate |
| humanize_content.py | 12K | 2026-03-28 | Candidate |
| whisper_server.py | 8.0K | 2026-03-29 | Candidate |
| feature_router.py | 8.0K | 2026-03-28 | Candidate |
| transcribe.py | 8.0K | 2026-03-29 | Candidate |

**Total potential savings:** ~44KB

## OpenRouter Issue (Known Limitation)

- OpenRouter free models require API key
- Current fallback chain is non-functional
- Primary model (MiniMax) works fine
- **Recommendation:** Document as "known limitation" not "blocker"

## Knowledge Graph

- Was: 15 nodes, 0 edges
- Now: 15 nodes, 17 edges ✅
- **Needs:** More nodes for patterns, learnings

## Disk Space

- Freed: 3.3GB from pip cache
- Current: ~70GB free (28% used)

---

*Created: 2026-04-10 21:26 UTC*
*Status: Pending Master Approval for deletions*