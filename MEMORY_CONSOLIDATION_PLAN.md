# 📋 CONSOLIDATION & OPTIMIZATION MASTER PLAN
## Memory Systems — Phase 2
**Generated:** 2026-04-11 21:08 UTC
**Status:** PLANNING

---

## 📊 PHASE 1: ANALYSIS (Current State)

### ✅ Systems Status (CORRECTED!)

| System | Location | Size | Entries | Status |
|--------|----------|------|---------|--------|
| Knowledge Graph | `core_ultralight/memory/` | 1.7MB | 209 entities, 4659 relations | ✅ Healthy |
| Semantic Index | `core_ultralight/memory/` | 460KB | **51 documents** | ✅ Populated |
| Master Index | `core_ultralight/memory/` | 9KB | **47 files** | ✅ Populated |
| Daily Notes | `memory/` | 388KB | 2 files + metrics | ✅ Active |
| CEO Memory | `ceo/memory/` | 468KB | 30+ files | ⚠️ Fragmented |
| Experience Bank | `ceo/experience_bank/` | 60KB | ~50 experiences | ⚠️ Underused |

### 🎯 Consolidation Goals

```
CURRENT STATE (6 systems):                    TARGET STATE (3 systems):
├── Knowledge Graph (1.7MB)                  ├── Knowledge Graph (UNIFIED)
├── Semantic Index (460KB)                   │     ├── Semantic Search
├── Master Index (9KB)                       │     ├── File Tracking
├── Daily Notes (388KB)                     │     └── Daily Notes
├── CEO Memory (468KB)                       ├── CEO Memory (CONSOLIDATED)
└── Experience Bank (60KB)                  └── Experience Bank (INTEGRATED)
```

---

## 📋 PHASE 2: STRUCTURE & CONSOLIDATE

### 2.1 Consolidate Daily Notes

**Problem:** Dual daily notes in two locations

**Action:**
```markdown
/workspace/memory/2026-04-11.md      ← KEEP (official daily)
/workspace/ceo/memory/2026-04-11.md  ← MERGE into above
```

**Merge Strategy:**
1. Read both files
2. Combine unique entries
3. Maintain chronological order
4. Archive merged file with original name

### 2.2 Consolidate CEO Memory

**Problem:** 30+ files, no structure

**Target Structure:**
```
/workspace/ceo/memory/
├── daily/                 # Daily session logs (consolidated)
│   ├── 2026-04-11.md
│   └── ...
├── learnings/            # Extracted learnings (ALREADY EXISTS)
├── projects/             # Project-specific memories
│   ├── evolver/
│   ├── heartbeat/
│   └── capability/
├── .dreams/              # Short-term recall (ALREADY EXISTS)
└── INDEX.md              # Master index for CEO memory
```

### 2.3 Integrate Experience Bank

**Problem:** Underused, separate from main memory flow

**Action:**
1. Move experience extraction into daily cleanup
2. Add experiences to Knowledge Graph automatically
3. Create `EXPERIENCE_BANK.md` as searchable KG category

---

## ⚡ PHASE 3: OPTIMIZE

### 3.1 Knowledge Graph Optimization

**Current Issues:**
- Large file (1.7MB) - slow to load
- Some orphaned entities (40 found + removed)

**Optimizations:**
```python
# 1. Chunk large entities
CHUNK_SIZE = 1000  # Max entities per chunk

# 2. Add lazy loading
def load_kg(chunk_id=None):
    if chunk_id:
        return load_chunk(chunk_id)
    return load_full_kg()

# 3. Add caching
KG_CACHE_TTL = 3600  # 1 hour
```

### 3.2 Search Optimization

**Current:** Hybrid search loads entire semantic index (460KB)

**Optimizations:**
1. Pre-filter by category before embedding search
2. Add category-specific indexes
3. Implement result caching

### 3.3 Memory Cleanup Optimization

**Current:** Cleanup runs on-demand

**Improvements:**
1. Add incremental cleanup (only changed files)
2. Add cleanup cron (weekly)
3. Add cleanup reporting to HEARTBEAT

---

## 📚 PHASE 4: DOCUMENT & IMPLEMENT

### 4.1 Documentation

**Create:**
```
/workspace/docs/
├── MEMORY_ARCHITECTURE.md     # System overview
├── MEMORY_PIPELINE.md         # How data flows
├── MEMORY_API.md              # Script interfaces
└── MEMORY_GUIDE.md           # Usage guide
```

### 4.2 Implementation Timeline

```
Day 1 (Today):
├── [ ] Audit and merge dual daily notes
├── [ ] Create CEO memory folder structure
├── [ ] Move CEO daily notes to /daily/
└── [ ] Update memory_cleanup.py with consolidation

Day 2:
├── [ ] Implement KG chunking + caching
├── [ ] Add search result caching
├── [ ] Create MEMORY_API.py wrapper
└── [ ] Add weekly cleanup cron

Day 3:
├── [ ] Integrate experience_bank into KG
├── [ ] Create memory dashboard
├── [ ] Test full pipeline
└── [ ] Update all documentation
```

### 4.3 Integration Points

**Update Scripts:**
```python
# memory_cleanup.py - ADD:
- Consolidation logic
- CEO memory structure
- Experience integration

# kg_updater.py - ADD:
- Chunking support
- Caching layer
- Lazy loading

# memory_hybrid_search.py - ADD:
- Result caching
- Category pre-filter
```

---

## 🎯 SUCCESS METRICS

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Memory Systems | 6 | 3 | ✅ |
| CEO Memory Files | 30+ | <10 | 📋 |
| Search Latency | ~500ms | <200ms | ⚡ |
| KG Load Time | ~2s | <500ms | ⚡ |
| Experience Reuse | 0 | 10+/week | 📈 |

---

## 🚨 RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data loss during merge | HIGH | Backup before merge, test on copy first |
| Breaking existing scripts | HIGH | Test each script after changes |
| Performance regression | MEDIUM | Benchmark before/after |

---

## 📝 TASK LIST

### Immediate (Today)
- [ ] Backup all memory systems
- [ ] Merge dual daily notes (2026-04-11.md)
- [ ] Create CEO memory folder structure
- [ ] Move + consolidate CEO daily logs

### Short-term (This Week)
- [ ] Implement KG chunking
- [ ] Add memory_cleanup consolidation logic
- [ ] Create MEMORY_API.py
- [ ] Add weekly cleanup cron

### Long-term (This Month)
- [ ] Experience Bank integration
- [ ] Memory dashboard
- [ ] Full documentation
- [ ] Performance benchmarking

---

*Plan Version: 1.0*
*Next Update: After Phase 1 completion*
