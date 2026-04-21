#!/usr/bin/env python3
"""
Dynamic Experience Memory — Phase 4, Day 3
==========================================
Implements HealthFlow-inspired experience memory:
M = {E1, E2, ..., EN} with forgetting mechanism

Features:
- Dynamic experience storage
- Spaced repetition for memory consolidation
- Forgetting mechanism for obsolete experiences
- Experience replay for learning

Usage:
    python3 dynamic_experience_memory.py --add "<exp>"   # Add experience
    python3 dynamic_experience_memory.py --replay       # Replay recent experiences
    python3 dynamic_experience_memory.py --consolidate  # Consolidate memories
    python3 dynamic_experience_memory.py --forget       # Run forgetting
    python3 dynamic_experience_memory.py --status       # Show memory status
    python3 dynamic_experience_memory.py --search <q>  # Search experiences
"""

import json
import argparse
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import deque, defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
MEM_DIR = WORKSPACE / "memory" / "experiences"
MEM_FILE = MEM_DIR / "experience_memory.json"
CONFIG_FILE = MEM_DIR / "memory_config.json"

# Default configuration
DEFAULT_CONFIG = {
    "max_experiences": 500,          # Maximum experiences to store
    "consolidation_interval_hours": 24,  # How often to consolidate
    "forgetting_threshold": 0.2,     # Importance below this gets forgotten
    "decay_rate_per_day": 0.05,      # How fast importance decays
    "boost_on_access": 0.1,          # Importance boost when accessed
    "min_importance": 0.1,           # Minimum importance before deletion
    "replay_sample_size": 10,         # How many to replay
    "version": "1.0"
}

def init_dirs():
    MEM_DIR.mkdir(parents=True, exist_ok=True)
    
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
    
    if not MEM_FILE.exists():
        MEM_FILE.write_text(json.dumps({
            "experiences": [],
            "index": {},
            "consolidation_log": [],
            "version": "1.0"
        }))

def load_config():
    init_dirs()
    return json.loads(CONFIG_FILE.read_text())

def save_config(config):
    CONFIG_FILE.write_text(json.dumps(config, indent=2))

def load_memory():
    init_dirs()
    return json.loads(MEM_FILE.read_text())

def save_memory(memory):
    MEM_FILE.write_text(json.dumps(memory, indent=2))

def calculate_importance(experience: dict, memory: dict) -> float:
    """Calculate current importance score for an experience."""
    base_importance = experience.get("importance", 0.5)
    
    # Recency factor
    created = experience.get("created_at", "")
    if created:
        try:
            days_old = (datetime.now(timezone.utc) - datetime.fromisoformat(created.replace("Z", "+00:00"))).days
            recency_factor = max(0.5, 1 - days_old * 0.02)  # Lose 2% per day, min 50%
        except:
            recency_factor = 0.5
    else:
        recency_factor = 0.5
    
    # Access frequency factor
    access_count = experience.get("access_count", 1)
    access_factor = min(1.5, 1 + access_count * 0.05)  # Max 1.5x boost
    
    # Reinforcement factor
    reinforcement = experience.get("reinforcement", 0)
    reinforcement_factor = 1 + reinforcement * 0.1
    
    # Calculate final importance
    importance = base_importance * recency_factor * access_factor * reinforcement_factor
    
    return min(importance, 1.0)

def add_experience(description: str, experience_type: str = "general", 
                   importance: float = 0.5, context: dict = None, 
                   outcome: str = None, tags: list = None) -> dict:
    """Add a new experience to memory."""
    config = load_config()
    memory = load_memory()
    
    exp_id = f"EXP-{len(memory['experiences']) + 1:05d}"
    now = datetime.now(timezone.utc).isoformat()
    
    experience = {
        "id": exp_id,
        "description": description,
        "type": experience_type,
        "importance": importance,
        "context": context or {},
        "outcome": outcome,
        "tags": tags or [],
        "created_at": now,
        "last_accessed": now,
        "access_count": 1,
        "reinforcement": 0,
        "decay_count": 0,
        "consolidated": False
    }
    
    # Add to experiences
    memory["experiences"].append(experience)
    
    # Update index
    for tag in experience["tags"]:
        if tag not in memory["index"]:
            memory["index"][tag] = []
        memory["index"][tag].append(exp_id)
    
    # Update type index
    if experience_type not in memory["index"]:
        memory["index"][experience_type] = []
    memory["index"][experience_type].append(exp_id)
    
    # Enforce max size
    if len(memory["experiences"]) > config["max_experiences"]:
        run_forgetting(memory, config)
    
    save_memory(memory)
    
    print(f"✅ Added experience {exp_id}: {description[:50]}...")
    print(f"   Type: {experience_type} | Importance: {importance:.2f}")
    
    return experience

def access_experience(exp_id: str) -> dict:
    """Access and reinforce an experience."""
    memory = load_memory()
    config = load_config()
    
    for exp in memory["experiences"]:
        if exp["id"] == exp_id:
            exp["access_count"] += 1
            exp["last_accessed"] = datetime.now(timezone.utc).isoformat()
            
            # Boost importance slightly
            exp["importance"] = min(1.0, exp["importance"] + config["boost_on_access"])
            
            save_memory(memory)
            print(f"📖 Accessed {exp_id}: {exp['description'][:50]}...")
            return exp
    
    print(f"❌ Experience {exp_id} not found.")
    return None

def replay_experiences(n: int = None, experience_type: str = None) -> list:
    """Replay experiences (for learning)."""
    config = load_config()
    memory = load_memory()
    
    sample_size = n or config["replay_sample_size"]
    
    # Filter by type if specified
    candidates = memory["experiences"]
    if experience_type:
        candidates = [e for e in candidates if e.get("type") == experience_type]
    
    # Sort by importance (highest first)
    for exp in candidates:
        exp["current_importance"] = calculate_importance(exp, memory)
    
    candidates.sort(key=lambda x: -x["current_importance"])
    
    # Sample
    to_replay = candidates[:sample_size]
    
    print(f"\n🔄 Replaying {len(to_replay)} experiences (from {len(candidates)} total)\n")
    for i, exp in enumerate(to_replay, 1):
        imp = exp["current_importance"]
        bar = "█" * int(imp * 10) + "░" * (10 - int(imp * 10))
        print(f"  {i}. [{bar}] {imp:.2f} | {exp['description'][:50]}")
        print(f"     Type: {exp.get('type', 'general')} | Accesses: {exp.get('access_count', 0)}")
        if exp.get("outcome"):
            print(f"     Outcome: {exp['outcome'][:50]}")
        print()
    
    # Reinforce replayed experiences
    for exp in to_replay:
        exp_id = exp["id"]
        for e in memory["experiences"]:
            if e["id"] == exp_id:
                e["reinforcement"] += 1
                break
    
    save_memory(memory)
    return to_replay

def run_forgetting(memory: dict = None, config: dict = None):
    """Run forgetting mechanism - remove low importance experiences."""
    if memory is None:
        memory = load_memory()
    if config is None:
        config = load_config()
    
    before_count = len(memory["experiences"])
    
    # Calculate importance for all and mark for deletion
    to_delete = []
    
    for exp in memory["experiences"]:
        current_importance = calculate_importance(exp, memory)
        exp["current_importance"] = current_importance
        
        days_old = 0
        created = exp.get("created_at", "")
        if created:
            try:
                days_old = (datetime.now(timezone.utc) - datetime.fromisoformat(created.replace("Z", "+00:00"))).days
            except:
                pass
        
        # Forgetting conditions
        should_forget = (
            current_importance < config["min_importance"] or
            (current_importance < config["forgetting_threshold"] and days_old > 7) or
            (exp.get("access_count", 1) == 1 and days_old > 14)  # Single access, old
        )
        
        if should_forget:
            to_delete.append(exp["id"])
            exp["decay_count"] += 1
    
    # Remove lowest importance if still over max
    if len(memory["experiences"]) - len(to_delete) > config["max_experiences"] * 0.8:
        # Sort by importance
        sorted_exps = sorted(memory["experiences"], key=lambda x: calculate_importance(x, memory))
        to_delete.extend([e["id"] for e in sorted_exps[:5]])
    
    # Actually delete
    original_count = len(memory["experiences"])
    memory["experiences"] = [e for e in memory["experiences"] if e["id"] not in to_delete]
    
    # Rebuild index
    memory["index"] = {}
    for exp in memory["experiences"]:
        for tag in exp.get("tags", []):
            if tag not in memory["index"]:
                memory["index"][tag] = []
            memory["index"][tag].append(exp["id"])
        exp_type = exp.get("type", "general")
        if exp_type not in memory["index"]:
            memory["index"][exp_type] = []
        memory["index"][exp_type].append(exp["id"])
    
    deleted = original_count - len(memory["experiences"])
    
    if deleted > 0:
        print(f"🧹 Forgetting: Removed {deleted} low-importance experiences")
        print(f"   Remaining: {len(memory['experiences'])}")
    
    save_memory(memory)
    return deleted

def consolidate_memories():
    """Consolidate similar experiences and strengthen patterns."""
    memory = load_memory()
    config = load_config()
    
    before_count = len(memory["experiences"])
    
    # Group similar experiences by type and tags
    groups = defaultdict(list)
    for exp in memory["experiences"]:
        key = exp.get("type", "general")
        tags = tuple(sorted(exp.get("tags", [])))
        groups[(key, tags)].append(exp)
    
    consolidated_count = 0
    
    for (exp_type, tags), experiences in groups.items():
        if len(experiences) < 2:
            continue
        
        # Find most important
        for exp in experiences:
            exp["current_importance"] = calculate_importance(exp, memory)
        
        experiences.sort(key=lambda x: -x["current_importance"])
        strongest = experiences[0]
        
        # Merge insights from others
        merged_insights = [strongest.get("description", "")]
        outcomes = set()
        
        for exp in experiences[1:]:
            if exp.get("outcome"):
                outcomes.add(exp["outcome"])
            if exp.get("description"):
                merged_insights.append(exp["description"][:50])
        
        # Update strongest with merged info
        strongest["reinforcement"] = sum(e.get("reinforcement", 0) for e in experiences)
        strongest["access_count"] = max(e.get("access_count", 1) for e in experiences)
        strongest["merged_from"] = len(experiences) - 1
        strongest["outcomes"] = list(outcomes)
        strongest["consolidated"] = True
        strongest["last_consolidated"] = datetime.now(timezone.utc).isoformat()
        
        consolidated_count += len(experiences) - 1
    
    # Log consolidation
    memory["consolidation_log"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "before_count": before_count,
        "after_count": len(memory["experiences"]),
        "consolidated": consolidated_count
    })
    
    # Keep only last 100 consolidation logs
    memory["consolidation_log"] = memory["consolidation_log"][-100:]
    
    # Run forgetting after consolidation
    run_forgetting(memory, config)
    
    print(f"✅ Consolidation complete: {consolidated_count} experiences merged")
    print(f"   Total experiences: {len(memory['experiences'])}")
    
    save_memory(memory)
    return memory

def show_status():
    """Show memory status."""
    config = load_config()
    memory = load_memory()
    
    exp_count = len(memory["experiences"])
    
    # Calculate stats
    total_importance = sum(calculate_importance(e, memory) for e in memory["experiences"])
    avg_importance = total_importance / max(exp_count, 1)
    
    # Count by type
    by_type = defaultdict(int)
    for exp in memory["experiences"]:
        by_type[exp.get("type", "general")] += 1
    
    # Recent experiences
    recent = sorted(memory["experiences"], key=lambda x: x.get("created_at", ""), reverse=True)[:5]
    
    # Last consolidation
    last_consolidation = memory.get("consolidation_log", [])[-1] if memory.get("consolidation_log") else None
    
    print(f"""
🧠 Dynamic Experience Memory Status
{'=' * 45}
Configuration:
  Max Experiences:     {config['max_experiences']}
  Decay Rate/Day:     {config['decay_rate_per_day']:.2%}
  Forgetting Thresh:  {config['forgetting_threshold']:.2%}
  Replay Sample:      {config['replay_sample_size']}

Memory:
  Total Experiences:  {exp_count}
  Avg Importance:     {avg_importance:.2f}
  Capacity Used:      {exp_count / config['max_experiences']:.1%}

By Type:
""")
    for exp_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {exp_type}: {count}")
    
    print(f"""
Recent Experiences:
""")
    for exp in recent:
        imp = calculate_importance(exp, memory)
        print(f"  • {exp['id']} | {exp['description'][:40]}... | imp={imp:.2f}")
    
    if last_consolidation:
        print(f"""
Last Consolidation:
  {last_consolidation['timestamp'][:19]}
  Before: {last_consolidation['before_count']} | After: {last_consolidation['after_count']}
""")

def search_experiences(query: str) -> list:
    """Search experiences by description, tags, or type."""
    memory = load_memory()
    
    query_lower = query.lower()
    results = []
    
    for exp in memory["experiences"]:
        # Check description
        if query_lower in exp.get("description", "").lower():
            results.append(exp)
            continue
        
        # Check tags
        if any(query_lower in tag.lower() for tag in exp.get("tags", [])):
            results.append(exp)
            continue
        
        # Check type
        if query_lower in exp.get("type", "").lower():
            results.append(exp)
            continue
    
    if not results:
        print(f"📭 No experiences found matching '{query}'")
        return []
    
    print(f"\n🔍 Found {len(results)} experiences matching '{query}':\n")
    for exp in sorted(results, key=lambda x: -calculate_importance(x, memory))[:10]:
        imp = calculate_importance(exp, memory)
        print(f"  [{exp['id']}] {exp['description'][:60]}")
        print(f"       Type: {exp.get('type', 'general')} | Importance: {imp:.2f}")
        print(f"       Tags: {', '.join(exp.get('tags', []) or ['none'])}")
        print()
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Dynamic Experience Memory")
    parser.add_argument("--add", metavar="DESC", help="Add experience")
    parser.add_argument("--type", default="general", help="Experience type")
    parser.add_argument("--importance", type=float, default=0.5, help="Importance 0-1")
    parser.add_argument("--outcome", help="Outcome description")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--replay", action="store_true", help="Replay experiences")
    parser.add_argument("--n", type=int, help="Number to replay")
    parser.add_argument("--consolidate", action="store_true", help="Consolidate memories")
    parser.add_argument("--forget", action="store_true", help="Run forgetting")
    parser.add_argument("--status", action="store_true", help="Show memory status")
    parser.add_argument("--search", metavar="QUERY", help="Search experiences")
    parser.add_argument("--access", metavar="EXP_ID", help="Access experience")
    
    args = parser.parse_args()
    
    init_dirs()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    if args.add:
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        add_experience(
            description=args.add,
            experience_type=args.type,
            importance=args.importance,
            outcome=args.outcome,
            tags=tags
        )
    
    if args.access:
        access_experience(args.access)
    
    if args.replay:
        replay_experiences(n=args.n)
    
    if args.consolidate:
        consolidate_memories()
    
    if args.forget:
        run_forgetting()
    
    if args.status:
        show_status()
    
    if args.search:
        search_experiences(args.search)

if __name__ == "__main__":
    main()
