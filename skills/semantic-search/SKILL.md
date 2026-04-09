---
name: semantic-search
description: Semantische Suche im Workspace. Nutze diese Skill wenn du komplexe Queries hast die mit Keyword-Matching nicht gefunden werden, oder wenn du ähnliche Konzepte über mehrere Dateien hinweg suchen willst.
---

# 🔍 Semantic Search Skill

Semantische Suche mit lokalen Embeddings (all-MiniLM-L6-v2).

## Use Cases

- Komplexe Queries die Keyword-Matching nicht findet
- Ähnliche Konzepte über mehrere Dateien
- "Was wissen wir über X?" type questions
- Code/Content Discovery über Kategorien hinweg

## Nutzung

```bash
python3 /home/clawbot/.openclaw/workspace/scripts/semantic_search.py build   # Index neu bauen
python3 /home/clawbot/.openclaw/workspace/scripts/semantic_search.py search "<query>"  # Suchen
```

## Index

- **Location:** `/home/clawbot/.openclaw/workspace/data/semantic_index.json`
- **Size:** ~200KB (22 chunks)
- **Rebuild:** Täglich 06:00 UTC (cron)
- **Quelldateien:** `/home/clawbot/.openclaw/workspace/memory/*.md`

## Im Vergleich zu memory_search

| Tool | Wann nutzen |
|------|-------------|
| `memory_search` | Schnelle Keyword-Suche, Recall von Fakten |
| `semantic_search` | Komplexe Queries, konzeptuelle Ähnlichkeit |

## Workflow

1. Query an semantic_search.py übergeben
2. Embeddings werden lokal generiert (all-MiniLM-L6-v2)
3. Kosinus-Ähnlichkeit über Index
4. Top Results mit Score返回

## Output Format

```
🔍 Results for: <query>
==================================================
[<score>] <source_file>
  <excerpt>...
```
