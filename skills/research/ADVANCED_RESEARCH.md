# Advanced Research Methodology

**Version:** 1.0.0  
**Created:** 2026-04-11  
**Status:** Active  
**Author:** Sir HazeClaw

---

## Overview

Deep Research ist mehr als nur "googeln". Es ist ein systematischer Prozess um Knowledge zu acquire, analysieren, synthetisieren und anwenden.

Dieses Dokument definiert fortgeschrittene Research Patterns für Sir HazeClaw.

---

## 🧠 Deep Research Loop

```
┌─────────────────────────────────────────────────────────────┐
│                    DEEP RESEARCH LOOP                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│   │ RESEARCH │───▶│ ANALYZE  │───▶│ SYNTHESIZE│              │
│   └──────────┘    └──────────┘    └──────────┘              │
│        │              │              │                       │
│        ▼              ▼              ▼                       │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│   │ Document │◀───│ Validate │◀───│ Create   │              │
│   └──────────┘    └──────────┘    └──────────┘              │
│        │                                             │       │
│        └─────────────────────────────────────────────┘       │
│                         (iterate)                            │
└─────────────────────────────────────────────────────────────┘
```

### Phase 1: RESEARCH
- **Goal:** Breite Information sammeln
- **Actions:**
  - Multiple Web Searches mit Variationen
  - Fetch 5-10 relevante URLs
  - Collect Zitate, Statistics, Patterns
- **Output:** Raw Notes (ungefiltert)

### Phase 2: ANALYZE
- **Goal:** Informationen filtern und strukturieren
- **Actions:**
  - Wichtige Insights von noise trennen
  - Quellen evaluieren (reliability check)
  - Contradictions identifizieren
- **Output:** Strukturierten Notes

### Phase 3: SYNTHESIZE
- **Goal:** Neue Erkenntnis erschaffen
- **Actions:**
  - Combine insights zu neuer Ideas
  - Eigene Interpretation entwickeln
  - Validate mit weiteren Sources
- **Output:** Synthesized Knowledge

### Phase 4: DOCUMENT
- **Goal:** Knowledge persistent machen
- **Actions:**
  - In memory/research/ speichern
  - Key findings to KG hinzufügen
  - Mit Master teilen wenn relevant
- **Output:** Persistentes Wissen

---

## 🔍 Web Research Workflow

### Effizientes Suchen

```python
# Research Workflow Template
def deep_research(topic, depth='normal'):
    """
    Deep Research Workflow
    
    Args:
        topic: Was soll erforscht werden?
        depth: 'shallow' (5min) | 'normal' (20min) | 'deep' (60min+)
    """
    
    # 1. Generate search queries
    queries = [
        f"{topic} best practices 2026",
        f"{topic} advanced techniques",
        f"{topic} common pitfalls",
        f"{topic} case studies",
        # Variations for different perspectives
        f"why {topic} doesn't work",
        f"future of {topic}",
    ]
    
    # 2. Execute searches (limit to prevent overload)
    max_results = 10 if depth == 'shallow' else 30
    results = web_search_multi(queries, max_results)
    
    # 3. Fetch content
    urls = extract_unique_urls(results)
    content = fetch_parallel(urls[:15])  # Limit for efficiency
    
    # 4. Analyze and synthesize
    insights = analyze_content(content)
    
    # 5. Document
    save_to_memory(insights, topic)
    add_to_kg(insights)
    
    return insights
```

### Search Query Patterns

| Pattern | Example | Use Case |
|---------|---------|----------|
| `[topic] best practices` | `AI agent best practices` | How-to Guides |
| `[topic] architecture` | `microservices architecture` | System Design |
| `[topic] failure cases` | `kubernetes failure cases` | Risk Analysis |
| `[topic] 2026` | `LLM optimization 2026` | Current State |
| `why [topic] fails` | `why microservices fail` | Critical Analysis |
| `[topic] vs [alternative]` | `kubernetes vs docker swarm` | Comparison |

---

## 📊 Source Evaluation Matrix

### Vertrauenswürdigkeit

| Source | Score | Why |
|--------|-------|-----|
| Official Documentation | ⭐⭐⭐⭐⭐ | Ground truth |
| Academic Papers | ⭐⭐⭐⭐⭐ | Peer reviewed |
| GitHub Issues/PRs | ⭐⭐⭐⭐ | Real problems, real solutions |
| Stack Overflow | ⭐⭐⭐ | Often outdated, but verified |
| Official Blog Posts | ⭐⭐⭐⭐ | Curated, but marketing |
| Expert Twitter/X | ⭐⭐⭐ | Quick takes, check sources |
| Reddit | ⭐⭐ | Anecdotal, verify claims |
| Medium/Blogs | ⭐⭐ | Varies wildly |
| YouTube | ⭐⭐ | Shallow for complex topics |

### Red Flags (Unreliable Sources)
- Keine Zitate/References
- Extreme claims ohne Beweis
- Veraltete Informationen
- Promotion/Marketing heavy
- Anonyme Autoren

---

## 🧬 Mind Map Creation

### Strukturiertes Knowledge Mapping

```
                    [MAIN TOPIC]
                          │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   [CATEGORY 1]    [CATEGORY 2]   [CATEGORY 3]
         │               │               │
    ┌────┴────┐      ┌────┴────┐      ┌────┴────┐
    ▼    ▼    ▼      ▼    ▼    ▼      ▼    ▼    ▼
  [A]  [B]  [C]    [D]  [E]  [F]    [G]  [H]  [I]
```

### Mind Map Template

```markdown
# [TOPIC] Mind Map

## Zentrales Konzept
[B kurze Beschreibung]

## Hauptzweige

### 1. [First Principle]
- Sub-points
- Details
- Examples

### 2. [Second Principle]
- Sub-points
- Details
- Examples

### 3. [Third Principle]
- Sub-points
- Details
- Examples

## Verbindungen
- [Branch 1] → [Branch 2]: [why related]
- [Branch 2] → [Branch 3]: [why related]

## Offene Fragen
- Was ist noch unklar?
- Welche Aspekte brauchen mehr Research?
```

---

## 📝 Information Synthesis

### Der Synthese-Prozess

```
Raw Input ──▶ Filter ──▶ Group ──▶ Prioritize ──▶ Synthesize ──▶ Output
                 │         │           │              │
            Remove      Cluster    Rank by         Create new
            noise      related     importance      insight
```

### Synthesis Rules

1. **Never Copy-Paste** - Immer in eigenen Worten
2. **Cite Sources** - Für wichtige Fakten
3. **Identify Contradictions** - Dokumentiere sie
4. **Add Value** - Nicht nur zusammenfassen, sondern ergänzen
5. **Make it Actionable** - Was kann man damit machen?

### Synthesis Template

```markdown
# Research Synthesis: [TOPIC]

## Executive Summary
[2-3 sentences was ist das wichtigste]

## Key Insights

### Insight 1: [Name]
- **What:** [Kurze Beschreibung]
- **Source:** [Source mit Link]
- **Why Important:** [Relevanz]
- **Action:** [Was kann man damit machen]

### Insight 2: ...
...

## Open Questions
- [Frage 1]
- [Frage 2]

## Next Steps
- [Action 1]
- [Action 2]
```

---

## 🔄 Research Pattern Library

### Pattern: Competitive Research
```
1. Identify 3-5 main competitors
2. Fetch their websites, docs, blogs
3. Analyze: Was bieten sie an? Was fehlt?
4. Compare: Preis, Features, Positioning
5. Document: Opportunities/Threats
```

### Pattern: Technology Evaluation
```
1. Official Docs lesen
2. GitHub stars/issues checken
3. Reddit/HN discussions lesen
4. Try it yourself ( wenn möglich)
5. Decision framework anwenden
```

### Pattern: Best Practice Research
```
1. Search "[topic] best practices"
2. Filter für aktuelle (2024+)
3. Collect 5-10 guides
4. Extract common patterns
5. Apply mit lokaler Anpassung
```

---

## 🎯 Research Quality Checklist

Vor "Research abgeschlossen":

- [ ] Mindestens 5 verschiedene Quellen
- [ ] Quellen evaluiert (reliability check)
- [ ] Key insights dokumentiert
- [ ] Contradictions notiert
- [ ] Synthesized knowledge erstellt
- [ ] In memory/ oder KG gespeichert
- [ ] Own words (kein copy-paste)
- [ ] Actionable conclusions

---

## 📚 Research Output Examples

### Example: Technology Evaluation

```markdown
# Technology Eval: [NEW_TOOL]

## Summary
[1-2 sentence description]

## Pros
- ✅ [Advantage 1]
- ✅ [Advantage 2]

## Cons  
- ❌ [Disadvantage 1]
- ❌ [Disadvantage 2]

## Use Cases
- Best for: [Use case]
- Avoid for: [Use case]

## Decision
🟢 Adopt | 🟡 Further Evaluation | 🔴 Reject

## Next Steps
- [If adopted: how to get started]
```

---

## 🔗 Integration with KG

Research findings should be added to Knowledge Graph:

```python
def add_research_to_kg(insights):
    """Add research insights to Knowledge Graph."""
    kg_updates = []
    
    for insight in insights:
        entity = {
            "type": "research_insight",
            "name": f"insight_{insight['topic']}_{date}",
            "properties": {
                "topic": insight["topic"],
                "summary": insight["summary"],
                "confidence": insight["confidence"],  # 0-1
                "sources": insight["sources"],
                "research_date": date,
            }
        }
        kg_updates.append(entity)
    
    # Add to KG via kg_updater or direct API
    return kg_updates
```

---

*Last Updated: 2026-04-11*
*Part of: Sir HazeClaw Research Skill*
