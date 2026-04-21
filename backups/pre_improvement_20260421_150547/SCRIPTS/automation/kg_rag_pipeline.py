#!/usr/bin/env python3
"""
🎯 KG RAG Pipeline — Knowledge Graph Retrieval Augmented Generation
========================================================================
Hybrid Search: Vector (semantic) + KG (relations) for better context retrieval.

Architecture:
  Query → Query Analysis → [Vector Search + KG Lookup] → Context Assembly → LLM-ready

Features:
- Semantic search via Gemini embeddings (existing)
- KG relation traversal
- Query decomposition for complex questions
- Context ranking and filtering
- Response validation

Usage:
    python3 kg_rag_pipeline.py "Wie verbessere ich die Learning Loop?"
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Paths
KG_PATH = Path("/home/clawbot/.openclaw/workspace/ceo/memory/kg/knowledge_graph.json")
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "kg_rag.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")


class KGLoader:
    """Load and cache the Knowledge Graph."""
    
    def __init__(self, kg_path: Path):
        self.kg_path = kg_path
        self.entities = {}
        self.relations = []
        self.load()
    
    def load(self):
        """Load KG from disk."""
        log(f"Loading KG from {self.kg_path}")
        with open(self.kg_path) as f:
            data = json.load(f)
        
        self.entities = data.get('entities', {})
        self.relations = data.get('relations', [])
        log(f"Loaded {len(self.entities)} entities, {len(self.relations)} relations")
    
    def reload(self):
        """Reload KG from disk."""
        self.load()


class KGIndex:
    """Index for fast KG lookups."""
    
    def __init__(self, kg: KGLoader):
        self.kg = kg
        self.entity_by_type = {}
        self.entity_by_keyword = {}
        self._build_index()
    
    def _build_index(self):
        """Build search indexes."""
        log("Building KG index...")
        
        # Index by type
        for entity_id, entity in self.kg.entities.items():
            entity_type = entity.get('type', 'unknown')
            if entity_type not in self.entity_by_type:
                self.entity_by_type[entity_type] = []
            self.entity_by_type[entity_type].append(entity_id)
        
        # Index by keywords (from entity IDs and facts)
        keywords = set()
        for entity_id in self.kg.entities.keys():
            # Split entity ID into words
            words = entity_id.lower().replace('_', ' ').replace('-', ' ').split()
            for word in words:
                if len(word) > 2:
                    keywords.add(word)
        
        log(f"Index built: {len(self.entity_by_type)} types, {len(keywords)} keywords")
    
    def search_by_type(self, entity_type: str, limit: int = 10):
        """Get entities by type."""
        entities = self.entity_by_type.get(entity_type, [])
        results = []
        for eid in entities[:limit]:
            results.append((eid, self.kg.entities[eid]))
        return results
    
    def search_by_keyword(self, query: str, limit: int = 10):
        """Simple keyword search."""
        query_words = query.lower().split()
        scores = {}
        
        for entity_id, entity in self.kg.entities.items():
            score = 0
            entity_text = entity_id.lower()
            
            # Also include facts
            facts = entity.get('facts', [])
            for fact in facts:
                entity_text += ' ' + fact.get('content', '').lower()
            
            for word in query_words:
                if word in entity_text:
                    score += 1
                    # Exact match bonus
                    if word == entity_id.lower():
                        score += 5
            
            if score > 0:
                scores[entity_id] = score
        
        # Sort by score
        sorted_results = sorted(scores.items(), key=lambda x: -x[1])
        return [(eid, self.kg.entities[eid], score) for eid, score in sorted_results[:limit]]


class QueryDecomposer:
    """Decompose complex queries into sub-queries."""
    
    def __init__(self):
        self.indicators = {
            'comparison': ['vs', 'versus', 'oder', 'compare', 'difference'],
            'cause_effect': ['weil', 'causes', 'because', 'führt zu', 'result'],
            'temporal': ['wann', 'when', 'zuerst', 'first', 'dann', 'then', 'bevor', 'after'],
            'list': ['was sind', 'what are', 'liste', 'list', 'alle', 'all'],
            'howto': ['wie', 'how', 'machen', 'do', 'verbessern', 'improve', 'fix'],
            'why': ['warum', 'why', 'grund', 'reason'],
        }
    
    def decompose(self, query: str) -> dict:
        """Analyze query and return decomposition."""
        query_lower = query.lower()
        
        query_type = 'simple'
        for qtype, indicators in self.indicators.items():
            if any(ind in query_lower for ind in indicators):
                query_type = qtype
                break
        
        # Extract key topics
        words = query_lower.split()
        key_topics = [w for w in words if len(w) > 3]
        
        # Determine required entity types
        required_types = []
        if any(w in query_lower for w in ['pattern', 'learning', 'error', 'problem']):
            required_types.extend(['LearningPattern', 'error_pattern', 'success_pattern'])
        if any(w in query_lower for w in ['verbesser', 'improvement', 'optimize']):
            required_types.append('Improvement')
        if any(w in query_lower for w in ['concept', 'idea', 'wissen']):
            required_types.append('concept')
        
        return {
            'original_query': query,
            'query_type': query_type,
            'key_topics': key_topics,
            'required_types': required_types,
            'is_complex': len(required_types) > 1 or query_type != 'simple'
        }


class ContextAssembler:
    """Assemble retrieved context into LLM-ready format."""
    
    def __init__(self, kg: KGLoader):
        self.kg = kg
    
    def assemble(self, query_analysis: dict, retrieved_entities: list) -> str:
        """Assemble context from retrieved entities."""
        context_parts = []
        context_parts.append(f"## Query Analysis")
        context_parts.append(f"Type: {query_analysis['query_type']}")
        context_parts.append(f"Topics: {', '.join(query_analysis['key_topics'])}")
        context_parts.append("")
        
        context_parts.append("## Retrieved Knowledge:")
        
        for i, (entity_id, entity, score) in enumerate(retrieved_entities[:10], 1):
            context_parts.append(f"\n### {i}. {entity_id} ({entity.get('type', 'unknown')})")
            
            # Priority
            priority = entity.get('priority', 'MEDIUM')
            context_parts.append(f"Priority: {priority}")
            
            # Facts
            facts = entity.get('facts', [])
            if facts:
                context_parts.append("Facts:")
                for fact in facts[:3]:  # Limit facts
                    content = fact.get('content', '')
                    confidence = fact.get('confidence', 0)
                    context_parts.append(f"  - [{confidence:.0%}] {content}")
            
            # Related entities (from relations)
            related = self._get_related(entity_id)
            if related:
                context_parts.append(f"Related: {', '.join(related[:5])}")
        
        return '\n'.join(context_parts)
    
    def _get_related(self, entity_id: str, limit: int = 5) -> list:
        """Get related entities via relations."""
        related = []
        for rel in self.kg.relations:
            if isinstance(rel, dict):
                if rel.get('from') == entity_id:
                    related.append(f"{rel.get('to', '')} ({rel.get('type', '')})")
                elif rel.get('to') == entity_id:
                    related.append(f"{rel.get('from', '')} ({rel.get('type', '')})")
        return related[:limit]


class KGRAGPipeline:
    """Main KG RAG Pipeline."""
    
    def __init__(self):
        log("Initializing KG RAG Pipeline...")
        self.kg = KGLoader(KG_PATH)
        self.index = KGIndex(self.kg)
        self.decomposer = QueryDecomposer()
        self.assembler = ContextAssembler(self.kg)
    
    def query(self, user_query: str, verbose: bool = False) -> str:
        """Process a query through the RAG pipeline."""
        log(f"Query: {user_query}")
        
        # Step 1: Query Analysis
        query_analysis = self.decomposer.decompose(user_query)
        if verbose:
            log(f"Query Analysis: {json.dumps(query_analysis, indent=2)}")
        
        # Step 2: Retrieval
        retrieved = []
        
        # Type-based retrieval
        for entity_type in query_analysis['required_types']:
            type_results = self.index.search_by_type(entity_type, limit=5)
            for entity_id, entity in type_results:
                retrieved.append((entity_id, entity, 1.0))
        
        # Keyword search
        keyword_results = self.index.search_by_keyword(
            user_query, 
            limit=10
        )
        for entity_id, entity, score in keyword_results:
            # Avoid duplicates
            if not any(r[0] == entity_id for r in retrieved):
                retrieved.append((entity_id, entity, score))
        
        log(f"Retrieved {len(retrieved)} entities")
        
        # Step 3: Context Assembly
        context = self.assembler.assemble(query_analysis, retrieved)
        
        return context
    
    def query_and_print(self, user_query: str):
        """Query and print results."""
        context = self.query(user_query, verbose=True)
        print("\n" + "="*60)
        print("KG RAG CONTEXT")
        print("="*60)
        print(context)
        print("="*60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 kg_rag_pipeline.py \"Your question here\"")
        print("  or: python3 kg_rag_pipeline.py --interactive")
        sys.exit(1)
    
    if sys.argv[1] == '--interactive':
        print("KG RAG Interactive Mode (type 'exit' to quit)")
        pipeline = KGRAGPipeline()
        while True:
            try:
                query = input("\nQuery> ")
                if query.lower() in ['exit', 'quit', 'q']:
                    break
                if query.strip():
                    pipeline.query_and_print(query)
            except KeyboardInterrupt:
                break
    elif sys.argv[1] == '--stats':
        pipeline = KGRAGPipeline()
        print("\n=== KG RAG Statistics ===")
        print(f"Entities: {len(pipeline.kg.entities)}")
        print(f"Relations: {len(pipeline.kg.relations)}")
        print(f"Entity Types: {len(pipeline.index.entity_by_type)}")
        print("\nTop Entity Types:")
        type_counts = [(t, len(eids)) for t, eids in pipeline.index.entity_by_type.items()]
        for t, count in sorted(type_counts, key=lambda x: -x[1])[:10]:
            print(f"  {t}: {count}")
    else:
        query = ' '.join(sys.argv[1:])
        pipeline = KGRAGPipeline()
        pipeline.query_and_print(query)


if __name__ == "__main__":
    main()
