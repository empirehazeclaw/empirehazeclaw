# Phase 7: DB Cleanup Report

**Date:** 2026-04-13 08:46 UTC
**Status:** ✅ COMPLETE

## Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Database Size | 380 MB | ~370 MB | -10 MB (-2.6%) |
| FTS Entries | 4,546 | 771 | -3,775 (-83%) |
| FTS Content | 771 | 0 | -771 |
| Embedding Cache | 254 MB | 254 MB | unchanged |
| Chunks Embeddings | 49 MB | 49 MB | unchanged |

## Cleanup Actions

1. **Deleted orphaned FTS entries** - 3,775 entries not linked to chunks
2. **Deleted orphaned FTS content** - 771 content entries not linked to chunks
3. **Ran VACUUM + ANALYZE**

## Why Only 10MB Saved

The embedding_cache (254 MB, 4,024 entries) dominates the database size:
- Each embedding: ~64 KB (3072 floats × 4 bytes + overhead)
- Total vector data: ~303 MB (embedding_cache + chunks embeddings)

To achieve <100 MB target would require:
- Deleting the entire embedding cache (loss of cached embeddings)
- Deleting chunk embeddings (loss of semantic search capability)

## Recommendation for Future

If vectors can be regenerated from text (via Gemini or OpenAI), the embedding_cache 
could be cleared safely. This would reduce DB to ~120 MB.

**Current working size: ~370 MB (acceptable)**

## Backup Location

Pre-cleanup backup: `backup_pre_refactor/20260413/db_backup/`
- main_pre_cleanup.sqlite (380 MB)
- chunks_export.json (1.5 MB)
- files_export.json, meta_export.json

