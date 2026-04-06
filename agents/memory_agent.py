#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          OPENCLAW · MEMORY & LEARNING AGENT                  ║
║          Persistent Knowledge · Vector Store · Feedback       ║
╚══════════════════════════════════════════════════════════════╝

5 Memory Types:
  - EPISODIC: Task-Historie + Ergebnisse
  - SEMANTIC: Fakten, Wissen, Dokumente
  - PROCEDURAL: Gelernte Muster & Best Practices
  - FEEDBACK: Qualitätsbewertungen
  - ERROR: Fehler-Patterns

Hinweis: LLM-Routing wird NICHT verwendet - wir nutzen das Standard-Modell
"""

from __future__ import annotations

import json
import time
import hashlib
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, List, Dict
from uuid import uuid4
import os

# ChromaDB for vector storage
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️ ChromaDB nicht installiert - nutze File-basiertes Fallback")

# Local embeddings (free)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

import sys
sys.path.insert(0, '/home/clawbot/.openclaw/workspace/scripts')

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [MEMORY] %(message)s")
log = logging.getLogger("openclaw.memory")

# Konfiguration
PERSIST_DIR = Path("/home/clawbot/.openclaw/workspace/memory/chroma")
MODEL_NAME = "all-MiniLM-L6-v2"  # Lokal, schnell, kostenlos
TOP_K_DEFAULT = 5
RELEVANCE_THRESHOLD = 0.72


class MemoryType(str, Enum):
    """5 Gedächtnis-Typen"""
    EPISODIC = "episodic"     # Task-Ausführungen & Ergebnisse
    SEMANTIC = "semantic"     # Fakten, Dokumente, Wissen
    PROCEDURAL = "procedural" # Gelernte Strategien & Patterns
    FEEDBACK = "feedback"     # Qualitätsbewertungen
    ERROR = "error"           # Fehler-Patterns


class MemoryAgent:
    """Multi-Typ Memory Agent mit Vector Search"""
    
    def __init__(self):
        self.collections = {}
        self.embeddings_model = None
        self._init_vector_store()
        
    def _init_vector_store(self):
        """Initialisiere ChromaDB oder Fallback"""
        if CHROMADB_AVAILABLE:
            try:
                # Create persist directory
                PERSIST_DIR.mkdir(parents=True, exist_ok=True)
                
                self.chroma_client = chromadb.PersistentClient(
                    path=str(PERSIST_DIR),
                    settings=Settings(anonymized_telemetry=False)
                )
                
                # Create collections for each memory type
                for mem_type in MemoryType:
                    collection_name = f"openclaw_{mem_type.value}"
                    try:
                        collection = self.chroma_client.get_or_create_collection(
                            name=collection_name,
                            metadata={"description": f"OpenClaw {mem_type.value} memory"}
                        )
                        self.collections[mem_type] = collection
                        log.info(f"✅ Collection erstellt: {collection_name}")
                    except Exception as e:
                        log.error(f"❌ Fehler bei Collection {collection_name}: {e}")
                
                # Load embeddings model
                if SENTENCE_TRANSFORMERS_AVAILABLE:
                    self.embeddings_model = SentenceTransformer(MODEL_NAME)
                    log.info(f"✅ Embeddings Model geladen: {MODEL_NAME}")
                else:
                    log.warning("⚠️ sentence-transformers nicht verfügbar")
                    
            except Exception as e:
                log.error(f"❌ ChromaDB Initialisierung fehlgeschlagen: {e}")
                self.chroma_client = None
        else:
            self.chroma_client = None
            log.warning("⚠️ ChromaDB nicht verfügbar - File-Fallback aktiv")
    
    def store(
        self,
        memory_type: MemoryType,
        content: str,
        metadata: Optional[Dict] = None,
        task_id: Optional[str] = None
    ) -> str:
        """
        Speichere etwas im Memory
        
        Args:
            memory_type: Welcher Typ (episodic, semantic, etc.)
            content: Der eigentliche Inhalt
            metadata: Zusätzliche Daten (agent, task, score, etc.)
            task_id: Optional ID für Verknüpfung
            
        Returns:
            memory_id: Die ID des gespeicherten Eintrags
        """
        memory_id = task_id or str(uuid4())
        metadata = metadata or {}
        metadata["created_at"] = datetime.now().isoformat()
        metadata["memory_type"] = memory_type.value
        
        # Store in ChromaDB
        if self.chroma_client and memory_type in self.collections:
            try:
                collection = self.collections[memory_type]
                
                # Generate embedding if available
                if self.embeddings_model:
                    embedding = self.embeddings_model.encode(content).tolist()
                else:
                    # Fallback: use hash as pseudo-embedding
                    embedding = self._simple_embedding(content)
                
                collection.add(
                    ids=[memory_id],
                    documents=[content],
                    embeddings=[embedding],
                    metadatas=[metadata]
                )
                
                log.info(f"💾 Gespeichert: {memory_type.value} | {memory_id[:8]}...")
                return memory_id
                
            except Exception as e:
                log.error(f"❌ Speicher-Fehler: {e}")
        
        # Fallback: File-based storage
        return self._store_fallback(memory_type, content, metadata, memory_id)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """Einfacher Hash-basierter Embedding-Ersatz"""
        hash_val = hashlib.md5(text.encode()).hexdigest()
        # Convert hex to float list (pseudo-embedding)
        return [float(int(hash_val[i:i+2], 16)) / 255 for i in range(0, 32, 2)]
    
    def _store_fallback(self, memory_type, content, metadata, memory_id):
        """File-basiertes Fallback"""
        fallback_dir = PERSIST_DIR / "fallback" / memory_type.value
        fallback_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = fallback_dir / f"{memory_id}.json"
        data = {
            "id": memory_id,
            "content": content,
            "metadata": metadata
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        log.info(f"💾 (Fallback) Gespeichert: {memory_type.value} | {memory_id[:8]}")
        return memory_id
    
    def retrieve(
        self,
        memory_type: MemoryType,
        query: str,
        top_k: int = TOP_K_DEFAULT,
        min_score: float = RELEVANCE_THRESHOLD
    ) -> List[Dict]:
        """
        Relevante Einträge aus Memory abrufen
        
        Args:
            memory_type: Welcher Typ soll durchsucht werden
            query: Die Suchanfrage
            top_k: Wie viele Ergebnisse
            min_score: Minimale Relevanz
            
        Returns:
            Liste von Dict mit {id, content, metadata, score}
        """
        results = []
        
        if self.chroma_client and memory_type in self.collections:
            try:
                collection = self.collections[memory_type]
                
                # Generate query embedding
                if self.embeddings_model:
                    query_embedding = self.embeddings_model.encode(query).tolist()
                else:
                    query_embedding = self._simple_embedding(query)
                
                # Search
                search_results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                
                # Parse results
                if search_results.get("documents"):
                    for i, doc in enumerate(search_results["documents"][0]):
                        score = 1.0 - (search_results.get("distances", [[0]])[0][i] / 2)  # Convert distance to similarity
                        
                        if score >= min_score:
                            results.append({
                                "id": search_results["ids"][0][i],
                                "content": doc,
                                "metadata": search_results.get("metadatas", [{}])[0][i],
                                "score": score
                            })
                            
            except Exception as e:
                log.error(f"❌ Retrieval-Fehler: {e}")
        
        return results
    
    def retrieve_all_types(self, query: str, top_k: int = 3) -> Dict[MemoryType, List[Dict]]:
        """
        Durchsuche alle Memory-Typen
        
        Returns:
            Dict mit MemoryType -> Liste von Ergebnissen
        """
        all_results = {}
        
        for mem_type in MemoryType:
            results = self.retrieve(mem_type, query, top_k=top_k)
            if results:
                all_results[mem_type] = results
                
        return all_results
    
    def store_episodic(self, task: str, agent: str, result: str, duration: float, score: float = 1.0):
        """Spezialmethode: Task-Ausführung speichern"""
        return self.store(
            MemoryType.EPISODIC,
            f"Task: {task} | Agent: {agent} | Result: {result}",
            metadata={
                "task": task,
                "agent": agent,
                "result": result,
                "duration_s": duration,
                "score": score
            }
        )
    
    def store_error(self, error: str, context: str, agent: str = None):
        """Spezialmethode: Fehler speichern"""
        return self.store(
            MemoryType.ERROR,
            f"Error: {error} | Context: {context}",
            metadata={
                "error": error,
                "context": context,
                "agent": agent
            }
        )
    
    def store_feedback(self, task: str, score: float, feedback: str):
        """Spezialmethode: Feedback speichern"""
        return self.store(
            MemoryType.FEEDBACK,
            f"Task: {task} | Score: {score} | Feedback: {feedback}",
            metadata={
                "task": task,
                "score": score,
                "feedback": feedback
            }
        )
    
    def store_procedural(self, pattern: str, description: str, agents: List[str]):
        """Spezialmethode: Gelerntes Pattern speichern"""
        return self.store(
            MemoryType.PROCEDURAL,
            f"Pattern: {pattern} | {description}",
            metadata={
                "pattern": pattern,
                "description": description,
                "agents": agents
            }
        )
    
    def get_stats(self) -> Dict:
        """Zeige Memory-Statistiken"""
        stats = {
            "total_collections": len(self.collections),
            "chroma_available": CHROMADB_AVAILABLE,
            "embeddings_available": SENTENCE_TRANSFORMERS_AVAILABLE,
            "by_type": {}
        }
        
        if self.chroma_client:
            for mem_type, collection in self.collections.items():
                try:
                    count = collection.count()
                    stats["by_type"][mem_type.value] = count
                except:
                    stats["by_type"][mem_type.value] = 0
        
        return stats


def main():
    """CLI Interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory Agent CLI")
    parser.add_argument("--store", nargs=3, metavar=("TYPE", "CONTENT", "METADATA"),
                        help="Speichere etwas (episodic|semantic|procedural|feedback|error)")
    parser.add_argument("--retrieve", nargs=2, metavar=("TYPE", "QUERY"),
                        help="Suche in Memory")
    parser.add_argument("--all", metavar="QUERY", help="Suche in allen Typen")
    parser.add_argument("--stats", action="store_true", help="Zeige Statistiken")
    
    args = parser.parse_args()
    
    agent = MemoryAgent()
    
    if args.stats:
        stats = agent.get_stats()
        print("\n📊 MEMORY STATS:")
        print(json.dumps(stats, indent=2))
    
    elif args.store:
        mem_type = args.store[0]
        content = args.store[1]
        metadata = json.loads(args.store[2]) if args.store[2] != "null" else {}
        
        try:
            mem_type_enum = MemoryType(mem_type)
            agent.store(mem_type_enum, content, metadata)
            print(f"✅ Gespeichert: {mem_type}")
        except ValueError:
            print(f"❌ Unbekannter Typ: {mem_type}")
    
    elif args.retrieve:
        mem_type = args.retrieve[0]
        query = args.retrieve[1]
        
        try:
            mem_type_enum = MemoryType(mem_type)
            results = agent.retrieve(mem_type_enum, query)
            print(f"\n🔍 Ergebnisse für '{query}' in {mem_type}:")
            for r in results:
                print(f"  [{r['score']:.2f}] {r['content'][:100]}...")
        except ValueError:
            print(f"❌ Unbekannter Typ: {mem_type}")
    
    elif args.all:
        query = args.all
        results = agent.retrieve_all_types(query)
        
        print(f"\n🔍 Alle Ergebnisse für '{query}':")
        for mem_type, items in results.items():
            print(f"\n  📂 {mem_type.value}:")
            for r in items:
                print(f"    [{r['score']:.2f}] {r['content'][:80]}...")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
