# 🧠 Multi-Agent Shared Memory System
*Zentrales Memory-Management für alle Agents*

---

## 📁 Struktur

```
/workspace/shared/memory/
├── SHARED_MEMORY_RULES.md    ← Du bist hier
├── kg_summary.md             ← Knowledge Graph Zusammenfassung
├── agent_context/            ← Agent-spezifische Kontexte
│   ├── security.md
│   ├── builder.md
│   ├── data.md
│   ├── qc.md
│   └── research.md
└── .index.json               ← Schnellzugriff Index
```

---

## 🎯 Ziel

Alle Agents sollen:
1. **Lesen** können: Gemeinsames Wissen nutzen
2. **Schreiben** können: Erkenntnisse teilen
3. **Updaten** können: Knowledge Graph erweitern

---

## 📋 Zugriffsregeln

### 🧠 Data Manager (CDO)
| Aktion | Erlaubt |
|--------|---------|
| Knowledge Graph lesen | ✅ Immer |
| Knowledge Graph updaten | ✅ Immer |
| KG-Summary pflegen | ✅ Immer |
| Agent-Kontexte updaten | ✅ Immer |

### 🔒 Security Officer
| Aktion | Erlaubt |
|--------|---------|
| Knowledge Graph lesen | ✅ Immer |
| Audit Findings teilen | ✅ Immer |
| Security Insights schreiben | ✅ Immer |
| KG direkt updaten | ❌ Nur über Data Manager |

### 💻 Builder
| Aktion | Erlaubt |
|--------|---------|
| Knowledge Graph lesen | ✅ Immer |
| Technical Insights schreiben | ✅ Immer |
| Build-Status teilen | ✅ Immer |
| KG direkt updaten | ❌ Nur über Data Manager |

### 📋 QC Officer
| Aktion | Erlaubt |
|--------|---------|
| Knowledge Graph lesen | ✅ Immer |
| Quality Reports schreiben | ✅ Immer |
| Validation Insights teilen | ✅ Immer |
| KG direkt updaten | ❌ Nur über Data Manager |

### 🔬 Research
| Aktion | Erlaubt |
|--------|---------|
| Knowledge Graph lesen | ✅ Immer |
| Research Insights schreiben | ✅ Immer |
| Tech Findings teilen | ✅ Immer |
| KG direkt updaten | ❌ Nur über Data Manager |

---

## 🔄 Memory-Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Knowledge Graph                       │
│                 (Data Manager verwaltet)                 │
└──────────┬─────────────────┬─────────────────┬──────────┘
           │                 │                 │
           ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ Security │      │  Builder │      │    QC    │
    │  Officer │      │          │      │  Officer │
    └────┬─────┘      └────┬─────┘      └────┬─────┘
         │                 │                 │
         └────────┬────────┴────────┬────────┘
                  │                 │
                  ▼                 ▼
         ┌──────────────┐  ┌──────────────────┐
         │ Shared       │  │ Shared Insights   │
         │ Memory Layer │  │ (alle Agents)     │
         └──────────────┘  └──────────────────┘
```

---

## 📝 Wie man Memory teilt

### 1. Insight schreiben (Alle Agents)
```
Pfad: /workspace/memory/shared/insights/
Template: TEMPLATE.md nutzen
```

### 2. Knowledge Graph updaten (Data Manager)
```
Pfad: /workspace/data/memory/knowledge_graph/
```

### 3. Agent-Kontext updaten
```
Pfad: /workspace/shared/memory/agent_context/[agent].md
```

### 4. KG-Summary lesen
```
Pfad: /workspace/shared/memory/kg_summary.md
```

---

## 🏆 Quality Standards

| Regel | Beschreibung |
|-------|-------------|
| ** atomic** | Ein Insight = Ein Topic |
| **cite** | Quellen angeben |
| **tag** | Immer Tags vergeben |
| **date** | Datum nicht vergessen |
| **link** | Zum KG verlinken wenn relevant |

---

## 🔗 Verknüpfte Systeme

| System | Pfad |
|--------|------|
| Task Board | `/workspace/shared/TASK_BOARD.md` |
| Shared Insights | `/workspace/memory/shared/insights/` |
| Knowledge Graph | `/workspace/data/memory/knowledge_graph/` |
| Dreaming (Nightly) | `memory/dreaming/` (02:00 UTC) |

---

*Letzte Aktualisierung: 2026-04-09 23:07 UTC*
