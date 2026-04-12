# 🔍 QMD — Query Markdown Documents

**Type:** CLI Search Tool
**Installed:** `/home/clawbot/.npm-global/bin/qmd`
**Status:** ✅ READY TO USE (On-Demand, not a daemon)

---

## 🎯 WHAT IS QMD?

QMD is a **hybrid search engine for Markdown documents**. It combines:
- Full-text BM25 search
- Vector embeddings (local GGUF models)
- LLM-based query expansion + reranking

**Important:** QMD is **NOT a daemon**. It runs on-demand when you query it. No process needs to be running in the background.

---

## 📊 QMD STATUS

```
Index: /home/clawbot/.cache/qmd/index.sqlite
Size:  17.5 MB
Documents: 58 files indexed
Vectors: 1692 embedded
Updated: 2d ago

Collections:
  memory (qmd://memory/)
    Pattern:  **/*.md
    Files:    58 (updated 2d ago)
```

---

## 🚀 USAGE

### Basic Search
```bash
qmd search "error handling" -c memory     # BM25 full-text search
qmd query "how do I fix cron errors" -c memory  # Hybrid search (recommended)
qmd vsearch "pattern matching" -c memory      # Vector similarity only
```

### List Files
```bash
qmd ls memory                      # List all indexed files
qmd get qmd://memory/2026-04-11.md  # Get specific file
```

### Update Index
```bash
qmd update --pull  # Git pull + re-index
qmd embed -f       # Force re-embed vectors
```

---

## ⚙️ QMD CONFIGURATION

### Models Used
| Model | Type | Location |
|-------|------|----------|
| embeddinggemma-300M-GGUF | Embedding | HuggingFace (cached) |
| Qwen3-Reranker-0.6B-Q8_0 | Reranking | HuggingFace (cached) |
| qmd-query-expansion-1.7B | Query Expansion | HuggingFace (cached) |

### Performance Note
```
GPU: none (running on CPU — slow)
CPU: 2 math cores
```
Without GPU acceleration, queries are slower but still functional.

---

## 🔄 INTEGRATION WITH OPENCLAW

QMD is **independent** from OpenClaw's memory-core plugin:

| Feature | OpenClaw memory-core | QMD |
|--------|---------------------|-----|
| Type | Plugin (automatic) | CLI (on-demand) |
| Purpose | Memory consolidation | Document search |
| Index | SQLite vectors | QMD SQLite index |
| Timing | 04:40 UTC nightly | Manual query |

### When to Use QMD
- **Quick search** through all Markdown docs
- **Finding specific patterns** or code snippets
- **Research** through documentation
- **Not covered by memory-core**: QMD searches ALL .md files

### When to Use memory-core
- **Automatic memory consolidation**
- **Dreaming** (recall promotion)
- **Long-term learning** (KG entities)

---

## 📁 INDEX LOCATION

```
/home/clawbot/.cache/qmd/
├── index.sqlite          # Main index
└── embeddings/           # Vector cache
```

---

## 🔧 TROUBLESHOOTING

### "No qmd process running"
**This is NORMAL.** QMD is not a daemon. It runs on-demand.

### Slow queries
**Cause:** CPU-only mode (no GPU)
**Solution:** Install CUDA/ROCm for GPU acceleration, or accept slower performance.

### Index out of date
```bash
qmd update --pull  # Update + re-index
```

---

## 📝 SCRIPTS INTEGRATION

### Example: Create a search script
```bash
#!/bin/bash
# scripts/qmd_search.sh
qmd query "$1" -c memory --format markdown
```

### Example: Add to cron (weekly reindex)
```
0 6 * * 0 qmd update --pull >> ~/.openclaw/logs/qmd_update.log 2>&1
```

---

## 📊 ALTERNATIVES

| Tool | Best For | Speed |
|------|----------|-------|
| `grep` | Simple text search | Fast |
| `qmd search` | BM25 keyword search | Medium |
| `qmd query` | Semantic/hybrid search | Slower (CPU) |
| OpenClaw memory search | Integrated memory | Fast |

---

*Letztes Update: 2026-04-12 06:57 UTC*
*QMD v1.0 — Installed and ready*
