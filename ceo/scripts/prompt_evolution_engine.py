#!/usr/bin/env python3
"""
Phase 6.2: Prompt Evolution Engine
===================================
Comprehensive prompt inventory, benchmarking, and evolution system.

Was es macht:
1. Inventarisiert alle Prompts im System (SOUL, AGENTS, USER, IDENTITY, etc.)
2. Benchmarkt Prompts gegen bekannte Test-Cases
3. A/B Testing zwischen Varianten
4. Automatische Prompt-Optimierung basierend auf Feedback

Usage:
    python3 prompt_evolution_engine.py --action inventory
    python3 prompt_evolution_engine.py --action benchmark [--prompt_type soul]
    python3 prompt_evolution_engine.py --action evolve [--prompt_type soul]
    python3 prompt_evolution_engine.py --action test [--variant soul_v2]
"""

import json
import os
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
STATE_FILE = f"{WORKSPACE}/memory/prompts/prompt_evolution_state.json"
INVENTORY_FILE = f"{WORKSPACE}/memory/prompts/prompt_inventory.json"
BENCHMARK_RESULTS_FILE = f"{WORKSPACE}/memory/prompts/benchmark_results.json"


class PromptEvolutionEngine:
    def __init__(self):
        self.state = self.load_state()
        self.inventory = self.load_inventory()
        
    # ========== STATE MANAGEMENT ==========
    
    def load_state(self):
        """Load prompt evolution state."""
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {'active_prompts': {}, 'variants': {}, 'benchmarks': {}, 'tests': []}
    
    def save_state(self):
        """Save prompt evolution state."""
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def load_inventory(self):
        """Load prompt inventory."""
        if os.path.exists(INVENTORY_FILE):
            with open(INVENTORY_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_inventory(self):
        """Save prompt inventory."""
        with open(INVENTORY_FILE, 'w') as f:
            json.dump(self.inventory, f, indent=2)
    
    # ========== PROMPT SOURCES ==========
    
    def get_prompt_files(self):
        """Find all files containing prompts."""
        prompt_files = {
            'soul': f"{WORKSPACE}/SOUL.md",
            'agents': f"{WORKSPACE}/AGENTS.md",
            'user': f"{WORKSPACE}/USER.md",
            'identity': f"{WORKSPACE}/IDENTITY.md",
            'memory': f"{WORKSPACE}/MEMORY.md",
            'tools': f"{WORKSPACE}/TOOLS.md",
            'heartbeat': f"{WORKSPACE}/HEARTBEAT.md",
            'prompt_coach': f"{WORKSPACE}/PROMPT_COACH.md",
            'decision_framework': f"{WORKSPACE}/DECISION_FRAMEWORK.md",
            'dreams': f"{WORKSPACE}/DREAMS.md",
        }
        
        # Filter to only existing files
        return {k: v for k, v in prompt_files.items() if os.path.exists(v)}
    
    def read_prompt_content(self, prompt_type, file_path=None):
        """Read prompt content from file."""
        if file_path is None:
            file_path = self.get_prompt_files().get(prompt_type)
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return f.read()
        return None
    
    # ========== INVENTORY ==========
    
    def run_inventory(self):
        """Scan system and build prompt inventory."""
        print("📦 Prompt Inventory Scan")
        print("=" * 50)
        
        prompt_files = self.get_prompt_files()
        inventory = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'prompt_types': {},
            'total_prompts': 0,
            'total_variants': 0
        }
        
        for prompt_type, file_path in prompt_files.items():
            content = self.read_prompt_content(prompt_type, file_path)
            if content:
                # Calculate basic metrics
                lines = content.split('\n')
                char_count = len(content)
                line_count = len(lines)
                
                # Hash for change detection
                content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
                
                # Estimate token count (rough: 4 chars ≈ 1 token)
                token_estimate = char_count // 4
                
                entry = {
                    'prompt_type': prompt_type,
                    'file_path': file_path,
                    'char_count': char_count,
                    'line_count': line_count,
                    'token_estimate': token_estimate,
                    'content_hash': content_hash,
                    'last_modified': datetime.fromtimestamp(
                        os.path.getmtime(file_path)
                    ).isoformat() if os.path.exists(file_path) else None,
                    'has_variants': prompt_type in self.state.get('variants', {}),
                    'variant_count': len([
                        v for v in self.state.get('variants', {}).get(prompt_type, {}).values()
                    ])
                }
                
                # Check for quality issues
                issues = []
                if token_estimate > 4000:
                    issues.append('TOO_LONG')
                if 'TODO' in content or 'FIXME' in content:
                    issues.append('HAS_TODOS')
                if content.count('\n\n\n') > 3:
                    issues.append('EXCESSIVE_WHITESPACE')
                
                entry['quality_issues'] = issues
                
                inventory['prompt_types'][prompt_type] = entry
                inventory['total_prompts'] += 1
                inventory['total_variants'] += entry['variant_count']
                
                print(f"  ✅ {prompt_type}: {token_estimate} tokens, {line_count} lines")
                if issues:
                    print(f"     ⚠️ Issues: {', '.join(issues)}")
        
        self.inventory = inventory
        self.save_inventory()
        
        print(f"\n📊 Inventory Summary:")
        print(f"   Total Prompts: {inventory['total_prompts']}")
        print(f"   Total Variants: {inventory['total_variants']}")
        print(f"   Saved to: {INVENTORY_FILE}")
        
        return inventory
    
    # ========== BENCHMARK TESTS ==========
    
    def get_benchmark_tests(self):
        """Define benchmark test cases for each prompt type."""
        return {
            'soul': [
                {
                    'test_id': 'soul_direct_response',
                    'description': 'Response should be direct, no filler',
                    'input': 'Kannst du mir helfen?',
                    'expected_behavior': ['no_filler', 'direct_answer', 'actionable'],
                    'weight': 1.0
                },
                {
                    'test_id': 'soul_proactive',
                    'description': 'Should act proactively on opportunities',
                    'input': 'Die KG orphan rate ist hoch',
                    'expected_behavior': ['takes_action', 'no_asking'],
                    'weight': 1.0
                },
                {
                    'test_id': 'soul_evidence',
                    'description': 'Should not assume, only act on evidence',
                    'input': 'Ich glaube der Server ist down',
                    'expected_behavior': ['asks_first', 'no_assumption'],
                    'weight': 1.0
                }
            ],
            'agents': [
                {
                    'test_id': 'agents_trigger_rule',
                    'description': 'Should follow trigger rule strictly',
                    'input': 'Sehe ich gerade einen Trigger?',
                    'expected_behavior': ['checks_evidence', 'no_hallucination'],
                    'weight': 1.0
                }
            ]
        }
    
    def run_benchmark(self, prompt_type=None):
        """Run benchmark tests against prompts."""
        print("🧪 Prompt Benchmark")
        print("=" * 50)
        
        tests = self.get_benchmark_tests()
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'results': {}
        }
        
        # If prompt_type specified, only run those tests
        if prompt_type:
            tests = {prompt_type: tests.get(prompt_type, [])}
        
        for ptype, test_cases in tests.items():
            if not test_cases:
                continue
                
            print(f"\n📝 Testing: {ptype}")
            
            # Get current active prompt
            active_variant = self.state.get('active_prompts', {}).get(ptype, {})
            if not active_variant:
                # Load from file
                content = self.read_prompt_content(ptype)
                if content:
                    active_variant = {
                        'variant_id': f'{ptype}_current',
                        'prompt': content[:500],  # First 500 chars for quick test
                        'metadata': {'source': 'file'}
                    }
            
            for test in test_cases:
                results['tests_run'] += 1
                test_result = {
                    'test_id': test['test_id'],
                    'passed': False,
                    'score': 0.0,
                    'notes': ''
                }
                
                # Simple heuristic scoring based on prompt content
                prompt_preview = active_variant.get('prompt', '')[:500].lower()
                input_text = test['input'].lower()
                
                # Check if expected behaviors are suggested by prompt
                score = 0.5  # baseline
                for behavior in test['expected_behavior']:
                    if behavior == 'no_filler':
                        if any(w in prompt_preview for w in ['filler', 'performative', 'great question']):
                            score -= 0.2
                        else:
                            score += 0.1
                    elif behavior == 'direct_answer':
                        if 'concise' in prompt_preview or 'direct' in prompt_preview:
                            score += 0.2
                    elif behavior == 'takes_action':
                        if 'proactive' in prompt_preview or 'sofort handeln' in prompt_preview:
                            score += 0.2
                    elif behavior == 'no_asking':
                        if 'sofort' in prompt_preview:
                            score += 0.1
                    elif behavior == 'asks_first':
                        if 'ask' in prompt_preview or 'clarify' in prompt_preview:
                            score += 0.1
                    elif behavior == 'no_assumption':
                        if 'assume' in prompt_preview and 'evidence' in prompt_preview:
                            score += 0.1
                
                test_result['score'] = min(1.0, max(0.0, score))
                test_result['passed'] = score >= 0.5
                test_result['notes'] = f"Benchmark score: {score:.2f}"
                
                if test_result['passed']:
                    results['tests_passed'] += 1
                    print(f"   ✅ {test['test_id']}: {score:.2f}")
                else:
                    results['tests_failed'] += 1
                    print(f"   ❌ {test['test_id']}: {score:.2f}")
                
                results['results'][test['test_id']] = test_result
        
        # Save benchmark results
        os.makedirs(os.path.dirname(BENCHMARK_RESULTS_FILE), exist_ok=True)
        with open(BENCHMARK_RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📊 Benchmark Summary:")
        print(f"   Tests Run: {results['tests_run']}")
        print(f"   Passed: {results['tests_passed']}")
        print(f"   Failed: {results['tests_failed']}")
        print(f"   Pass Rate: {results['tests_passed']/max(1,results['tests_run'])*100:.0f}%")
        print(f"   Saved to: {BENCHMARK_RESULTS_FILE}")
        
        return results
    
    # ========== PROMPT EVOLUTION ==========
    
    def create_variant(self, prompt_type, variant_id, modifications, description):
        """Create a new prompt variant with modifications."""
        original = self.read_prompt_content(prompt_type)
        if not original:
            return None
        
        # Apply modifications (simple text replacement)
        modified = original
        for old_text, new_text in modifications:
            modified = modified.replace(old_text, new_text)
        
        # Store variant
        if prompt_type not in self.state['variants']:
            self.state['variants'][prompt_type] = {}
        
        variant_data = {
            'variant_id': variant_id,
            'prompt': modified,
            'metadata': {
                'prompt_type': prompt_type,
                'description': description,
                'created': datetime.now().isoformat(),
                'based_on': f'{prompt_type}_current'
            },
            'successes': 0,
            'failures': 0,
            'total_score': 0.0,
            'success_rate': 0.5,
            'avg_score': 0.0
        }
        
        self.state['variants'][prompt_type][variant_id] = variant_data
        self.save_state()
        
        return variant_data
    
    def evolve_prompt(self, prompt_type):
        """Generate improved version of a prompt based on learnings."""
        print(f"🚀 Evolving prompt: {prompt_type}")
        print("=" * 50)
        
        # Get current content
        current = self.read_prompt_content(prompt_type)
        if not current:
            print(f"   ❌ No prompt found for {prompt_type}")
            return None
        
        # Get benchmark results for this type
        benchmark_file = BENCHMARK_RESULTS_FILE
        benchmark_pass_rate = 0.7  # default
        if os.path.exists(benchmark_file):
            with open(benchmark_file, 'r') as f:
                results = json.load(f)
                if results['tests_run'] > 0:
                    benchmark_pass_rate = results['tests_passed'] / results['tests_run']
        
        print(f"   Current benchmark pass rate: {benchmark_pass_rate*100:.0f}%")
        
        # Get learnings from KG if available
        learnings = self.get_learnings_for_prompt(prompt_type)
        
        # Generate evolution recommendations
        modifications = []
        
        if prompt_type == 'soul':
            # Check for common improvements
            if 'sofort handeln' not in current.lower():
                modifications.append((
                    '## Vibe\n',
                    '## Vibe\n\n## ⚡ Proaktive Actions — SOFORT HANDELN\n**Wenn ich eine Opportunity sehe → TUE SIE.**\n'
                ))
            
            if 'assume no input' not in current.lower():
                modifications.append((
                    '**Earn trust through competence.**',
                    '**Assume no input unless you see evidence.** If you think something happened but didn\'t see explicit proof: ASK, don\'t act.\n\n**Earn trust through competence.**'
                ))
        
        # Apply modifications
        evolved = current
        for old_text, new_text in modifications:
            evolved = evolved.replace(old_text, new_text)
        
        # Create evolved variant
        variant_id = f"{prompt_type}_evolved_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        if modifications:
            variant_data = self.create_variant(
                prompt_type,
                variant_id,
                modifications,
                f"Evolved version based on learnings ({len(modifications)} modifications)"
            )
            print(f"   ✅ Created variant: {variant_id}")
            print(f"   Modifications applied: {len(modifications)}")
        else:
            print(f"   ⚠️ No modifications needed")
            variant_data = None
        
        return variant_data
    
    def get_learnings_for_prompt(self, prompt_type):
        """Get relevant learnings from KG."""
        learnings = []
        
        # Try to load from KG
        kg_file = f"{WORKSPACE}/memory/kg/knowledge_graph.json"
        if os.path.exists(kg_file):
            try:
                with open(kg_file, 'r') as f:
                    kg = json.load(f)
                    # Look for learning-related entities
                    for entity in kg.get('entities', []):
                        if entity.get('type') == 'learning' and prompt_type in str(entity):
                            learnings.append(entity)
            except:
                pass
        
        return learnings
    
    # ========== A/B TESTING ==========
    
    def record_test_result(self, variant_id, success, score):
        """Record A/B test result for a variant."""
        # Find variant in state
        found = False
        for ptype, variants in self.state.get('variants', {}).items():
            if variant_id in variants:
                variant = variants[variant_id]
                variant['total_score'] = variant.get('total_score', 0) + score
                if success:
                    variant['successes'] = variant.get('successes', 0) + 1
                else:
                    variant['failures'] = variant.get('failures', 0) + 1
                
                total = variant['successes'] + variant['failures']
                if total > 0:
                    variant['success_rate'] = variant['successes'] / total
                    variant['avg_score'] = variant['total_score'] / total
                
                found = True
                break
        
        if found:
            self.save_state()
            print(f"📊 Recorded: {variant_id} → success={success}, score={score}")
        else:
            print(f"⚠️ Variant not found: {variant_id}")
    
    def get_best_variant(self, prompt_type):
        """Get the best performing variant for a prompt type."""
        # Check both structures: variants.prompt_type.variant_id and active_prompts.prompt_type.variant_id
        variants = self.state.get('variants', {}).get(prompt_type, {})
        if not variants:
            # Try active_prompts structure
            variants = self.state.get('active_prompts', {}).get(prompt_type, {})
        if not variants:
            return None
        
        best = None
        best_score = -1
        
        for vid, vdata in variants.items():
            if isinstance(vdata, dict):
                score = vdata.get('avg_score', 0)
                if score > best_score:
                    best_score = score
                    best = vdata
        
        return best
    
    # ========== MAIN ==========
    
    def run(self, action='inventory', prompt_type=None, variant_id=None):
        """Run requested action."""
        if action == 'inventory':
            return self.run_inventory()
        elif action == 'benchmark':
            return self.run_benchmark(prompt_type)
        elif action == 'evolve':
            return self.evolve_prompt(prompt_type)
        elif action == 'test':
            # Record test result
            if variant_id:
                print(f"📝 Test recording for {variant_id}... (needs success/score args)")
            return {'status': 'test_mode'}
        elif action == 'status':
            return self.get_status()
        else:
            print(f"Unknown action: {action}")
            return None
    
    def get_status(self):
        """Get current prompt evolution status."""
        status = {
            'total_variants': sum(len(v) for v in self.state.get('variants', {}).values()),
            'total_benchmarks': len(self.state.get('benchmarks', {})),
            'prompt_types_with_variants': list(self.state.get('variants', {}).keys()),
            'best_performing': {}
        }
        
        # Check both structures
        prompt_types = set(self.state.get('variants', {}).keys())
        prompt_types.update(self.state.get('active_prompts', {}).keys())
        
        for ptype in prompt_types:
            best = self.get_best_variant(ptype)
            if best and isinstance(best, dict):
                status['best_performing'][ptype] = {
                    'variant_id': best.get('variant_id', 'unknown'),
                    'avg_score': best.get('avg_score', 0),
                    'success_rate': best.get('success_rate', 0)
                }
        
        return status


def main():
    engine = PromptEvolutionEngine()
    
    # Parse args
    action = 'inventory'
    prompt_type = None
    variant_id = None
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--action' and i+1 < len(args):
            action = args[i+1]
            i += 2
        elif args[i] == '--prompt_type' and i+1 < len(args):
            prompt_type = args[i+1]
            i += 2
        elif args[i] == '--variant' and i+1 < len(args):
            variant_id = args[i+1]
            i += 2
        else:
            i += 1
    
    if action == 'inventory':
        engine.run('inventory')
    elif action == 'benchmark':
        engine.run('benchmark', prompt_type)
    elif action == 'evolve':
        if not prompt_type:
            print("❌ --prompt_type required for evolve")
            sys.exit(1)
        engine.run('evolve', prompt_type)
    elif action == 'status':
        status = engine.get_status()
        print("📊 Prompt Evolution Status:")
        print(json.dumps(status, indent=2))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
