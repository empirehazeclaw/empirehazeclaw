#!/usr/bin/env python3
"""
meta_kg_query_interface.py — Phase 4: Meta-KG Query Interface
=============================================================
Query-Interface für Meta-Learning via KG.
Einfaches Interface für Meta-Learning Queries.

Usage:
    python3 meta_kg_query_interface.py --ask <question>   # Query KG
    python3 meta_kg_query_interface.py --recommend <task> # Get recommendation
    python3 meta_kg_query_interface.py --status           # Show interface status
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
KG_DIR = WORKSPACE / 'memory/kg'
PATTERNS_FILE = WORKSPACE / 'memory/meta_learning/meta_patterns.json'
WEIGHTS_FILE = WORKSPACE / 'memory/meta_learning/algorithm_weights.json'


class MetaKGQueryInterface:
    """Query interface for meta-learning via KG."""
    
    def __init__(self):
        self.kg_entities = []
        self.kg_relations = []
        self.patterns = []
        self.weights = {}
        self.load_data()
    
    def load_data(self):
        """Load required data."""
        # Load KG
        kg_file = KG_DIR / 'knowledge_graph.json'
        if kg_file.exists():
            with open(kg_file, 'r') as f:
                data = json.load(f)
            
            # Entities can be dict or list - normalize to list
            entities_data = data.get('entities', {})
            if isinstance(entities_data, dict):
                self.kg_entities = []
                for entity_id, entity in entities_data.items():
                    if isinstance(entity, dict):
                        entity['id'] = entity.get('id', entity_id)
                        self.kg_entities.append(entity)
            else:
                self.kg_entities = entities_data if isinstance(entities_data, list) else []
            
            # Relations can be dict or list - normalize
            relations_data = data.get('relations', data.get('relationships', {}))
            if isinstance(relations_data, dict):
                self.kg_relations = []
                for source, targets in relations_data.items():
                    if isinstance(targets, list):
                        for target in targets:
                            self.kg_relations.append({'source': source, 'target': target, 'type': 'related'})
                    elif isinstance(targets, dict):
                        for rel_type, target_list in targets.items():
                            if isinstance(target_list, list):
                                for target in target_list:
                                    self.kg_relations.append({'source': source, 'target': target, 'type': rel_type})
            else:
                self.kg_relations = relations_data if isinstance(relations_data, list) else []
        else:
            self.kg_relations = []
        
        # Load patterns
        if PATTERNS_FILE.exists():
            with open(PATTERNS_FILE, 'r') as f:
                data = json.load(f)
            self.patterns = data.get('patterns', [])
        
        # Load weights
        if WEIGHTS_FILE.exists():
            with open(WEIGHTS_FILE, 'r') as f:
                data = json.load(f)
            self.weights = data.get('weights', {})
        
        print(f"📂 Loaded: {len(self.kg_entities)} entities, {len(self.patterns)} patterns")
    
    def query(self, question):
        """Query the meta-KG with a question."""
        print(f"\n🔍 Meta-KG Query: {question}")
        print("=" * 50)
        
        # Parse question type
        question_lower = question.lower()
        
        if 'task' in question_lower or 'what' in question_lower:
            return self.query_task_recommendation(question)
        elif 'pattern' in question_lower or 'learn' in question_lower:
            return self.query_pattern_insights(question)
        elif 'agent' in question_lower or 'who' in question_lower:
            return self.query_agent_recommendation(question)
        elif 'best' in question_lower or 'success' in question_lower:
            return self.query_best_practices(question)
        else:
            return self.query_general(question)
    
    def query_task_recommendation(self, question):
        """Get task execution recommendation."""
        print("\n📋 Task Recommendation Query")
        
        # Find relevant patterns
        relevant_patterns = []
        for pattern in self.patterns:
            desc = pattern.get('description', '').lower()
            if any(x in desc for x in ['direct', 'execution', 'task', 'fast']):
                relevant_patterns.append(pattern)
        
        if relevant_patterns:
            best = max(relevant_patterns, key=lambda p: p.get('success_rate', 0) * p.get('generalization_score', 0))
            print(f"\n💡 Recommendation:")
            print(f"   Based on patterns, the best approach is:")
            print(f"   {best.get('description')}")
            print(f"   Confidence: {best.get('success_rate', 0):.0%}")
            return best
        
        return None
    
    def query_pattern_insights(self, question):
        """Query pattern insights from KG."""
        print("\n🔍 Pattern Insights Query")
        
        print(f"\n📊 Available Patterns: {len(self.patterns)}")
        
        cross_task = [p for p in self.patterns if p.get('cross_task_valid', False)]
        print(f"   Cross-task valid: {len(cross_task)}")
        
        high_conf = [p for p in self.patterns if p.get('success_rate', 0) >= 1.0]
        print(f"   High confidence: {len(high_conf)}")
        
        if cross_task:
            print(f"\n💡 Best cross-task pattern:")
            best = max(cross_task, key=lambda p: p.get('generalization_score', 0))
            print(f"   {best.get('pattern_id')}: {best.get('description')}")
        
        return cross_task
    
    def query_agent_recommendation(self, question):
        """Query agent recommendation."""
        print("\n🤖 Agent Recommendation Query")
        
        # Find agent-specific patterns
        agent_patterns = {}
        for pattern in self.patterns:
            trigger = pattern.get('trigger', {})
            if 'delegated_to' in trigger:
                agent = trigger['delegated_to']
                if agent:
                    if agent not in agent_patterns:
                        agent_patterns[agent] = []
                    agent_patterns[agent].append(pattern)
        
        print(f"\n📋 Agent Performance Patterns:")
        for agent, patterns in sorted(agent_patterns.items(), key=lambda x: -len(x[1])):
            if patterns:
                avg_success = sum(p.get('success_rate', 1.0) for p in patterns) / len(patterns)
                print(f"   {agent}: {len(patterns)} patterns, {avg_success:.0%} avg success")
        
        return agent_patterns
    
    def query_best_practices(self, question):
        """Query best practices."""
        print("\n🏆 Best Practices Query")
        
        # Find highest performing patterns
        sorted_patterns = sorted(
            self.patterns,
            key=lambda p: (p.get('success_rate', 0), p.get('matching_tasks', 0)),
            reverse=True
        )
        
        print(f"\n🏆 Top 3 Patterns by Success Rate + Coverage:")
        for i, p in enumerate(sorted_patterns[:3], 1):
            print(f"   {i}. {p.get('pattern_id')}")
            print(f"      {p.get('description')[:60]}")
            print(f"      Success: {p.get('success_rate', 0):.0%} | Tasks: {p.get('matching_tasks', 0)}")
        
        return sorted_patterns[:3]
    
    def query_general(self, question):
        """General query."""
        print("\n🔍 General Query")
        print(f"   KG has {len(self.kg_entities)} entities")
        print(f"   Patterns: {len(self.patterns)}")
        print(f"   Relations: {len(self.kg_relations)}")
        
        return {
            'entities': len(self.kg_entities),
            'patterns': len(self.patterns),
            'relations': len(self.kg_relations)
        }
    
    def recommend_for_task(self, task_description):
        """Get recommendation for a task description."""
        print(f"\n🎯 Task Recommendation for: {task_description[:50]}...")
        print("=" * 50)
        
        # Classify the task
        task_lower = task_description.lower()
        
        # Determine task type
        if 'health' in task_lower or 'check' in task_lower:
            task_type = 'health_check'
        elif 'research' in task_lower or 'search' in task_lower:
            task_type = 'research'
        elif 'learning' in task_lower or 'sync' in task_lower:
            task_type = 'learning_sync'
        elif 'data' in task_lower or 'process' in task_lower:
            task_type = 'data_processing'
        else:
            task_type = 'general'
        
        print(f"   Detected task type: {task_type}")
        
        # Find matching patterns
        matching_patterns = []
        for pattern in self.patterns:
            trigger = pattern.get('trigger', {})
            if 'subtype' in trigger:
                if trigger['subtype'] == task_type:
                    matching_patterns.append(pattern)
        
        # Find matching agent weights
        agent_weights = {}
        for key, value in self.weights.items():
            if task_type in key:
                agent_weights[key] = value
        
        print(f"\n📋 Matching Patterns: {len(matching_patterns)}")
        for p in matching_patterns[:3]:
            print(f"   - {p.get('description')[:60]}")
            print(f"     Success: {p.get('success_rate', 0):.0%}")
        
        print(f"\n⚙️ Routing Weights for {task_type}:")
        for key, value in self.weights.items():
            if task_type in key or key == 'default':
                print(f"   {key}: {value:.2f}")
        
        # Generate recommendation
        if matching_patterns:
            best_pattern = max(matching_patterns, key=lambda p: p.get('success_rate', 0))
            recommended_route = best_pattern.get('action', {}).get('approach', 'direct')
        else:
            recommended_route = 'direct'
        
        print(f"\n✅ Recommended Route: {recommended_route}")
        
        return {
            'task_type': task_type,
            'patterns_found': len(matching_patterns),
            'recommended_route': recommended_route,
            'matching_patterns': matching_patterns[:3]
        }
    
    def status(self):
        """Show interface status."""
        print("🎯 Meta-KG Query Interface Status")
        print("=" * 50)
        print(f"KG Entities: {len(self.kg_entities)}")
        print(f"Patterns: {len(self.patterns)}")
        print(f"Weight parameters: {len(self.weights)}")
        print(f"Relations: {len(self.kg_relations)}")


def main():
    interface = MetaKGQueryInterface()
    
    if '--status' in sys.argv:
        interface.status()
        return
    
    ask_text = None
    recommend_text = None
    
    if '--ask' in sys.argv:
        idx = sys.argv.index('--ask')
        if idx + 1 < len(sys.argv):
            ask_text = sys.argv[idx + 1]
    
    if '--recommend' in sys.argv:
        idx = sys.argv.index('--recommend')
        if idx + 1 < len(sys.argv):
            recommend_text = sys.argv[idx + 1]
    
    if ask_text:
        interface.query(ask_text)
    elif recommend_text:
        interface.recommend_for_task(recommend_text)
    else:
        interface.status()


if __name__ == '__main__':
    main()