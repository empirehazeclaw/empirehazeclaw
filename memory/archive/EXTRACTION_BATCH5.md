# Telegram Memory Extraction - Batch 5

**Extracted:** 2026-04-05  
**Files Processed:** 10  
**Total Messages:** 9,809

---

## Per-File Summary

| File | Messages | Decisions | Learnings | Facts | Tasks | Code | System | Discarded |
|------|----------|-----------|-----------|-------|-------|------|--------|-----------|
| messages22---9368de72 | 990 | 7 | 19 | 252 | 46 | 6 | 25 | 635 |
| messages22---e9ab1eba | 990 | 7 | 19 | 252 | 46 | 6 | 25 | 635 |
| messages23---92e878ef | 976 | 7 | 6 | 142 | 63 | 9 | 10 | 739 |
| messages23---f96c63b3 | 976 | 7 | 6 | 142 | 63 | 9 | 10 | 739 |
| messages24---7532f73c | 955 | 10 | 18 | 98 | 77 | 13 | 124 | 615 |
| messages24---96f30125 | 955 | 10 | 18 | 98 | 77 | 13 | 124 | 615 |
| messages25---2dcba584 | 95 | 1 | 3 | 11 | 11 | 0 | 2 | 67 |
| messages25---f7fc7fef | 935 | 5 | 18 | 194 | 72 | 7 | 30 | 609 |
| messages26---8381ec42 | 960 | 4 | 15 | 249 | 28 | 7 | 7 | 650 |
| messages27---5c1853ee | 977 | 7 | 9 | 167 | 55 | 9 | 12 | 718 |

---

## Totals

| Category | Count |
|----------|-------|
| **Decisions** | 48 |
| **Learnings** | 96 |
| **Facts** | 1,113 |
| **Tasks** | 408 |
| **Code** | 50 |
| **System** | 210 |
| **Discarded** | 4,632 |
| **Processed (saved)** | 1,925 |

**Processing Rate:** 19.6% of messages contained actionable content

---

## Notes

- messages22 and messages23 files appear to be duplicates (same message count and stats)
- messages24 files show highest SYSTEM activity (124 events each) — active agent operations
- messages25---2dcba584 is significantly smaller (95 msgs) — likely a partial export
- messages26---8381ec42 has highest FACT density (249 facts) — configuration-heavy session

**Output written to:**
- `memory/decisions/` — 48 decision entries
- `memory/learnings/` — 96 learning entries
- `MEMORY.md` — 1,113 facts appended
- `todos/current.md` — 408 tasks added
