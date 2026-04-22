# Knowledge Graph Reorganisation — 2026-04-17
**Status:** IN_PROGRESS

## Current KG State
- Entities: 277
- Relations: 636
- Last updated: 2026-04-17 19:03 UTC

## Issues Identified
1. **Orphan entities** — some entities have no relations
2. **Stale data** — some entities from old/broken integrations
3. **No quality score** — KG has no health metric

## Reorganisation Plan

### 1. KG Quality Score
Introduce a quality score based on:
- Entity completeness (has description, relations)
- Relation validity (both endpoints exist)
- Recency (when was entity last updated)

### 2. Orphan Detection
Find entities with 0 relations and either:
- Delete them (if truly orphaned)
- Link them to relevant clusters

### 3. Stale Entity Cleanup
Mark entities not updated in >30 days as "stale"
- Review stale entities for deletion or update

## Implementation
Script: `kg_reorganizer.py` (待创建)

## Status
- [x] KG state analyzed
- [ ] Quality score implemented
- [ ] Orphan detection run
- [ ] Cleanup executed