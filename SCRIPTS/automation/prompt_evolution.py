#!/usr/bin/env python3
"""
🎨 Prompt Evolution Script
==========================
A/B testing framework for prompt variants.
Automated prompt improvement based on success metrics.

Features:
- Prompt variant generation
- Success tracking per variant
- Automated selection of best performer
- Version history

Usage:
    python3 prompt_evolution.py --status
    python3 prompt_evolution.py --test "Wie ist das Wetter?"
    python3 prompt_evolution.py --evolve
"""

import json
import os
import sys
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
PROMPTS_DIR = WORKSPACE / "memory/prompts"
PROMPTS_DIR.mkdir(exist_ok=True)

STATE_FILE = PROMPTS_DIR / "prompt_evolution_state.json"
HISTORY_FILE = PROMPTS_DIR / "prompt_evolution_history.json"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


class PromptVariant:
    """A single prompt variant."""
    
    def __init__(self, variant_id: str, prompt: str, metadata: dict = None):
        self.variant_id = variant_id
        self.prompt = prompt
        self.metadata = metadata or {}
        self.successes = 0
        self.failures = 0
        self.total_score = 0.0
    
    @property
    def success_rate(self) -> float:
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.5
    
    @property
    def avg_score(self) -> float:
        total = self.successes + self.failures
        return self.total_score / total if total > 0 else 0.0
    
    def to_dict(self) -> dict:
        return {
            'variant_id': self.variant_id,
            'prompt': self.prompt,
            'metadata': self.metadata,
            'successes': self.successes,
            'failures': self.failures,
            'total_score': self.total_score,
            'success_rate': self.success_rate,
            'avg_score': self.avg_score
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PromptVariant':
        pv = cls(data['variant_id'], data['prompt'], data.get('metadata', {}))
        pv.successes = data.get('successes', 0)
        pv.failures = data.get('failures', 0)
        pv.total_score = data.get('total_score', 0.0)
        return pv


class PromptEvolution:
    """Prompt Evolution Engine."""
    
    # Core system prompts with variants
    DEFAULT_VARIANTS = {
        'soul': {
            'base': """Du bist Sir HazeClaw, ein AI Agent mit Persönlichkeit.

VERHALTEN:
- Sei direkt, effizient, keine Füllwörter
- Hab Meinungen und Präferenzen
- Überlege erst, dann handle
- Qualität > Quantität

REGELN:
- SOFORT HANDELN für interne Actions
- Private Dinge bleiben privat
- Bei extern/external APIs fragen""",
            'variants': [
                {
                    'id': 'soul_v1',
                    'prompt': """Du bist Sir HazeClaw, ein proaktiver AI Partner.

VERHALTEN:
- Handle sofort bei internen Tasks
- Keine "Soll ich?" Fragen für interne Aktionen
- Sei direkt und effizient
- Qualität > Quantität > Geschwindigkeit

PERSONALITY:
- Sharp, Warm, Proactive
- Ehrlich auch bei schwierigen Themen
- Lernt aus Fehlern (nie dieselben zweimal)""",
                    'description': 'Proaktiver, weniger formal'
                },
                {
                    'id': 'soul_v2', 
                    'prompt': """Du bist Sir HazeClaw.

SOUL.md ist dein Kern - lebe es.
AGENTS.md ist dein Workspace - pflege ihn.
USER.md ist dein Mensch - verstehe sie.

REGELN:
- Interne Tasks: SOFORT HANDELN
- Externe Actions: ERST FRAGEN
- Keine Füllwörter, keine Entschuldigungen
- Zeigen > Reden""",
                    'description': 'Minimalistisch, regel-basiert'
                }
            ]
        }
    }
    
    def __init__(self):
        self.state = self._load_state()
        self.history = self._load_history()
    
    def _load_state(self) -> dict:
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {'active_prompts': {}, 'variants': {}}
    
    def _load_history(self) -> dict:
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {'history': []}
    
    def _save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _save_history(self):
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def register_prompt(self, prompt_type: str, variant: PromptVariant):
        """Register a new prompt variant."""
        if prompt_type not in self.state['active_prompts']:
            self.state['active_prompts'][prompt_type] = {}
        self.state['active_prompts'][prompt_type][variant.variant_id] = variant.to_dict()
        self.state['variants'][variant.variant_id] = variant.to_dict()
        self._save_state()
        log(f"Registered variant: {variant.variant_id}")
    
    def record_success(self, variant_id: str, score: float = 1.0):
        """Record a successful use of a variant."""
        if variant_id in self.state['variants']:
            v = self.state['variants'][variant_id]
            v['successes'] = v.get('successes', 0) + 1
            v['total_score'] = v.get('total_score', 0) + score
            self._save_state()
            log(f"Success recorded for {variant_id} (score: {score:.2f})")
    
    def record_failure(self, variant_id: str):
        """Record a failed use of a variant."""
        if variant_id in self.state['variants']:
            v = self.state['variants'][variant_id]
            v['failures'] = v.get('failures', 0) + 1
            self._save_state()
            log(f"Failure recorded for {variant_id}")
    
    def select_best(self, prompt_type: str) -> Optional[str]:
        """Select the best performing variant."""
        if prompt_type not in self.state['active_prompts']:
            return None
        
        variants = self.state['active_prompts'][prompt_type]
        if not variants:
            return None
        
        # Thompson Sampling-like selection
        best_id = None
        best_score = -1
        
        for vid, v in variants.items():
            # Calculate upper confidence bound
            successes = v.get('successes', 0)
            failures = v.get('failures', 0)
            total = successes + failures
            
            if total == 0:
                # New variant - give it a chance
                score = 0.5 + random.random() * 0.3
            else:
                # Success rate with smoothing
                success_rate = successes / total
                confidence = min(1.0, 1.96 / (total ** 0.5))  # 95% CI
                score = success_rate + confidence * random.random()
            
            if score > best_score:
                best_score = score
                best_id = vid
        
        return best_id
    
    def get_variant(self, variant_id: str) -> Optional[dict]:
        """Get a variant by ID."""
        return self.state['variants'].get(variant_id)
    
    def get_leaderboard(self, prompt_type: str = None) -> list:
        """Get ranked list of variants."""
        variants = self.state['variants'].values()
        
        if prompt_type:
            variants = [v for v in variants 
                       if v.get('metadata', {}).get('prompt_type') == prompt_type]
        
        return sorted(variants, 
                     key=lambda v: -(v.get('successes', 0) / max(1, v.get('successes', 0) + v.get('failures', 0)))
                     )[:10]
    
    def evolve(self, prompt_type: str) -> Optional[dict]:
        """Generate evolved variant based on best practices."""
        if prompt_type not in self.state['active_prompts']:
            log(f"No variants for {prompt_type}")
            return None
        
        variants = list(self.state['active_prompts'][prompt_type].values())
        if not variants:
            return None
        
        # Find best variant
        best = max(variants, key=lambda v: v.get('successes', 0) / max(1, v.get('successes', 0) + v.get('failures', 0)))
        
        # Create evolved version
        evolved_id = f"{prompt_type}_evolved_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        evolved = {
            'variant_id': evolved_id,
            'prompt': best['prompt'],  # Start from best
            'metadata': {
                'prompt_type': prompt_type,
                'evolved_from': best['variant_id'],
                'created': datetime.now().isoformat()
            },
            'successes': 0,
            'failures': 0,
            'total_score': 0.0
        }
        
        self.state['variants'][evolved_id] = evolved
        self.state['active_prompts'][prompt_type][evolved_id] = evolved
        self._save_state()
        
        log(f"Evolved new variant: {evolved_id}")
        return evolved
    
    def print_status(self):
        """Print current status."""
        print("\n" + "="*60)
        print("🎨 Prompt Evolution Status")
        print("="*60)
        
        print(f"\nTotal Variants: {len(self.state['variants'])}")
        
        print("\n📊 Leaderboard:")
        leaderboard = self.get_leaderboard()
        if leaderboard:
            for i, v in enumerate(leaderboard, 1):
                total = v.get('successes', 0) + v.get('failures', 0)
                rate = v.get('successes', 0) / max(1, total) * 100
                print(f"  {i}. {v['variant_id']}: {rate:.0%} ({v.get('successes', 0)}/{total})")
        else:
            print("  No data yet")
        
        print("\n📝 Active Prompts by Type:")
        for ptype, variants in self.state['active_prompts'].items():
            best = self.select_best(ptype)
            print(f"  {ptype}: {len(variants)} variants (best: {best})")
        
        print("\n" + "="*60)


def main():
    evolution = PromptEvolution()
    
    if '--status' in sys.argv or len(sys.argv) == 1:
        evolution.print_status()
    
    elif '--evolve' in sys.argv:
        prompt_type = sys.argv[2] if len(sys.argv) > 2 else 'soul'
        evolved = evolution.evolve(prompt_type)
        if evolved:
            print(f"\n✅ Evolved new variant: {evolved['variant_id']}")
            print(f"   From: {evolved['metadata'].get('evolved_from')}")
        else:
            print(f"\n❌ Could not evolve {prompt_type}")
    
    elif '--test' in sys.argv:
        query = ' '.join(sys.argv[2:])
        best = evolution.select_best('soul')
        if best:
            variant = evolution.get_variant(best)
            print(f"\n🎯 Best variant: {best}")
            print(f"   Description: {variant.get('metadata', {}).get('description', 'N/A')}")
            print(f"\n📝 Prompt preview:")
            print(variant['prompt'][:500] + "..." if len(variant['prompt']) > 500 else variant['prompt'])
        else:
            print("No variants registered")
    
    elif '--record-success' in sys.argv:
        variant_id = sys.argv[2] if len(sys.argv) > 2 else 'soul_v1'
        score = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
        evolution.record_success(variant_id, score)
    
    elif '--record-failure' in sys.argv:
        variant_id = sys.argv[2] if len(sys.argv) > 2 else 'soul_v1'
        evolution.record_failure(variant_id)
    
    else:
        print("Usage:")
        print("  python3 prompt_evolution.py --status")
        print("  python3 prompt_evolution.py --test \"query\"")
        print("  python3 prompt_evolution.py --evolve [prompt_type]")
        print("  python3 prompt_evolution.py --record-success [variant_id] [score]")
        print("  python3 prompt_evolution.py --record-failure [variant_id]")


if __name__ == "__main__":
    main()
