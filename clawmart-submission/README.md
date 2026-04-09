# Memory System Skill v3.0

**Price:** FREE | **Version:** 3.0 | **Category:** Ops

---

## ⚠️ Most AI Memory is Broken

Most AI memory is just a **flat text file that gets stale fast**.

**This is different.**

This is a **battle-tested three-layer system** used by production OpenClaw agents.

---

## 🏗️ The Three Layers

### Layer 1: Knowledge Graph (PARA)

**Entity-based storage:**
- **P**rojects
- **A**reas
- **R**esources
- **A**rchives

Atomic JSON with:
- Access tracking
- Memory decay (9% per week)
- Recency weighting

### Layer 2: Daily Notes

Chronological timeline:
- Raw events as they happen
- Time blocks
- Session context
- Feeds into knowledge graph

### Layer 3: Tacit Knowledge

Facts about the **USER**, not the world:
- Preferences
- Patterns
- Lessons learned
- Communication style

---

## ✨ Key Features

| Feature | What it does |
|---------|--------------|
| Memory Decay | Old facts fade, don't clutter |
| Recency Weighting | Recent info stays relevant |
| Priority Retrieval | HIGH/MEDIUM/LOW |
| Auto-Learning | Patterns get promoted |
| Access Tracking | Know what's being used |
| PARA Method | Organized, not chaotic |

---

## 📦 What's Included

```
memory-skill/
├── SKILL.md              # This file
├── README.md             # You're here
├── config.json           # v3.0 config
├── scripts/
│   ├── knowledge_graph.py
│   ├── daily_notes.py
│   └── tacit_knowledge.py
└── templates/
    └── memory_structure/
        ├── knowledge_graph.json
        ├── daily/
        └── tacit.md
```

---

## 🚀 Installation

```bash
# 1. Copy to workspace
cp -r memory-skill/ ~/your-workspace/

# 2. Create memory directory
mkdir -p memory/daily

# 3. Import in your agent
from scripts.knowledge_graph import KnowledgeGraph
from scripts.daily_notes import DailyNotes
from scripts.tacit_knowledge import TacitKnowledge
```

---

## 💡 Usage

```python
# Initialize
kg = KnowledgeGraph()
notes = DailyNotes()
tacit = TacitKnowledge()

# Query memory
facts = kg.query("POD business")
today = notes.get_today()
profile = tacit.get_user_profile()

# Add new info
kg.add_fact("Master", "prefers_German", confidence=0.9)
notes.add_entry("Afternoon", "Discussed POD strategy")
tacit.add_pattern("communication", "likes_short_messages")
```

---

## 🔄 Memory Decay

```
New fact → Score: 1.0
Each week → Score × 0.9
If accessed → Score = 1.0

Score < 0.3 → Archive (rarely retrieved)
Score ≥ 0.7 → HIGH priority
```

---

## 🎯 Why Free?

We're building our customer base with **FREE products**:

| Product | Price | Status |
|---------|-------|--------|
| Memory System v3.0 | FREE | ✅ Now |
| POD Agent | $19-29 | Coming |
| Etsy SEO | $15-25 | Coming |

**Help us grow → Leave a review!**

---

## 🆕 v3.0 Improvements

- ✅ Knowledge Graph (PARA)
- ✅ Memory Decay
- ✅ Recency Weighting
- ✅ Priority Retrieval
- ✅ Tacit Knowledge
- ✅ Auto-Learning

---

**No more stale text files. This is production-ready.**

---

*Made with ❤️ for the OpenClaw Community*
*Version: 3.0*
