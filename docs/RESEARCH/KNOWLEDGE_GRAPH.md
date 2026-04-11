# 🧠 KNOWLEDGE GRAPH — OFFIZIELLE DOKUMENTATION

**Datum:** 2026-04-10 21:33 UTC
**Status:** ✅ MERGED & DOCUMENTED

---

## ⚠️ KRITISCHE INFORMATION

### Der ECHTE Knowledge Graph:

```
/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json
```

| Metrik | Wert |
|--------|------|
| Entities | **173** |
| Relations | **4649** |
| Letztes Update | 2026-04-10 21:33 UTC |

---

## 📊 STRUKTUR

### Entity Types (Top 10):
| Type | Count | Beispiel |
|------|-------|----------|
| topic | 48 | AI-Trends, Sales |
| subtopic | 18 | Email-Marketing |
| note | 15 | Meeting-Notes |
| sales | 11 | Lead-Qualifizierung |
| concept | 11+5 (skill) | Solo Fighter Mode |
| marketing | 6 | TikTok-Marketing |
| product | 5 | KI-Mitarbeiter |
| usecase | 5 | Email-Management |
| system | 5 | OpenClaw-Gateway |
| pattern | 3 | Loop Detection |

### Wichtige Entities:
- **EmpireHazeClaw** — Business (HIGH PRIORITY)
- **KI-Mitarbeiter** — Produkt (HIGH PRIORITY)
- **Zielgruppe-KMU** — Business (HIGH PRIORITY)
- **Managed-AI-Hosting** — Produkt
- **Solo Fighter Mode** — Konzept (Sir HazeClaw Architektur)

---

## 📁 VERGLEICH: DIE ZWEI KG FILES

| Property | FALSCH (alt) | RICHTIG (aktuell) |
|----------|--------------|-------------------|
| Pfad | `/home/clawbot/.openclaw/memory/kg.json` | `/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json` |
| Entities | 24 | **173** |
| Relations | 26 | **4649** |
| Verwendung | ❌ NONE | ✅ ACTIVE |
| Inhalt | Skill-Tracking | Business KG |

---

## 🔄 VERMERGTER INHALT (2026-04-10 21:33)

Folgende Entities wurden hinzugefügt:

### Skills (NEU):
- `skill_loop_prevention` — Loop Detection Pattern
- `skill_qa_enforcer` — Quality Assurance
- `skill_backup_advisor` — Backup Advisory

### Patterns (NEU):
- `pattern_loop_detection` — Erkennt Loops
- `pattern_backup_paranoia` — Erkennt Backup-Paranoia
- `pattern_quality_first` — Quality over Quantity

### Scripts (NEU):
- `script_self_check` — Health Check Script
- `script_morning_brief` — Daily Briefing Script

---

## 📖 FORMAT (Entity)

```json
{
  "EntityID": {
    "type": "concept|skill|pattern|script|...",
    "category": "concept|skill|pattern|script|...",
    "facts": [{
      "content": "Description...",
      "confidence": 0.9,
      "extracted_at": "2026-04-10T...",
      "category": "concept"
    }],
    "priority": "HIGH|MEDIUM|LOW",
    "created": "2026-04-10T...",
    "last_accessed": ""
  }
}
```

---

## 🔗 FORMAT (Relation)

```json
{
  "from": "EntityID",
  "to": "EntityID", 
  "type": "relation_type",
  "weight": 0.7,
  "created_at": "2026-04-10T..."
}
```

---

## 🚫 VERALTET: /home/clawbot/.openclaw/memory/kg.json

**Dieses File wird NICHT mehr verwendet!**

Es enthielt nur Skill-Tracking (24 nodes) und ist nicht der echte Knowledge Graph.

**AB SOFORT:** Alle KG-Operationen nur noch auf:
```
/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json
```

---

## 🛠️ KG OPERATIONEN

### Lesen:
```bash
python3 -c "
import json
kg = json.load(open('/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json'))
print(f'Entities: {len(kg[\"entities\"])}, Relations: {len(kg[\"relations\"])}')
"
```

### Suchen:
```bash
grep -i "Suchbegriff" /home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json
```

### Backup:
```bash
cp /home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json \
   /home/clawbot/.openclaw/backups/kg_backup_$(date +%Y%m%d).json
```

---

## 📝 TABELLE: ENTITY TYPES

| Type | Verwendung | Priority |
|------|-----------|----------|
| business | EmpireHazeClaw, Zielgruppe | HIGH |
| product | KI-Mitarbeiter, Plans | HIGH |
| sales | Leads, Pipeline | MEDIUM |
| marketing | Kampagnen, Content | MEDIUM |
| concept | Architektur-Entscheidungen | MEDIUM |
| skill | Agent-Fähigkeiten | MEDIUM |
| pattern | Erkannte Patterns | MEDIUM |
| script | Automatisierungs-Scripts | LOW |
| system | Technische Systeme | LOW |
| usecase | Anwendungsfälle | LOW |

---

*Sir HazeClaw — Knowledge Graph Documentation*
*Letztes Update: 2026-04-10 21:33 UTC*
*Pflichtlektüre für alle KG-Operationen*