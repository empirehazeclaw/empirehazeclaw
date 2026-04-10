# DEPTH TRACKING — Knowledge Graph

**Erstellt:** 2026-04-10
**Basierend auf:** knowledge-graph-skill research

---

## 🎯 PROBLEM

Aktuell haben wir keine Tiefe/Hierarchie im KG.

Beispiel:
```
root → topic → ... (keine depth info)
```

Wir wissen nicht:
- Wie tief ist ein Node?
- Was ist der Parent?
- Wie viele Ebenen haben wir?

---

## 💡 LÖSUNG

Parent-basierendes Depth Tracking wie bei knowledge-graph-skill:

```javascript
// Jeder Node hat:
{
  "id": "entity_id",
  "type": "concept",
  "label": "Name",
  "parent": "parent_id",  // Optional
  "depth": 3              // Berechnet
}

// Berechnung:
// depth = 0 wenn kein parent
// depth = parent.depth + 1 wenn parent existiert
```

---

## 📊 DEPTH LEVELS

| Depth | Beschreibung | Beispiel |
|-------|-------------|---------|
| 0 | Root/Top Level | EmpireHazeClaw (System) |
| 1 | Haupt-Kategorien | Memory, Scripts, Skills |
| 2 | Sub-Kategorien | Memory → Knowledge, Notes |
| 3 | Konkrete Entities | Knowledge → KG Concepts |
| 4+ | Spezifische Details | Credential → Buffer API |

---

## 🛠️ IMPLEMENTIERUNG

### depth Berechnung:

```python
def calc_depth(node_id, nodes):
    """Berechnet Tiefe eines Nodes."""
    node = nodes.get(node_id)
    if not node:
        return 0
    
    parent = node.get('parent')
    if not parent:
        return 0
    
    if parent not in nodes:
        return 0
    
    parent_depth = nodes[parent].get('depth', -1)
    if parent_depth < 0:
        return 0
    
    return parent_depth + 1

def recalc_all_depths(nodes):
    """Berechnet depths für alle Nodes neu."""
    for node_id in nodes:
        nodes[node_id]['depth'] = calc_depth(node_id, nodes)
    return nodes
```

---

## 📋 NUTZEN

### 1. Query-Optimierung
```
Tiefe Nodes (depth > 3) sind spezifischer
Flache Nodes (depth < 2) sind allgemeiner
```

### 2. Hierarchie-Verständnis
```
Bei Fehlern: "Ist es ein tiefes oder flaches Problem?"
```

### 3. Visualisierung
```
Level 0: System
  Level 1: Memory
    Level 2: Knowledge
      Level 3: Concepts
        Level 4: Specific Facts
```

### 4. Security
```
Tiefe Nodes könnten mehr Rechte brauchen
```

---

## 🎯 NÄCHSTE SCHRITTE

1. ⏳ KG Structure analysieren
2. ⏳ Parent-Felder hinzufügen wo sinnvoll
3. ⏳ Depth-Berechnung implementieren
4. ⏳ Max Depth tracken (meta.maxDepth)

---

## 📊 BEISPIEL

```json
{
  "nodes": {
    "root": {"type": "system", "depth": 0},
    "memory": {"type": "platform", "parent": "root", "depth": 1},
    "kg": {"type": "service", "parent": "memory", "depth": 2},
    "entity_type": {"type": "concept", "parent": "kg", "depth": 3}
  },
  "meta": {
    "maxDepth": 3
  }
}
```

---

*Erlernt aus: knowledge-graph-skill (ClawHub)*
