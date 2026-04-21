#!/usr/bin/env python3
"""
Reflection Engine — Sir HazeClaw Self-Reflection
=================================================
Generates natural-language self-critique after task failures.

Based on:
- Reflexion (Shinn et al., 2023) — Verbal RL for self-correction
- RISE (Qu et al., 2024) — Recursive Introspection
- Self-Refine (Madaan et al., 2023) — Generate → Critique → Revise

Usage:
    python3 reflection_engine.py --reflect task.json
    python3 reflection_engine.py --store
    python3 reflection_engine.py --retrieve --type learning_loop

Phase 5 of Self-Improvement Plan
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data"
REFLECTIONS_FILE = DATA_DIR / "reflection_store.json"
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"

MAX_REFLECTIONS = 100


def load_reflections() -> List[Dict]:
    """Load reflections from storage."""
    if REFLECTIONS_FILE.exists():
        data = json.load(open(REFLECTIONS_FILE))
        return data.get("reflections", [])
    return []


def save_reflections(reflections: List[Dict]):
    """Save reflections to storage."""
    REFLECTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {"reflections": reflections, "last_update": datetime.utcnow().isoformat() + "Z"}
    with open(REFLECTIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def prune_reflections(reflections: List[Dict]) -> List[Dict]:
    """Keep only most recent + most used reflections."""
    if len(reflections) <= MAX_REFLECTIONS:
        return reflections
    
    # Sort by score: use_count * recency
    scored = []
    for r in reflections:
        last_used = r.get("last_used", r.get("created_at", ""))
        try:
            age_days = (datetime.now() - datetime.fromisoformat(last_used.replace("Z", "+00:00"))).days
        except:
            age_days = 0
        score = r.get("use_count", 0) * 10 - age_days
        scored.append((score, r))
    
    scored.sort(reverse=True, key=lambda x: x[0])
    return [r for _, r in scored[:MAX_REFLECTIONS]]


class ReflectionEngine:
    """
    Generates natural-language self-critique after task failures.
    
    Pattern:
    1. Task fails
    2. Generate critique (what went wrong, why, how to fix)
    3. Store critique (local + KG)
    4. Retrieve relevant past critiques for similar tasks
    
    KG Integration (Phase 3):
    - Reflections stored as 'reflection' entities in KG
    - Linked to task_type, error_type, and related patterns
    - Semantic search via KG relations
    """
    
    def __init__(self):
        self.reflections = load_reflections()
        self.llm_available = self._check_llm()
        self._kg_cache = None
    
    def _check_llm(self) -> bool:
        """Check if LLM API is available."""
        try:
            import urllib.request
            req = urllib.request.Request(
                "https://api.minimax.chat/v1/text/chatcompletion_pro",
                headers={"Authorization": f"Bearer {os.environ.get('MINIMAX_API_KEY', '')}"}
            )
            return True
        except:
            return False
    
    def _load_kg(self) -> Dict:
        """Load KG (lazy)."""
        if self._kg_cache is None:
            if KG_PATH.exists():
                self._kg_cache = json.load(open(KG_PATH))
            else:
                self._kg_cache = {"entities": {}, "relations": []}
        return self._kg_cache
    
    def _save_kg(self, kg: Dict):
        """Save KG."""
        with open(KG_PATH, "w") as f:
            json.dump(kg, f, indent=2)
        self._kg_cache = kg
    
    def _create_kg_entity(self, reflection: Dict) -> str:
        """
        Create KG entity for a reflection.
        
        Returns entity ID.
        """
        kg = self._load_kg()
        entity_id = f"reflection_{int(time.time() * 1000)}"
        
        entity = {
            "type": "reflection",
            "name": f"{reflection.get('task_type', 'unknown')}:{reflection.get('error_type', 'unknown')}",
            "properties": {
                "task_type": reflection.get("task_type", "unknown"),
                "error_type": reflection.get("error_type", "unknown"),
                "critique": reflection.get("critique", ""),
                "task_description": reflection.get("task_description", ""),
                "created_at": reflection.get("created_at", ""),
                "use_count": reflection.get("use_count", 0),
                "resolved": reflection.get("resolved", False),
            }
        }
        
        kg["entities"][entity_id] = entity
        
        # Create relations to task_type and error_type categories
        task_type = reflection.get("task_type", "unknown")
        error_type = reflection.get("error_type", "unknown")
        
        # Relation: reflection → task_type (category)
        # Note: KG uses 'relationships' (list), not 'relations' (dict)
        rel1 = {
            "from": entity_id,
            "to": f"category_{task_type}",
            "type": "related_to",
            "weight": 0.8,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        if "relationships" not in kg:
            kg["relationships"] = []
        kg["relationships"].append(rel1)
        
        # Relation: reflection → error_type (category)
        # Note: KG uses 'relationships' (list), not 'relations' (dict)
        rel2 = {
            "from": entity_id,
            "to": f"category_{error_type}",
            "type": "related_to",
            "weight": 0.9,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        if "relationships" not in kg:
            kg["relationships"] = []
        kg["relationships"].append(rel2)
        
        # Also create category entities if they don't exist
        for cat_name in [task_type, error_type]:
            cat_id = f"category_{cat_name}"
            if cat_id not in kg["entities"]:
                kg["entities"][cat_id] = {
                    "type": "category",
                    "name": cat_name,
                    "properties": {"source": "reflection_engine", "count": 0}
                }
            # Increment count
            if "count" in kg["entities"][cat_id].get("properties", {}):
                kg["entities"][cat_id]["properties"]["count"] += 1
        
        self._save_kg(kg)
        return entity_id
    
    def _get_kg_reflections(self, task_type: str = None, error_type: str = None, limit: int = 3) -> List[Dict]:
        """
        Get reflections from KG.
        
        Filters by task_type and/or error_type if provided.
        Returns list of reflection entities.
        """
        kg = self._load_kg()
        results = []
        
        for eid, entity in kg.get("entities", {}).items():
            if entity.get("type") != "reflection":
                continue
            
            props = entity.get("properties", {})
            
            # Filter
            if task_type and props.get("task_type") != task_type:
                continue
            if error_type and props.get("error_type") != error_type:
                continue
            if props.get("resolved"):
                continue
            
            # Add use_count from KG
            entity["id"] = eid
            entity["use_count_kg"] = props.get("use_count", 0)
            results.append(entity)
        
        # Sort by use_count (most useful first)
        results.sort(key=lambda x: x.get("use_count_kg", 0), reverse=True)
        return results[:limit]
    
    def reflect(self, task: Dict, result: Dict, context: Optional[Dict] = None) -> Dict:
        """
        Generate self-reflection for a failed task.
        
        Args:
            task: Task details (type, description, expected, etc.)
            result: What happened (error, output, etc.)
            context: Additional context (session, time, etc.)
        
        Returns:
            Dict with reflection details + critique text
        """
        context = context or {}
        
        # Build reflection
        reflection = {
            "id": f"reflect_{int(time.time() * 1000)}",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "task_type": task.get("type", "unknown"),
            "task_description": task.get("description", "")[:200],
            "error_type": result.get("error_type", result.get("error", "unknown")),
            "error_detail": result.get("detail", result.get("error", ""))[:500],
            "resolved": False,
            "use_count": 0,
            "last_used": None,
        }
        
        # Generate critique via LLM or rule-based
        if self.llm_available:
            critique_text = self._generate_llm_critique(task, result, context)
        else:
            critique_text = self._generate_rule_based_critique(task, result)
        
        reflection["critique"] = critique_text
        
        # Store
        self.reflections.append(reflection)
        self.reflections = prune_reflections(self.reflections)
        save_reflections(self.reflections)
        
        # PHASE 3: Also store in KG for semantic retrieval
        try:
            kg_entity_id = self._create_kg_entity(reflection)
            reflection["kg_entity_id"] = kg_entity_id
        except Exception as e:
            print(f"Warning: KG storage failed: {str(e)[:50]}")
        
        return reflection
    
    def _generate_llm_critique(self, task: Dict, result: Dict, context: Dict) -> str:
        """Generate critique using LLM."""
        # Build prompt
        prompt = f"""
Du bist ein selbst-reflektierendes KI-System. Analysiere den fehlgeschlagenen Task.

FEHLGESCHLAGENER TASK:
- Type: {task.get('type', 'unknown')}
- Description: {task.get('description', 'N/A')}
- Expected: {task.get('expected', 'N/A')}

FEHLER RESULTAT:
- Error Type: {result.get('error_type', result.get('error', 'N/A'))}
- Detail: {result.get('detail', result.get('error', 'N/A'))[:300]}

Schreibe eine präzise Selbstkritik (3-5 Sätze):
1. Was ist konkret schief gelaufen?
2. Warum ist es schief gelaufen?
3. Was hätte ich anders machen sollen?
4. Wie kann ich es nächstes Mal besser machen?

Antworte auf Deutsch, professionell und präzise.
"""
        
        # Call LLM (placeholder — depends on API)
        # For now, fall back to rule-based
        return self._generate_rule_based_critique(task, result)
    
    def _generate_rule_based_critique(self, task: Dict, result: Dict) -> str:
        """Generate rule-based critique when LLM unavailable."""
        error_type = result.get("error_type", result.get("error", "unknown"))
        task_type = task.get("type", "unknown")
        
        # Template critiques by error type
        critiques = {
            "timeout": (
                "Der Task wurde wegen Timeout abgebrochen. "
                "Das System hat zu lange auf eine Antwort gewartet. "
                "Nächstes Mal: Timeout-Wert erhöhen oder Task in kleinere Schritte aufteilen."
            ),
            "validation_failed": (
                "Die Validierung des Ergebnisses ist fehlgeschlagen. "
                "Das System hat ein Ergebnis geliefert, das die Quality Checks nicht besteht. "
                "Nächstes Mal: Validierung vor Output durchführen, nicht nur danach."
            ),
            "api_error": (
                "Ein API-Fehler ist aufgetreten. "
                "Das System hat eine Exception bei einem externen Aufruf erhalten. "
                "Nächstes Mal: API-Fehlerhandling verbessern, Retry-Logik implementieren."
            ),
            "syntax_error": (
                "Ein Syntax-Fehler im Code. "
                "Das System hat Code geschrieben, der nicht ausführbar ist. "
                "Nächstes Mal: Code-Syntax vor Ausführung prüfen, Linter nutzen."
            ),
            "logic_error": (
                "Ein Logik-Fehler: Der Code läuft, macht aber das Falsche. "
                "Das System hat die Aufgabe semantisch missverstanden. "
                "Nächstes Mal: Task genauer analysieren, Zwischenergebnisse prüfen."
            ),
        }
        
        base_critique = critiques.get(
            error_type, 
            f"Unbekannter Fehler bei Task-Type '{task_type}'. "
            f"Fehler: {result.get('error', result.get('error_type', 'N/A'))}. "
            f"Das System muss generic Fehlerbehandlung verbessern."
        )
        
        return base_critique
    
    def retrieve(self, task_type: Optional[str] = None, error_type: Optional[str] = None, limit: int = 3) -> List[Dict]:
        """
        Retrieve relevant past reflections.
        
        Sources:
        1. Local reflection store (fast, exact match)
        2. KG (semantic, linked to categories)
        
        Args:
            task_type: Filter by task type
            error_type: Filter by error type
            limit: Maximum number to return
        
        Returns:
            List of relevant reflection entries
        """
        all_candidates = []
        
        # Source 1: Local store
        candidates = self.reflections
        if task_type:
            candidates = [r for r in candidates if r.get("task_type") == task_type]
        if error_type:
            candidates = [r for r in candidates if r.get("error_type") == error_type]
        candidates = [r for r in candidates if not r.get("resolved")]
        
        for r in candidates:
            r["_source"] = "local"
            all_candidates.append(r)
        
        # Source 2: KG (for semantic retrieval)
        try:
            kg_refs = self._get_kg_reflections(task_type, error_type, limit)
            for kg_r in kg_refs:
                kg_r["_source"] = "kg"
                all_candidates.append(kg_r)
        except Exception as e:
            pass  # KG retrieval is best-effort
        
        # Deduplicate by ID (prefer local over KG)
        seen = set()
        result = []
        for r in all_candidates:
            rid = r.get("id", "")
            if rid not in seen:
                seen.add(rid)
                result.append(r)
        
        # Sort by utility: use_count * 5 - age_days
        scored = []
        for r in result:
            last_used = r.get("last_used", r.get("created_at", ""))
            try:
                age_days = (datetime.now() - datetime.fromisoformat(last_used.replace("Z", "+00:00"))).days
            except:
                age_days = 0
            score = r.get("use_count", 0) * 5 - age_days
            scored.append((score, r))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        result = [r for _, r in scored[:limit]]
        
        # Update use_count for retrieved reflections
        for r in result:
            rid = r.get("id", "")
            # Update local store
            for lr in self.reflections:
                if lr.get("id") == rid:
                    lr["use_count"] = lr.get("use_count", 0) + 1
                    lr["last_used"] = datetime.utcnow().isoformat() + "Z"
            # Update KG entity
            if r.get("_source") == "kg":
                self._increment_kg_use_count(rid)
        
        save_reflections(self.reflections)
        
        return result
    
    def _increment_kg_use_count(self, entity_id: str):
        """Increment use_count in KG entity."""
        try:
            kg = self._load_kg()
            if entity_id in kg.get("entities", {}):
                props = kg["entities"][entity_id].get("properties", {})
                props["use_count"] = props.get("use_count", 0) + 1
                kg["entities"][entity_id]["properties"] = props
                self._save_kg(kg)
        except:
            pass
    
    def mark_resolved(self, reflection_id: str):
        """Mark a reflection as resolved (problem solved)."""
        for r in self.reflections:
            if r["id"] == reflection_id:
                r["resolved"] = True
                r["resolved_at"] = datetime.utcnow().isoformat() + "Z"
        save_reflections(self.reflections)
    
    def stats(self) -> Dict:
        """Get reflection store statistics."""
        total = len(self.reflections)
        by_type = defaultdict(int)
        by_error = defaultdict(int)
        resolved = 0
        
        for r in self.reflections:
            by_type[r.get("task_type", "unknown")] += 1
            by_error[r.get("error_type", "unknown")] += 1
            if r.get("resolved"):
                resolved += 1
        
        return {
            "total": total,
            "resolved": resolved,
            "by_task_type": dict(by_type),
            "by_error_type": dict(by_error),
            "retrievable": sum(1 for r in self.reflections if not r.get("resolved")),
        }


def main():
    parser = argparse.ArgumentParser(description="Reflection Engine — Self-Reflection for Sir HazeClaw")
    subparsers = parser.add_subparsers(dest="command")
    
    # Reflect command
    reflect_parser = subparsers.add_parser("reflect", help="Generate reflection for failed task")
    reflect_parser.add_argument("--task", required=True, help="JSON task file")
    reflect_parser.add_argument("--result", required=True, help="JSON result file")
    
    # Retrieve command
    retrieve_parser = subparsers.add_parser("retrieve", help="Retrieve relevant reflections")
    retrieve_parser.add_argument("--type", help="Task type filter")
    retrieve_parser.add_argument("--error", help="Error type filter")
    retrieve_parser.add_argument("--limit", type=int, default=3)
    
    # Stats command
    subparsers.add_parser("stats", help="Show reflection store statistics")
    
    args = parser.parse_args()
    
    if args.command == "reflect":
        task = json.load(open(args.task))
        result = json.load(open(args.result))
        engine = ReflectionEngine()
        reflection = engine.reflect(task, result)
        print(f"Generated reflection: {reflection['id']}")
        print(f"Critique: {reflection.get('critique', 'N/A')[:200]}...")
    
    elif args.command == "retrieve":
        engine = ReflectionEngine()
        results = engine.retrieve(args.type, args.error, args.limit)
        print(f"Found {len(results)} relevant reflections:")
        for r in results:
            print(f"  [{r['id']}] {r.get('task_type', '?')} - {r.get('error_type', '?')}")
            print(f"    Critique: {r.get('critique', 'N/A')[:100]}...")
    
    elif args.command == "stats":
        engine = ReflectionEngine()
        s = engine.stats()
        print(f"Reflection Store Statistics:")
        print(f"  Total: {s['total']}")
        print(f"  Resolved: {s['resolved']}")
        print(f"  Retrievable: {s['retrievable']}")
        print(f"  By Task Type: {s['by_task_type']}")
        print(f"  By Error Type: {s['by_error_type']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
