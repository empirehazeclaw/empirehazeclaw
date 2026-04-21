#!/usr/bin/env python3
"""
KG Reorganizer v2
================
Reorganizes Knowledge Graph with correct dict-based structure.

KG Structure:
- entities: dict {entity_id: {type, category, facts, priority, created, last_accessed, ...}}
- relationships: list [{from, to, type, weight, created_at}]

Usage:
    python3 kg_reorganizer.py --score        # Calculate quality scores
    python3 kg_reorganizer.py --orphans      # Find orphan entities
    python3 kg_reorganizer.py --cleanup      # Remove stale/orphan entities
    python3 kg_reorganizer.py --full         # Run all
"""

import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
KG_FILE = WORKSPACE / 'memory/kg/knowledge_graph.json'
BACKUP_FILE = WORKSPACE / 'memory/kg/knowledge_graph.json.bak'
REPORT_FILE = WORKSPACE / 'memory/kg/reorg_report.json'


class KGReorganizer:
    def __init__(self):
        self.kg = self.load_kg()
        # entities is a dict {entity_id: entity_data}
        self.entities = self.kg.get('entities', {})
        # relationships is a list
        self.relationships = self.kg.get('relationships', [])
    
    def load_kg(self):
        with open(KG_FILE, 'r') as f:
            return json.load(f)
    
    def save_kg(self):
        with open(KG_FILE, 'w') as f:
            json.dump(self.kg, f, indent=2)
    
    def create_backup(self):
        if not BACKUP_FILE.exists():
            shutil.copy(KG_FILE, BACKUP_FILE)
            print("✅ Backup created at memory/kg/knowledge_graph.json.bak")
    
    def calculate_quality_scores(self):
        """Calculate quality score for each entity."""
        print("📊 Calculating KG Quality Scores...")
        
        # Build relation count map
        relation_count = defaultdict(int)
        for rel in self.relationships:
            entity_id = rel.get('from') or rel.get('source')
            target_id = rel.get('to') or rel.get('target')
            if entity_id:
                relation_count[entity_id] += 1
            if target_id:
                relation_count[target_id] += 1
        
        scores = []
        
        for entity_id, entity_data in self.entities.items():
            # Completeness score (0-1)
            has_type = bool(entity_data.get('type'))
            has_category = bool(entity_data.get('category'))
            facts = entity_data.get('facts', [])
            has_facts = len(facts) > 0
            has_label = bool(entity_id)  # entity_id itself is the label
            
            completeness = (has_label + has_type + has_category + has_facts) / 4
            
            # Relation score (0-1)
            rel_count = relation_count.get(entity_id, 0)
            relation_score = min(rel_count / 5, 1.0)  # Cap at 5 relations
            
            # Recency score (0-1) — using last_accessed or created
            last_accessed = entity_data.get('last_accessed', entity_data.get('created', ''))
            if last_accessed:
                try:
                    days_old = (datetime.now() - datetime.fromisoformat(last_accessed)).days
                    recency_score = max(0, 1 - (days_old / 90))  # 90 days = 0
                except:
                    recency_score = 0.5
            else:
                recency_score = 0.5
            
            # Weighted total
            total = completeness * 0.4 + relation_score * 0.3 + recency_score * 0.3
            
            scores.append({
                'id': entity_id,
                'type': entity_data.get('type'),
                'completeness': round(completeness, 2),
                'relation_count': rel_count,
                'recency_score': round(recency_score, 2),
                'quality_score': round(total, 2)
            })
        
        # Sort by quality score
        scores.sort(key=lambda x: x['quality_score'])
        
        print(f"   Total entities: {len(scores)}")
        print(f"   High quality (>0.6): {len([s for s in scores if s['quality_score'] > 0.6])}")
        print(f"   Medium (0.3-0.6): {len([s for s in scores if 0.3 <= s['quality_score'] <= 0.6])}")
        print(f"   Low (<0.3): {len([s for s in scores if s['quality_score'] < 0.3])}")
        
        return scores
    
    def find_orphans(self):
        """Find orphan entities (0 relations)."""
        print("\n🔍 Finding orphan entities...")
        
        # Build connected set from relationships
        connected = set()
        for rel in self.relationships:
            entity_id = rel.get('from') or rel.get('source')
            target_id = rel.get('to') or rel.get('target')
            if entity_id:
                connected.add(entity_id)
            if target_id:
                connected.add(target_id)
        
        # Find entities not in connected set
        orphan_ids = [eid for eid in self.entities.keys() if eid not in connected]
        
        print(f"   Total entities: {len(self.entities)}")
        print(f"   Connected: {len(connected)}")
        print(f"   Orphans: {len(orphan_ids)} ({(len(orphan_ids)/len(self.entities))*100:.1f}%)")
        
        if orphan_ids:
            print("\n   Top 10 orphans:")
            for oid in orphan_ids[:10]:
                entity = self.entities[oid]
                print(f"     - {oid} (type: {entity.get('type', 'unknown')})")
        
        return orphan_ids
    
    def find_stale_entities(self, days=30):
        """Find entities not accessed in >days."""
        print(f"\n🔍 Finding stale entities (>{days} days old)...")
        
        stale = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for entity_id, entity_data in self.entities.items():
            last_accessed = entity_data.get('last_accessed', entity_data.get('created', ''))
            if last_accessed:
                try:
                    if datetime.fromisoformat(last_accessed) < cutoff:
                        stale.append({
                            'id': entity_id,
                            'type': entity_data.get('type'),
                            'last_accessed': last_accessed,
                            'access_count': entity_data.get('access_count', 0)
                        })
                except:
                    pass
        
        print(f"   Stale entities: {len(stale)}")
        
        return stale
    
    def analyze_orphan_categories(self, orphan_ids):
        """Analyze what types of entities are orphaned."""
        print("\n📋 Orphan Category Analysis...")
        
        categories = defaultdict(list)
        
        for oid in orphan_ids:
            entity = self.entities[oid]
            entity_type = entity.get('type', 'unknown')
            entity_category = entity.get('category', 'unknown')
            
            # Group by prefix pattern (for generated entities)
            if oid.startswith('success_'):
                categories['success_patterns'].append(oid)
            elif oid.startswith('error_'):
                categories['error_patterns'].append(oid)
            elif oid.startswith('Improvement_'):
                categories['improvement_tracking'].append(oid)
            elif oid.startswith('category_'):
                categories['category_entries'].append(oid)
            else:
                categories['other'].append(oid)
        
        for cat, ids in sorted(categories.items(), key=lambda x: -len(x[1])):
            print(f"   {cat}: {len(ids)} entities")
        
        return categories
    
    def run_full_reorg(self):
        """Run full reorganisation."""
        print("🧹 KG Reorganizer v2 — Full Run")
        print("=" * 50)
        
        self.create_backup()
        
        # Calculate quality scores
        scores = self.calculate_quality_scores()
        
        # Find orphans
        orphan_ids = self.find_orphans()
        
        # Analyze orphan categories
        categories = self.analyze_orphan_categories(orphan_ids)
        
        # Find stale
        stale = self.find_stale_entities(30)
        
        # Build report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_entities': len(self.entities),
            'total_relations': len(self.relationships),
            'quality_distribution': {
                'high': len([s for s in scores if s['quality_score'] > 0.6]),
                'medium': len([s for s in scores if 0.3 <= s['quality_score'] <= 0.6]),
                'low': len([s for s in scores if s['quality_score'] < 0.3])
            },
            'orphans': {
                'count': len(orphan_ids),
                'percentage': round((len(orphan_ids) / len(self.entities)) * 100, 1),
                'by_category': {k: len(v) for k, v in categories.items()}
            },
            'stale_30_days': len(stale),
            'recommendations': []
        }
        
        # Generate recommendations
        orphan_pct = (len(orphan_ids) / len(self.entities)) * 100
        
        if orphan_pct > 50:
            report['recommendations'].append({
                'action': 'review_learning_loop_artifacts',
                'priority': 'HIGH',
                'reason': f'{orphan_pct:.1f}% orphan rate — mostly learning loop generated entities',
                'count': len(orphan_ids)
            })
        
        if stale:
            report['recommendations'].append({
                'action': 'review_stale_entities',
                'priority': 'MED',
                'reason': 'Entities not accessed in 30+ days',
                'count': len(stale)
            })
        
        # Success/error patterns analysis
        se_count = len(categories.get('success_patterns', [])) + len(categories.get('error_patterns', []))
        if se_count > 20:
            report['recommendations'].append({
                'action': 'cleanup_success_error_patterns',
                'priority': 'LOW',
                'reason': 'Temporary pattern tracking entries can be cleaned up',
                'count': se_count
            })
        
        with open(REPORT_FILE, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📋 Report saved to {REPORT_FILE}")
        print(f"\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  [{rec['priority']}] {rec['action']}: {rec['count']} entities")
        
        return report


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='KG Reorganizer v2')
    parser.add_argument('--score', action='store_true', help='Calculate quality scores')
    parser.add_argument('--orphans', action='store_true', help='Find orphans')
    parser.add_argument('--cleanup', action='store_true', help='Cleanup stale/orphans')
    parser.add_argument('--full', action='store_true', help='Full reorg')
    
    args = parser.parse_args()
    
    reorganizer = KGReorganizer()
    
    if args.score:
        reorganizer.calculate_quality_scores()
    elif args.orphans:
        reorganizer.find_orphans()
    elif args.full:
        reorganizer.run_full_reorg()
    else:
        parser.print_help()