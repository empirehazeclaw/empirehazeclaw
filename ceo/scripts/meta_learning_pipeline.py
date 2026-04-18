#!/usr/bin/env python3
"""
meta_learning_pipeline.py — Hourly Meta-Learning Pipeline
==========================================================
Runs: Pattern Mining → Integration → KG Sync

Usage:
    python3 meta_learning_pipeline.py          # Full pipeline
    python3 meta_learning_pipeline.py --step <step>  # Specific step
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')

# Import our modules
sys.path.insert(0, str(WORKSPACE / 'scripts'))
from meta_task_analyzer import run_analysis
from cross_task_pattern_miner import run_mining
from enhanced_pattern_miner import run_enhanced_mining
from meta_learning_integrator import MetaLearningIntegrator


def run_pipeline():
    """Run the full meta-learning pipeline."""
    print("🔄 Meta Learning Pipeline — Hourly")
    print("=" * 50)
    print(f"Started: {datetime.now().isoformat()}")
    
    # Step 1: Task Analysis
    print("\n📊 Step 1: Task Analysis")
    try:
        factors, insights = run_analysis(summary_only=True)
        print(f"   Analyzed {factors.get('total_tasks', 0)} tasks")
    except Exception as e:
        print(f"   ⚠️ Task analysis error: {e}")
    
    # Step 2: Pattern Mining (Enhanced)
    print("\n🔍 Step 2: Pattern Mining (Enhanced)")
    try:
        # Run both basic and enhanced mining
        basic_patterns = run_mining()
        enhanced_patterns = run_enhanced_mining()
        total_patterns = len(enhanced_patterns)
        print(f"   Found {total_patterns} patterns (basic + enhanced)")
    except Exception as e:
        print(f"   ⚠️ Pattern mining error: {e}")
        total_patterns = 0
    
    # Step 3: Integration
    print("\n🔄 Step 3: Integration")
    try:
        integrator = MetaLearningIntegrator()
        integrator.load_patterns()
        result = integrator.sync()
        print(f"   Integrated {len(result.get('patterns', []))} patterns")
    except Exception as e:
        print(f"   ⚠️ Integration error: {e}")
    
    # Step 4: Embedding Engine (Phase 2)
    print("\n🧮 Step 4: Task Embeddings")
    try:
        from task_embedding_engine import TaskEmbeddingEngine
        engine = TaskEmbeddingEngine()
        engine.load_embeddings()
        # Only embed new tasks
        if len(engine.embeddings) < 170:
            count = engine.embed_all_tasks()
            print(f"   Embeddings: {count}")
        else:
            print(f"   Embeddings: {len(engine.embeddings)} (up to date)")
    except Exception as e:
        print(f"   ⚠️ Embedding error: {e}")
    
    # Step 5: Similarity Index (Phase 2)
    print("\n🔗 Step 5: Similarity Index")
    try:
        from task_similarity_index import TaskSimilarityIndex
        index = TaskSimilarityIndex()
        if not index.index:
            index.build_index()
            print(f"   Indexed: {len(index.index)} tasks")
        else:
            print(f"   Index: {len(index.index)} tasks (up to date)")
    except Exception as e:
        print(f"   ⚠️ Index error: {e}")
    
    # Step 6: Meta-Learning Controller (Phase 3)
    print("\n🧠 Step 6: Meta-Learning Controller")
    try:
        from meta_learning_controller import MetaLearningController
        controller = MetaLearningController()
        result = controller.run_cycle()
        print(f"   Test accuracy: {result.get('test_accuracy', 0):.1%}")
        print(f"   Adjustments: {result.get('adjustments_made', 0)}")
    except Exception as e:
        print(f"   ⚠️ Controller error: {e}")
    
    # Step 7: Algorithm Optimizer (Phase 3)
    print("\n⚙️ Step 7: Learning Algorithm Optimizer")
    try:
        from learning_algorithm_optimizer import LearningAlgorithmOptimizer
        optimizer = LearningAlgorithmOptimizer()
        from cross_task_pattern_miner import run_mining as get_patterns
        patterns = get_patterns()
        optimizer.optimize_from_patterns(patterns)
        print(f"   Optimized {len(optimizer.weights)} weight parameters")
    except Exception as e:
        print(f"   ⚠️ Optimizer error: {e}")
    
    # Step 8: Feedback Bridge (Phase 3)
    print("\n🔄 Step 8: Meta Feedback Bridge")
    try:
        from meta_feedback_bridge import MetaFeedbackBridge
        bridge = MetaFeedbackBridge()
        result = bridge.run_feedback_cycle()
        print(f"   Patterns adjusted: {len(result.get('adjustments', []))}")
    except Exception as e:
        print(f"   ⚠️ Feedback bridge error: {e}")
    
    # Step 9: KG Meta-Learner (Phase 4)
    print("\n🧠 Step 9: KG Meta-Learner")
    try:
        from kg_meta_learner import KGMetaLearner
        learner = KGMetaLearner()
        result = learner.run_meta_learning()
        print(f"   KG entities: {len(learner.kg_entities)}")
        print(f"   Meta-relations: {result.get('meta_relations', 0)}")
    except Exception as e:
        print(f"   ⚠️ KG Meta-Learner error: {e}")
    
    # Step 10: KG Embedding Updater (Phase 4)
    print("\n🔄 Step 10: KG Embedding Updater")
    try:
        from kg_embedding_updater import KGEmbeddingUpdater
        updater = KGEmbeddingUpdater()
        result = updater.run_update()
        print(f"   Entity updates: {result.get('entity_updates', 0)}")
        print(f"   Relation additions: {result.get('relation_updates', 0)}")
    except Exception as e:
        print(f"   ⚠️ KG Updater error: {e}")
    
    # Step 11: Meta-KG Query Interface (Phase 4)
    print("\n🎯 Step 11: Meta-KG Query Interface")
    try:
        from meta_kg_query_interface import MetaKGQueryInterface
        interface = MetaKGQueryInterface()
        interface.status()
    except Exception as e:
        print(f"   ⚠️ Query Interface error: {e}")
    
    print(f"\n✅ Pipeline complete: {datetime.now().isoformat()}")


def run_step(step):
    """Run a specific pipeline step."""
    if step == 'analyze':
        run_analysis()
    elif step == 'mine':
        run_mining()
    elif step == 'integrate':
        integrator = MetaLearningIntegrator()
        integrator.sync()
    else:
        print(f"Unknown step: {step}")


if __name__ == '__main__':
    step = None
    if '--step' in sys.argv:
        idx = sys.argv.index('--step')
        if idx + 1 < len(sys.argv):
            step = sys.argv[idx + 1]
    
    if step:
        run_step(step)
    else:
        run_pipeline()