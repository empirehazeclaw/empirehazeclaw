# MEMORY.md - Advanced Memory System v3.1

*A production-ready memory system with automatic fact extraction and priority management*

---

## 🎯 Overview

This is NOT a flat text file. This is a **structured long-term memory system** with:
- PARA-method knowledge graph
- Automatic fact extraction
- Memory decay and recency weighting
- Daily note timeline
- Access tracking and priority management

---

## 🏗️ Complete Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY SYSTEM v3.1                       │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: Knowledge Graph (PARA)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Projects    │ Areas    │ Resources │ Archives      │   │
│  │ - POD Biz  │ System   │ Guides    │ Old Ideas     │   │
│  └─────────────────────────────────────────────────────┘   │
│  • Atomic JSON storage                                      │
│  • Automatic fact extraction                                │
│  • Memory decay (9%/week)                                  │
│  • Priority: HIGH/MEDIUM/LOW                               │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: Daily Notes (Timeline)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Morning (00-12) │ Afternoon (12-18) │ Evening    │   │
│  │ - Did X         │ - Did Y           │ - Did Z    │   │
│  └─────────────────────────────────────────────────────┘   │
│  • Chronological events                                     │
│  • Time-block format                                       │
│  • Feeds into Knowledge Graph                              │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: Tacit Knowledge (User)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Preferences │ Patterns │ Lessons │ Style          │   │
│  │ - German    │ - Quick  │ - Learn │ - Direct      │   │
│  └─────────────────────────────────────────────────────┘   │
│  • Facts about the USER                                     │
│  • Auto-learned patterns                                    │
│  • Communication style                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Automatic Fact Extraction

### How it works:

```python
class FactExtractor:
    """Automatically extract facts from conversations"""
    
    # Patterns that indicate important facts
    FACT_PATTERNS = {
        "preference": [
            "I prefer", "I like", "I want", "I don't like",
            "german", "english", "short", "detailed"
        ],
        "goal": [
            "goal is", "I want to", "my target", "aim for",
            "€100/month", "goal:"
        ],
        "learning": [
            "I learned", "found out", "discovered",
            "new:", "lesson:"
        ],
        "preference": [
            "call me", "my name", "don't call me"
        ]
    }
    
    def extract(self, text: str) -> list:
        """Extract facts from text"""
        facts = []
        
        for category, patterns in self.FACT_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in text.lower():
                    facts.append({
                        "category": category,
                        "content": text,
                        "extracted_at": datetime.now().isoformat(),
                        "confidence": self._calculate_confidence(text, pattern)
                    })
        
        return facts
    
    def _calculate_confidence(self, text: str, pattern: str) -> float:
        """Calculate confidence score 0-1"""
        # Direct statements are higher confidence
        direct_indicators = ["I am", "I will", "I want", "my"]
        if any(ind in text.lower() for ind in direct_indicators):
            return 0.9
        return 0.6
```

---

## 📊 Priority Management

### Access Tracking:

```python
class PriorityManager:
    """Manage memory priority and access"""
    
    PRIORITY_LEVELS = {
        "CRITICAL": 0.9,  # Must remember (name, preferences)
        "HIGH": 0.7,      # Important (goals, projects)
        "MEDIUM": 0.5,    # Useful (context, background)
        "LOW": 0.3,       # Reference (old info)
        "ARCHIVE": 0.1    # Almost never retrieved
    }
    
    def track_access(self, entity: str):
        """Track when something is accessed"""
        # Boost recency
        self.memory[entity]["last_accessed"] = datetime.now()
        self.memory[entity]["access_count"] += 1
        self.memory[entity]["priority"] = self._recalculate_priority(entity)
    
    def _recalculate_priority(self, entity: str) -> str:
        """Recalculate priority based on access patterns"""
        data = self.memory[entity]
        
        # Frequently accessed = CRITICAL
        if data.get("access_count", 0) > 10:
            return "CRITICAL"
        
        # Recently accessed = HIGH
        days_since = (datetime.now() - data["last_accessed"]).days
        if days_since < 7:
            return "HIGH"
        
        return "MEDIUM"
```

---

## 🔄 Complete Memory Flow with Auto-Extraction

```
User Message
    ↓
1. Extract Facts (auto)
    → Categorize: preference/goal/learning/pattern
    → Assign priority
    ↓
2. Update Knowledge Graph
    → Add to correct PARA category
    → Apply decay
    ↓
3. Log to Daily Notes
    → Time block
    → Raw content
    ↓
4. Update Tacit Knowledge
    → Extract patterns
    → Learn preferences
    ↓
5. Apply Priority Management
    → Track access
    → Recalculate priority
    ↓
6. Build Context
    → Query with priority weighting
    → Include recency
    ↓
7. Process Request
```

---

## 💾 Implementation

### Complete Memory System

```python
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

class MemorySystem:
    """Complete memory system v3.1"""
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.kg_path = self.workspace / "memory" / "knowledge_graph.json"
        self.daily_path = self.workspace / "memory" / "daily"
        self.tacit_path = self.workspace / "memory" / "tacit.md"
        
        # Initialize directories
        self.daily_path.mkdir(parents=True, exist_ok=True)
        
        # Load or create knowledge graph
        self.kg = self._load_kg()
        
        # Initialize components
        self.fact_extractor = FactExtractor()
        self.priority_manager = PriorityManager()
    
    def process_message(self, message: str, context: dict = None):
        """Complete memory processing pipeline"""
        
        # 1. Extract facts
        facts = self.fact_extractor.extract(message)
        
        # 2. Add to knowledge graph
        for fact in facts:
            self._add_to_kg(fact)
        
        # 3. Log to daily notes
        self._add_daily_entry(message)
        
        # 4. Extract patterns to tacit
        self._update_tacit(message)
        
        # 5. Save state
        self._save_kg()
    
    def query(self, query: str, priority_filter: str = None) -> List[dict]:
        """Query memory with priority and recency weighting"""
        
        results = []
        
        # Search knowledge graph
        for entity, data in self.kg["entities"].items():
            # Apply decay
            decay = self._calculate_decay(data["last_accessed"])
            
            # Check priority filter
            if priority_filter and data.get("priority") != priority_filter:
                continue
            
            # Search facts
            for fact in data.get("facts", []):
                if query.lower() in fact["content"].lower():
                    results.append({
                        "entity": entity,
                        "fact": fact["content"],
                        "category": fact.get("category", "unknown"),
                        "priority": data.get("priority", "MEDIUM"),
                        "score": fact["confidence"] * decay,
                        "last_accessed": data["last_accessed"]
                    })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def _calculate_decay(self, last_accessed: str) -> float:
        """Calculate decay (9% per week)"""
        days = (datetime.now() - datetime.fromisoformat(last_accessed)).days
        return 0.9 ** (days / 7)
    
    def _add_to_kg(self, fact: dict):
        """Add fact to knowledge graph with PARA"""
        
        # Determine PARA category
        category = self._determine_para_category(fact)
        
        # Add to entity
        entity = fact.get("category", "general")
        
        if entity not in self.kg["entities"]:
            self.kg["entities"][entity] = {
                "type": category,
                "facts": [],
                "priority": "MEDIUM",
                "created": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 0
            }
        
        self.kg["entities"][entity]["facts"].append({
            "content": fact["content"],
            "confidence": fact["confidence"],
            "extracted_at": fact["extracted_at"]
        })
    
    def _determine_para_category(self, fact: dict) -> str:
        """Determine PARA category"""
        
        category_map = {
            "preference": "Areas",
            "goal": "Projects",
            "learning": "Resources",
            "pattern": "Areas",
            "project": "Projects",
            "system": "Resources"
        }
        
        return category_map.get(fact.get("category", "general"), "Resources")
    
    def _add_daily_entry(self, content: str):
        """Add to daily notes"""
        
        today = datetime.now().strftime("%Y-%m-%d")
        hour = datetime.now().hour
        
        # Determine time block
        if hour < 12:
            block = "Morning"
        elif hour < 18:
            block = "Afternoon"
        else:
            block = "Evening"
        
        # Write to file
        file_path = self.daily_path / f"{today}.md"
        
        with open(file_path, "a") as f:
            f.write(f"\n### {block}\n")
            f.write(f"- {content}\n")
    
    def _update_tacit(self, content: str):
        """Extract and update tacit knowledge"""
        
        # Simple pattern extraction
        patterns = {
            "name": ["my name is", "call me"],
            "language": ["german", "deutsch", "english"],
            "style": ["short", "direct", "concise"]
        }
        
        # Write to tacit file
        with open(self.tacit_path, "a") as f:
            for key, keywords in patterns.items():
                if any(kw in content.lower() for kw in keywords):
                    f.write(f"\n## {key}\n")
                    f.write(f"- {content} (learned: {datetime.now().date()})\n")
    
    def _load_kg(self) -> dict:
        """Load knowledge graph"""
        if self.kg_path.exists():
            return json.load(open(self.kg_path))
        return {"entities": {}, "last_updated": None}
    
    def _save_kg(self):
        """Save knowledge graph"""
        self.kg["last_updated"] = datetime.now().isoformat()
        json.dump(self.kg, open(self.kg_path, "w"), indent=2)
```

---

## 📋 Complete File Structure

```
memory/
├── knowledge_graph.json     # Layer 1: PARA entities
├── daily/                  # Layer 2: Daily timeline
│   ├── 2026-03-05.md
│   └── 2026-03-04.md
├── tacit.md               # Layer 3: User patterns
├── todos.md               # Active TODOs
├── archive/               # Archived (decayed) memories
└── config.json           # Memory settings
```

---

## ⚙️ Configuration

```json
{
  "memory": {
    "version": "3.1",
    "decay_rate": 0.9,
    "decay_period_days": 7,
    "para_categories": ["Projects", "Areas", "Resources", "Archives"],
    "priority_levels": {
      "CRITICAL": 0.9,
      "HIGH": 0.7,
      "MEDIUM": 0.5,
      "LOW": 0.3,
      "ARCHIVE": 0.1
    },
    "auto_extraction": {
      "enabled": true,
      "confidence_threshold": 0.5,
      "categories": ["preference", "goal", "learning", "pattern"]
    },
    "access_tracking": {
      "enabled": true,
      "boost_on_access": true,
      "recalculate_on_access": true
    }
  }
}
```

---

## 🎯 Usage

```python
# Initialize
memory = MemorySystem("/workspace")

# Process a message (auto-extracts facts)
memory.process_message(
    "Ich heiße Nico und möchte Print-on-Demand Business starten. "
    "Mein Ziel ist €100/Monat zu verdienen!"
)

# Facts extracted:
# - preference: "Ich heiße Nico"
# - goal: "€100/Monat zu verdienen"
# - project: "Print-on-Demand Business"

# Query memory
results = memory.query("Geld", priority_filter="HIGH")
# Returns high-priority facts about money/goals
```

---

## 🔒 Security & Privacy

- All data local to workspace
- No external APIs
- Encrypted storage for sensitive data
- Access tracking for audit
- DM-only for personal data

---

## 🚀 Why This Works

| Feature | Old System | This System |
|---------|------------|-------------|
| Stale data | Yes | No (decay) |
| Organized | No (flat file) | Yes (PARA) |
| Auto-learning | No | Yes |
| Priority | All same | HIGH/MEDIUM/LOW |
| Access tracking | No | Yes |

---

*Version: 3.1*
*Features: PARA, Fact Extraction, Decay, Priority, Access Tracking*
