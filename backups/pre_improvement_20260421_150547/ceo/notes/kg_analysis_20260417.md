# Knowledge Graph Analysis — 2026-04-17

## 📊 Current State

| Metric | Value |
|--------|-------|
| **Entities** | 444 |
| **Relations** | 628 |
| **Orphans** | 175 (39.4%) ⚠️ |
| **Unweighted Relations** | 272 (43.3%) ⚠️ |

---

## 🔴 Quality Issues

### 1. Orphan Entities (175)
**Critical** — 39.4% of entities have no relations:
- `Gateway-Restart-Problem`
- `Trading-Bot-Nicht-Profitabel`
- `Buffer-API-Limitation`
- Many `auto-extracted` placeholders

**Impact:** These entities cannot participate in graph reasoning. They're dead weight.

### 2. Placeholder/Empty Entities (226)
**High** — 51% of entities have:
- Empty facts
- `Source: [internal-path]` placeholders
- `confidence: 0.6` (low)

These are artifacts from import processes, not real knowledge.

### 3. Unweighted Relations (43.3%)
**Medium** — Nearly half of relations lack explicit weights.
- Only 356/628 relations have weights
- Weights range 0.32–1.0 (good spread)
- But the unweighted 43% default to unclear values

### 4. Unused Entities (311 never accessed)
**Medium** — 70% of entities never accessed:
- `auto-extracted` categories (92 entities)
- `pattern` category (61 entities)
- Many are stale metadata artifacts

### 5. Category Imbalance
```
unknown:            96 (21.6%)
auto-extracted:      92 (20.7%)
pattern:             61 (13.7%)
safety:              32 (7.2%)
system:              28 (6.3%)
```

**Issue:** 96 entities have `category: None/unknown` — inconsistent taxonomy.

---

## 📈 Relation Analysis

### Relation Types (Top 5)
| Type | Count | Usage |
|------|-------|-------|
| `co_occurs` | 211 | Good — captures temporal co-occurrence |
| `related_to` | 198 | Too generic — needs disambiguation |
| `categorized_as` | 69 | Good — semantic categorization |
| `created` | 64 | Good — provenance tracking |
| `validates` | 33 | Good — quality assertions |

**Problem:** `related_to` is too vague — 198 relations with no specific semantics.

### Relation Weight Distribution
- Min: 0.32 (weak)
- Max: 1.0 (strong)
- Avg: 0.85 (skewed high)
- **Most weights are >0.8** — low discrimination power

---

## 🏆 Best Practices (Research)

### 1. Entity Resolution
> "Without Entity Resolution, knowledge graphs are dumb!" — Senzing

**Best Practices:**
- **Canonicalization:** Each real-world entity = one node (not multiple)
- **Fuzzy matching:** Detect `Email-Management` vs `Email Management` duplicates
- **Confidence scoring:** Track resolution certainty
- **Graph embedding + Link Prediction:** Neo4j approach for discovering hidden linkages

### 2. Relation Weighting
**Current:** Uniform-ish (avg 0.85) — poor discrimination

**Better approaches:**
- **TF-IDF inspired:** Weight by how unique/predictive a relation is
- **Temporal decay:** Recent relations > old ones
- **Evidence-based:** More sources = higher weight
- **Transitive propagation:** propagate weights through paths

### 3. Graph Query Optimization
**Key techniques:**
- **Hierarchical retrieval** (arxiv:2503.01642): Narrow search space progressively
- **Seed node expansion:** Start with query entities, expand n-hop
- **Pruning:** Beam search + score cutoff
- **Caching:** Common subgraph patterns

### 4. Quality > Quantity
> "A well-curated knowledge graph with accurate entities and relationships will outperform a large, noisy graph." — Calmops 2026

---

## 🎯 Optimization Recommendations

### 🔴 P0 — Critical (Do Now)

#### 1. Clean Orphan Entities
```python
# Script to analyze and optionally merge/delete orphans
# Target: Reduce from 175 to <20
```

**Action:** Run orphan analysis, then:
- Delete truly useless entities (test artifacts, imports)
- Merge related orphans OR connect to graph

#### 2. Remove Placeholder Entities
**92 entities** with `category: auto-extracted` + `Source: [internal-path]` are noise.

**Action:** Add rule to KG builder: never create entity without real content.

#### 3. Fix Missing Relation Weights
272 relations with `weight: null` default to weight=1, inflating importance.

**Action:** 
- Set default `weight: 0.5` for null (neutral)
- OR run analysis to infer weights from relation type + connected entity quality

### 🟡 P1 — High Priority

#### 4. Disambiguate "related_to" Relations
198 relations use generic `related_to` — no semantic meaning.

**Options:**
- Replace with specific types: `depends_on`, `enables`, `contradicts`, `improves`
- OR add metadata: `related_to` with `strength: weak|medium|strong`

#### 5. Entity Deduplication
Example duplicates found:
- `skill_loop_prevention` vs `loop_detection` pattern
- `pattern_quality_first` vs `concept_quality_first_20260410`

**Action:** Create entity resolution matcher to detect:
- Similar names (fuzzy string match)
- Similar facts (content overlap >80%)
- Same category + temporal proximity

#### 6. Implement Decay Score Properly
**Current:** All `decay_score: 1` (no decay happening)
**Needed:** `decay_score < 1` for stale entities (never accessed + old)

### 🟢 P2 — Medium Priority

#### 7. Normalize Priority Distribution
Current:
- HIGH: 61 (13.7%)
- MEDIUM: 378 (85.1%)
- LOW: 2
- CRITICAL: 3

**Issue:** Almost everything is MEDIUM — no real prioritization.

**Fix:** Rescale so HIGH ≈ 15%, MEDIUM ≈ 50%, LOW ≈ 30%, CRITICAL < 5%

#### 8. Add Temporal Metadata to Relations
Relations have `created_at` but no:
- `updated_at` (last verified)
- `confidence` (how sure about this relation)
- `source` (where did this come from)

#### 9. Improve Access Tracking Integration
`memory_hybrid_search.py` has `update_kg_access()` but:
- Only called for semantic search
- Not called for relation traversal queries
- No batch update for multi-entity operations

---

## 📋 Suggested Implementation Order

```
Week 1: Cleanup
├── [ ] Remove 92 auto-extracted placeholder entities
├── [ ] Delete/merge 175 orphans
└── [ ] Set default weight=0.5 for null relations

Week 2: Quality
├── [ ] Entity deduplication (fuzzy match)
├── [ ] Replace 198 generic "related_to"
└── [ ] Implement decay_score decay logic

Week 3: Optimization
├── [ ] Add relation confidence/source metadata
├── [ ] Improve KG access tracking for all query paths
└── [ ] Add graph embedding for similarity search

Week 4: Monitoring
├── [ ] Add KG health dashboard
├── [ ] Track: orphan %, avg weight, unused entities
└── [ ] Alert when quality metrics degrade
```

---

## 📁 Files Analyzed
- `memory/kg/knowledge_graph.json` — 444 entities, 628 relations
- `memory/search/memory_hybrid_search.py` — KG integration code

## 🔗 References
- [Senzing: Entity Resolved Knowledge Graphs](https://senzing.com/entity-resolved-knowledge-graphs/)
- [Calmops: GraphRAG Complete Guide 2026](https://calmops.com/ai/graphrag-complete-guide-2026/)
- [Neo4j: Entity Resolution Use Cases](https://neo4j.com/blog/graph-data-science/graph-data-science-use-cases-entity-resolution/)
- [arXiv: Multi-hop KG Question Answering with Query Graph Optimization](https://dl.acm.org/doi/10.1145/3730436.3730443)