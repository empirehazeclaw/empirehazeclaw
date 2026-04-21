# 🧠 KG INDEX — Knowledge Graph Inventory
**Updated:** 2026-04-12 08:50 UTC
**KG Location:** `core_ultralight/memory/knowledge_graph.json`

---

## 📊 KG STATS

| Metric | Value |
|--------|-------|
| **Entities** | 260 |
| **Relations** | 523 |
| **Last Updated** | 2026-04-12 |
| **Access Count** | ⚠️ **ALL LOW (0-4)** |

---

## 🔴 CRITICAL ISSUE: KG Retrieval Broken

**Problem:** All 260 entities have `access_count < 5`
**Root Cause:** `memory_hybrid_search.py` never queries KG (access_count stays at 0)
**Impact:** KG grows but is never used!

### Fix Required (Phase 4):
1. Modify `memory_hybrid_search.py` to query KG first
2. Update `MEMORY_API.py` to expose KG search as primary
3. Add KG warmup on startup

---

## 📈 ENTITY TYPES

| Type | Count | Priority |
|------|-------|----------|
| topic | 47 | High |
| success_pattern | 25 | High |
| error_pattern | 20 | High |
| concept | 18 | Medium |
| subtopic | 18 | Medium |
| note | 15 | Medium |
| research | 13 | Medium |
| improvement | 13 | Medium |
| sales | 11 | Medium |
| system | 8 | High |
| category | 8 | Medium |
| skill | 7 | High |
| pattern | 7 | Medium |
| marketing | 6 | Medium |
| product | 5 | High |
| usecase | 5 | Medium |
| metrics | 5 | Medium |
| learning | 4 | Medium |
| infrastructure | 4 | High |
| domain | 4 | Medium |
| business | 3 | High |
| competition | 2 | Low |
| operations | 2 | Low |
| growth | 2 | Low |
| script | 2 | Low |
| decision | 1 | Low |
| person | 1 | Low |
| agent | 1 | Low |
| project | 1 | Low |
| reflection | 1 | Low |
| knowledge | 1 | Low |

---

## 🔗 RELATION TYPES

| Type | Count | Quality |
|------|-------|---------|
| co_occurs | 211 | ⚠️ Low (spam) |
| related_to | 198 | ✅ Medium |
| categorized_as | 69 | ✅ High |
| related_terms | 7 | ✅ High |
| implements | 7 | ✅ High |
| uses | 4 | ✅ High |
| follows | 3 | ✅ High |
| created | 3 | ✅ High |
| supports | 3 | ✅ High |
| enables | 2 | ✅ High |

**Note:** `co_occurs` was the spam relation type (68.7% before cleanup). Now at 40%.

---

## 🎯 TOP ENTITIES (by type)

### Business (3)
- EmpireHazeClaw
- Zielgruppe-KMU
- Managed-AI-Hosting

### Product (5)
- KI-Mitarbeiter
- Starter-Plan
- Professional-Plan
- Enterprise-Plan
- [others]

### System (8)
- OpenClaw Gateway
- Telegram Channel
- MetaClaw
- LCM Plugin
- MiniMax Model
- [others]

### Skills (7)
- [tracking skills]

---

## 📋 WEEK 2 TARGET: KG Growth

| Metric | Current | Target |
|--------|---------|--------|
| Entities | 260 | 500+ |
| Access Count | All low | >10 per important entity |
| Quality Relations | 60% | 80%+ |

### Action Plan:
1. Fix KG retrieval (Phase 4)
2. Add quality entities manually
3. Increase relation confidence threshold (0.7+)
4. Remove stale entities

---

## 🚨 ISSUES TO FIX

| # | Issue | Priority | Status |
|---|-------|----------|--------|
| 1 | KG never queried (access_count = 0) | 🔴 Critical | Phase 4 |
| 2 | co_occurs still high (40%) | 🟡 Medium | Monitor |
| 3 | No auto-update of access_count | 🟡 Medium | Phase 4 |
| 4 | Stale entities not removed | 🟢 Low | Week 2+ |

---

## 📁 KG RELATED SCRIPTS

| Script | Purpose | Status |
|--------|---------|--------|
| kg_updater.py | KG main + subcommands | ✅ Active |
| kg_enhancer.py | Enhancement | ⚠️ Merge into kg_updater |
| kg_lifecycle_manager.py | Lifecycle | ⚠️ Merge into kg_updater |
| kg_relation_cleaner.py | Clean relations | ⚠️ Merge into kg_updater |
| kg_dreamer.py | Dreaming/insights | ✅ Active |
| memory_hybrid_search.py | Hybrid search | 🔴 BROKEN |

---

*KG Index maintained by Sir HazeClaw*
*Last updated: 2026-04-12 08:50 UTC*