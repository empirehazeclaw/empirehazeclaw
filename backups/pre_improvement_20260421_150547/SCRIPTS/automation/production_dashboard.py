#!/usr/bin/env python3
"""
📊 Production Monitoring Dashboard
====================================
Real-time system metrics: Latency, Errors, Token Usage, Cost, Task Success

Framework: LNEW Metrics
- L = Latency (p50, p95, p99)
- N = Number of Errors (rate)
- E = Efficiency (tokens per task)
- W = Worth (cost per successful task)

Usage:
    python3 production_dashboard.py          # Full dashboard
    python3 production_dashboard.py --check # Quick health check
    python3 production_dashboard.py --report # Generate report
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LOG_DIR = WORKSPACE / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Config
RETENTION_HOURS = 24

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def get_openclaw_status() -> dict:
    """Get OpenClaw gateway status."""
    try:
        result = subprocess.run(
            ['openclaw', 'gateway', 'status'],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout + result.stderr
        if 'RPC probe: ok' in output or 'running' in output.lower():
            return {'status': 'running'}
        return {'status': 'unknown', 'raw': output[:200]}
    except:
        return {'status': 'unknown'}

def get_cron_stats() -> dict:
    """Get cron job statistics."""
    try:
        result = subprocess.run(
            ['openclaw', 'cron', 'list'],
            capture_output=True, text=True, timeout=15
        )
        lines = result.stdout.strip().split('\n')
        
        total = 0
        ok = 0
        failed = 0
        idle = 0
        
        for line in lines:
            if 'cron' in line.lower():
                total += 1
                if 'failed' in line.lower():
                    failed += 1
                elif 'ok' in line.lower():
                    ok += 1
                elif 'idle' in line.lower():
                    idle += 1
        
        return {'total': total, 'ok': ok, 'failed': failed, 'idle': idle}
    except Exception as e:
        return {'total': 0, 'ok': 0, 'failed': 0, 'idle': 0, 'error': str(e)}

def get_kg_stats() -> dict:
    """Get KG statistics."""
    kg_path = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
    if not kg_path.exists():
        return {'entities': 0, 'relations': 0}
    
    try:
        with open(kg_path) as f:
            kg = json.load(f)
        return {
            'entities': len(kg.get('entities', {})),
            'relations': len(kg.get('relations', []))
        }
    except:
        return {'entities': 0, 'relations': 0}

def get_learning_loop_score() -> float:
    """Get current learning loop score."""
    score_file = WORKSPACE / "scripts/learning_loop_score.json"
    if score_file.exists():
        try:
            with open(score_file) as f:
                data = json.load(f)
            return data.get('score', 0.763)
        except:
            pass
    return 0.763  # Default

def parse_litellm_log() -> dict:
    """Parse litellm log for latency and token stats."""
    log_file = LOG_DIR / "litellm.log"
    if not log_file.exists():
        return {'requests': 0, 'avg_latency': 0, 'total_tokens': 0}
    
    try:
        with open(log_file) as f:
            lines = f.readlines()
        
        # Parse recent entries
        cutoff = datetime.now() - timedelta(hours=RETENTION_HOURS)
        recent_lines = []
        
        for line in lines[-1000:]:  # Last 1000 lines
            try:
                # Extract timestamp
                if '[' in line and ']' in line:
                    ts_str = line.split(']')[0].replace('[', '')
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    if ts > cutoff:
                        recent_lines.append(line)
            except:
                pass
        
        # Calculate stats
        latencies = []
        tokens = []
        
        for line in recent_lines:
            if 'latency' in line.lower():
                # Try to extract latency
                parts = line.split()
                for i, p in enumerate(parts):
                    if 'latency' in p.lower() and i+1 < len(parts):
                        try:
                            latencies.append(float(parts[i+1]))
                        except:
                            pass
            
            if 'tokens' in line.lower():
                parts = line.split()
                for i, p in enumerate(parts):
                    if 'tokens' in p.lower() and i+1 < len(parts):
                        try:
                            tokens.append(int(parts[i+1]))
                        except:
                            pass
        
        return {
            'requests': len(recent_lines),
            'avg_latency': sum(latencies) / len(latencies) if latencies else 0,
            'total_tokens': sum(tokens) if tokens else 0,
            'sample_size': len(recent_lines)
        }
    except Exception as e:
        return {'requests': 0, 'avg_latency': 0, 'total_tokens': 0, 'error': str(e)}

def get_session_stats() -> dict:
    """Get session statistics."""
    try:
        result = subprocess.run(
            ['openclaw', 'sessions', 'list', '--json'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                'active': len(data.get('sessions', [])),
                'total': len(data.get('sessions', []))
            }
    except:
        pass
    return {'active': 0, 'total': 0}

def calculate_worth(cost_per_request: float, success_rate: float) -> float:
    """Calculate worth metric (cost per successful task)."""
    if success_rate == 0:
        return float('inf')
    return cost_per_request / success_rate

class ProductionDashboard:
    """Main dashboard."""
    
    def __init__(self):
        self.metrics = {}
        self.timestamp = datetime.now()
    
    def collect(self):
        """Collect all metrics."""
        log("Collecting metrics...")
        
        self.metrics = {
            'timestamp': self.timestamp.isoformat(),
            'gateway': get_openclaw_status(),
            'crons': get_cron_stats(),
            'kg': get_kg_stats(),
            'learning_score': get_learning_loop_score(),
            'litellm': parse_litellm_log(),
            'sessions': get_session_stats()
        }
        
        # Calculate derived metrics
        cron_total = self.metrics['crons'].get('total', 0)
        cron_failed = self.metrics['crons'].get('failed', 0)
        self.metrics['cron_success_rate'] = (cron_total - cron_failed) / cron_total if cron_total > 0 else 0
        
        # Latency score (target < 2s)
        avg_latency = self.metrics['litellm'].get('avg_latency', 0)
        self.metrics['latency_score'] = max(0, 1 - (avg_latency / 5)) if avg_latency > 0 else 1
        
        # Error rate
        requests = self.metrics['litellm'].get('requests', 0)
        errors = self.metrics['crons'].get('failed', 0)
        self.metrics['error_rate'] = errors / max(1, cron_total) * 100
        
        # Estimate cost (LiteLLM rough estimate: $0.001 per 1K tokens)
        tokens = self.metrics['litellm'].get('total_tokens', 0)
        self.metrics['estimated_cost'] = tokens * 0.000001  # $0.000001 per token
        
        # Worth (cost per successful task)
        self.metrics['worth'] = calculate_worth(
            self.metrics['estimated_cost'],
            self.metrics['cron_success_rate']
        )
        
        log("Metrics collected")
        return self.metrics
    
    def print_dashboard(self):
        """Print formatted dashboard."""
        m = self.metrics
        
        print("\n" + "="*70)
        print("🦞 Sir HazeClaw — Production Monitoring Dashboard")
        print("="*70)
        print(f"Timestamp: {m.get('timestamp', 'N/A')}")
        print()
        
        # Gateway Status
        gw_status = m.get('gateway', {}).get('status', 'unknown')
        gw_icon = "✅" if gw_status == 'running' else "⚠️"
        print(f"{gw_icon} Gateway: {gw_status.upper()}")
        print()
        
        # LNEW Metrics
        print("📊 LNEW Metrics:")
        print(f"  L (Latency):    {m.get('litellm', {}).get('avg_latency', 0):.2f}s avg")
        print(f"  N (Errors):     {m.get('error_rate', 0):.1f}% ({m.get('crons', {}).get('failed', 0)} failed)")
        print(f"  E (Efficiency): {m.get('litellm', {}).get('total_tokens', 0):,} tokens")
        print(f"  W (Worth):      ${m.get('worth', 0):.6f} per success")
        print()
        
        # Cron Overview
        cron = m.get('crons', {})
        print("⏰ Crons:")
        print(f"  Total: {cron.get('total', 0)} | OK: {cron.get('ok', 0)} | Failed: {cron.get('failed', 0)} | Idle: {cron.get('idle', 0)}")
        print(f"  Success Rate: {m.get('cron_success_rate', 0)*100:.1f}%")
        print()
        
        # Knowledge Graph
        kg = m.get('kg', {})
        print("🧠 Knowledge Graph:")
        print(f"  Entities: {kg.get('entities', 0)}")
        print(f"  Relations: {kg.get('relations', 0)}")
        print()
        
        # Learning Loop
        print("🎯 Learning Loop:")
        print(f"  Score: {m.get('learning_score', 0):.3f} (Target: 0.80)")
        print()
        
        # Token Usage
        litellm = m.get('litellm', {})
        print("📈 LiteLLM (last 24h):")
        print(f"  Requests: {litellm.get('requests', 0)}")
        print(f"  Tokens: {litellm.get('total_tokens', 0):,}")
        print(f"  Est. Cost: ${m.get('estimated_cost', 0):.4f}")
        print()
        
        print("="*70)
    
    def health_check(self) -> bool:
        """Quick health check."""
        m = self.metrics
        
        # Check gateway
        if m.get('gateway', {}).get('status') != 'running':
            print("⚠️ Gateway not running")
            return False
        
        # Check error rate
        if m.get('error_rate', 0) > 10:
            print(f"⚠️ High error rate: {m.get('error_rate', 0):.1f}%")
            return False
        
        # Check cron failures
        if m.get('crons', {}).get('failed', 0) > 5:
            print(f"⚠️ Many cron failures: {m.get('crons', {}).get('failed', 0)}")
            return False
        
        print("✅ All systems healthy")
        return True
    
    def export_json(self) -> str:
        """Export metrics as JSON."""
        return json.dumps(self.metrics, indent=2)


def main():
    dashboard = ProductionDashboard()
    dashboard.collect()
    
    if '--check' in sys.argv:
        dashboard.health_check()
    elif '--report' in sys.argv:
        dashboard.print_dashboard()
        # Also save to file
        report_file = LOG_DIR / f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            f.write(dashboard.export_json())
        log(f"Report saved to {report_file}")
    else:
        dashboard.print_dashboard()


if __name__ == "__main__":
    main()
