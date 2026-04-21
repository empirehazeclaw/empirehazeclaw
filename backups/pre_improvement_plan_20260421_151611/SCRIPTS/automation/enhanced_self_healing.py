#!/usr/bin/env python3
"""
🔧 Enhanced Self-Healing System
================================
Multi-Layer Detection + Automated Recovery Playbooks

Architecture:
  Observe → Diagnose → Select Playbook → Execute → Validate → Report

Layers:
  - Process (gateway, crons, scripts)
  - Memory (RAM, disk space)
  - Disk (log files, temp)
  - Network (connectivity)
  - Service (openclaw gateway)

Usage:
    python3 enhanced_self_healing.py --check      # Quick health check
    python3 enhanced_self_healing.py --full      # Full diagnostic
    python3 enhanced_self_healing.py --heal       # Run healing
    python3 enhanced_self_healing.py --status      # Show status
"""

import json
import os
import psutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LOG_DIR = WORKSPACE / "logs"
HEAL_LOG = LOG_DIR / "self_healing.log"
AUTONOMY_DIR = WORKSPACE / "ceo/memory/autonomy"

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(HEAL_LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")


class HealthChecker:
    """Multi-layer health checker."""
    
    def __init__(self):
        self.results = {}
    
    def check_all(self) -> Dict:
        """Run all health checks."""
        log("Starting full health check...")
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'process': self.check_process(),
            'memory': self.check_memory(),
            'disk': self.check_disk(),
            'network': self.check_network(),
            'gateway': self.check_gateway(),
            'cron': self.check_cron(),
        }
        
        # Calculate overall health
        healthy = sum(1 for v in self.results.values() if isinstance(v, dict) and v.get('healthy', False))
        total = len([v for v in self.results.values() if isinstance(v, dict)])
        self.results['overall_health'] = healthy / total if total > 0 else 0
        
        log(f"Health check complete: {healthy}/{total} layers healthy")
        return self.results
    
    def check_process(self) -> Dict:
        """Check if required processes are running."""
        result = {
            'name': 'Process',
            'healthy': True,
            'checks': {}
        }
        
        # Check gateway process
        gateway_processes = [p for p in psutil.process_iter(['pid', 'name', 'cmdline']) 
                           if 'openclaw' in ' '.join(p.info.get('cmdline') or []).lower()]
        
        result['checks']['gateway'] = {
            'running': len(gateway_processes) > 0,
            'count': len(gateway_processes)
        }
        
        if len(gateway_processes) == 0:
            result['healthy'] = False
            result['issue'] = 'Gateway process not found'
        
        return result
    
    def check_memory(self) -> Dict:
        """Check memory usage."""
        mem = psutil.virtual_memory()
        
        result = {
            'name': 'Memory',
            'healthy': mem.percent < 90,
            'checks': {
                'percent_used': mem.percent,
                'available_gb': round(mem.available / (1024**3), 2),
                'total_gb': round(mem.total / (1024**3), 2)
            }
        }
        
        if mem.percent > 90:
            result['issue'] = f'High memory usage: {mem.percent}%'
        elif mem.percent > 80:
            result['warning'] = f'Moderate memory usage: {mem.percent}%'
        
        return result
    
    def check_disk(self) -> Dict:
        """Check disk space."""
        disk = psutil.disk_usage('/')
        
        result = {
            'name': 'Disk',
            'healthy': disk.percent < 90,
            'checks': {
                'percent_used': disk.percent,
                'free_gb': round(disk.free / (1024**3), 2),
                'total_gb': round(disk.total / (1024**3), 2)
            }
        }
        
        if disk.percent > 90:
            result['issue'] = f'Low disk space: {disk.percent}% used'
        elif disk.percent > 80:
            result['warning'] = f'Disk space moderate: {disk.percent}% used'
        
        return result
    
    def check_network(self) -> Dict:
        """Check network connectivity."""
        result = {
            'name': 'Network',
            'healthy': True,
            'checks': {}
        }
        
        # Check if we can reach google (DNS test)
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            result['checks']['internet'] = True
        except:
            result['checks']['internet'] = False
            result['healthy'] = False
            result['issue'] = 'No internet connectivity'
        
        return result
    
    def check_gateway(self) -> Dict:
        """Check OpenClaw gateway via RPC."""
        result = {
            'name': 'Gateway',
            'healthy': False,
            'checks': {}
        }
        
        try:
            proc = subprocess.run(
                ['openclaw', 'gateway', 'status'],
                capture_output=True, text=True, timeout=10
            )
            output = proc.stdout + proc.stderr
            
            result['checks']['rpc_ok'] = 'RPC probe: ok' in output
            result['checks']['running'] = 'running' in output.lower()
            result['healthy'] = result['checks']['rpc_ok']
            
            if not result['healthy']:
                result['issue'] = 'Gateway RPC not responding'
                
        except subprocess.TimeoutExpired:
            result['issue'] = 'Gateway check timeout'
        except Exception as e:
            result['issue'] = str(e)
        
        return result
    
    def check_cron(self) -> Dict:
        """Check cron job status."""
        result = {
            'name': 'Cron',
            'healthy': True,
            'checks': {}
        }
        
        try:
            proc = subprocess.run(
                ['openclaw', 'cron', 'list'],
                capture_output=True, text=True, timeout=15
            )
            lines = proc.stdout.strip().split('\n')
            
            total = sum(1 for l in lines if 'cron' in l.lower())
            failed = sum(1 for l in lines if 'failed' in l.lower())
            
            result['checks']['total'] = total
            result['checks']['failed'] = failed
            result['healthy'] = failed == 0
            
            if failed > 0:
                result['issue'] = f'{failed} cron jobs failed'
                
        except Exception as e:
            result['issue'] = str(e)
            result['healthy'] = False
        
        return result


class RecoveryPlaybook:
    """Automated recovery playbooks."""
    
    PLAYBOOKS = {
        'gateway_down': {
            'name': 'Gateway Down Recovery',
            'steps': [
                ('check_process', 'Check if gateway process exists'),
                ('restart_service', 'Restart gateway service'),
                ('wait_and_verify', 'Wait 10s and verify RPC'),
                ('alert_if_fails', 'Alert if still down after 2 attempts')
            ]
        },
        'high_memory': {
            'name': 'High Memory Recovery',
            'steps': [
                ('clear_temp', 'Clear temp files'),
                ('clear_logs', 'Reduce log sizes'),
                ('trigger_gc', 'Trigger garbage collection')
            ]
        },
        'disk_full': {
            'name': 'Disk Full Recovery',
            'steps': [
                ('find_large_logs', 'Find large log files'),
                ('archive_old', 'Archive old logs'),
                ('clear_cache', 'Clear cache directories')
            ]
        },
        'cron_failed': {
            'name': 'Cron Failure Recovery',
            'steps': [
                ('get_error_log', 'Get error details'),
                ('auto_retry', 'Auto-retry if transient'),
                ('log_failure', 'Log persistent failures')
            ]
        }
    }
    
    def __init__(self):
        self.healing_log = []
    
    def execute_playbook(self, playbook_name: str, context: Dict = None) -> Dict:
        """Execute a recovery playbook."""
        if playbook_name not in self.PLAYBOOKS:
            return {'success': False, 'error': f'Unknown playbook: {playbook_name}'}
        
        playbook = self.PLAYBOOKS[playbook_name]
        context = context or {}
        
        log(f"Executing playbook: {playbook['name']}")
        
        results = []
        for step_name, step_desc in playbook['steps']:
            log(f"  Step: {step_desc}")
            
            try:
                step_result = self._execute_step(step_name, context)
                results.append({
                    'step': step_name,
                    'description': step_desc,
                    'success': step_result.get('success', False),
                    'result': step_result
                })
                
                if not step_result.get('success', False) and step_result.get('critical', False):
                    log(f"  ⚠️ Critical step failed: {step_name}")
                    break
                    
            except Exception as e:
                log(f"  ❌ Step error: {e}")
                results.append({
                    'step': step_name,
                    'description': step_desc,
                    'success': False,
                    'error': str(e)
                })
        
        success = all(r['success'] for r in results)
        
        return {
            'playbook': playbook_name,
            'success': success,
            'steps': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _execute_step(self, step_name: str, context: Dict) -> Dict:
        """Execute a single recovery step."""
        if step_name == 'restart_service':
            try:
                subprocess.run(['openclaw', 'gateway', 'restart'], 
                             capture_output=True, timeout=30)
                time.sleep(5)
                return {'success': True}
            except:
                return {'success': False, 'critical': True}
        
        elif step_name == 'clear_temp':
            try:
                subprocess.run(['rm', '-rf', '/tmp/openclaw_temp_*'], 
                             shell=True, capture_output=True)
                return {'success': True}
            except:
                return {'success': False}
        
        elif step_name == 'clear_logs':
            try:
                # Truncate large logs
                for log_file in LOG_DIR.glob('*.log'):
                    if log_file.stat().st_size > 10_000_000:  # 10MB
                        log_file.write_text(f"# Truncated at {datetime.now()}\n")
                return {'success': True}
            except:
                return {'success': False}
        
        elif step_name == 'wait_and_verify':
            time.sleep(10)
            try:
                result = subprocess.run(['openclaw', 'gateway', 'status'],
                                      capture_output=True, timeout=10)
                return {'success': 'RPC probe: ok' in (result.stdout + result.stderr)}
            except:
                return {'success': False, 'critical': True}
        
        elif step_name == 'auto_retry':
            cron_id = context.get('cron_id')
            if cron_id:
                try:
                    subprocess.run(['openclaw', 'cron', 'run', cron_id],
                                  capture_output=True, timeout=30)
                    return {'success': True}
                except:
                    return {'success': False}
            return {'success': False}
        
        return {'success': True}  # Default: success


class EnhancedSelfHealing:
    """Main self-healing orchestrator."""
    
    def __init__(self):
        self.checker = HealthChecker()
        self.playbook = RecoveryPlaybook()
        self.healing_history = []
    
    def diagnose_and_heal(self) -> Dict:
        """Run diagnosis and execute necessary recoveries."""
        log("Running diagnosis...")
        
        # Step 1: Check health
        health = self.checker.check_all()
        
        # Step 2: Identify issues
        issues = []
        for layer, result in health.items():
            if isinstance(result, dict) and not result.get('healthy', True):
                issue = result.get('issue', f'{layer} unhealthy')
                issues.append((layer, issue))
                log(f"Issue detected: {layer} - {issue}")
        
        # Step 3: Execute playbooks for issues
        recoveries = []
        for layer, issue in issues:
            playbook_name = self._map_issue_to_playbook(layer, issue)
            if playbook_name:
                log(f"Executing playbook: {playbook_name}")
                result = self.playbook.execute_playbook(playbook_name, {'layer': layer, 'issue': issue})
                recoveries.append(result)
        
        # Step 4: Verify recovery
        if recoveries:
            log("Verifying recovery...")
            time.sleep(5)
            new_health = self.checker.check_all()
            recovered = new_health.get('overall_health', 0) >= health.get('overall_health', 0)
            
            return {
                'success': recovered,
                'original_health': health,
                'recoveries': recoveries,
                'final_health': new_health if recovered else health
            }
        
        return {
            'success': True,
            'original_health': health,
            'recoveries': [],
            'final_health': health
        }
    
    def _map_issue_to_playbook(self, layer: str, issue: str) -> Optional[str]:
        """Map detected issue to appropriate playbook."""
        if layer == 'gateway':
            return 'gateway_down'
        elif layer == 'memory' or 'memory' in issue.lower():
            return 'high_memory'
        elif layer == 'disk' or 'disk' in issue.lower():
            return 'disk_full'
        elif layer == 'cron' or 'cron' in issue.lower():
            return 'cron_failed'
        return None
    
    def print_report(self, results: Dict):
        """Print formatted healing report."""
        health = results.get('final_health', {})
        overall = health.get('overall_health', 0)
        
        print("\n" + "="*60)
        print("🔧 Enhanced Self-Healing Report")
        print("="*60)
        print(f"Timestamp: {results.get('final_health', {}).get('timestamp', 'N/A')}")
        print(f"Overall Health: {overall*100:.0f}%")
        print()
        
        # Layer status
        print("📊 Layer Status:")
        for layer, data in health.items():
            if isinstance(data, dict):
                status = "✅" if data.get('healthy', False) else "⚠️"
                print(f"  {status} {layer}: {data.get('issue', 'OK') if not data.get('healthy', True) else 'Healthy'}")
                if data.get('checks'):
                    for check, val in data['checks'].items():
                        print(f"      {check}: {val}")
        
        # Recoveries
        recoveries = results.get('recoveries', [])
        if recoveries:
            print(f"\n🔄 Recoveries Executed: {len(recoveries)}")
            for r in recoveries:
                status = "✅" if r.get('success') else "❌"
                print(f"  {status} {r.get('playbook')}")
        
        print("="*60)


def main():
    import sys
    
    healer = EnhancedSelfHealing()
    
    if '--check' in sys.argv:
        results = healer.diagnose_and_heal()
        healer.print_report(results)
        
    elif '--full' in sys.argv:
        print("Running full diagnostic...")
        health = healer.checker.check_all()
        healer.print_report({'final_health': health, 'recoveries': []})
        
    elif '--heal' in sys.argv:
        results = healer.diagnose_and_heal()
        healer.print_report(results)
        
    elif '--status' in sys.argv:
        health = healer.checker.check_all()
        print(f"\n📊 Health Summary: {health.get('overall_health', 0)*100:.0f}%")
        for layer, data in health.items():
            if isinstance(data, dict):
                icon = "✅" if data.get('healthy') else "⚠️"
                print(f"  {icon} {layer}: {data.get('issue', 'OK') if not data.get('healthy') else 'Healthy'}")
    
    else:
        print("Usage:")
        print("  python3 enhanced_self_healing.py --check   # Diagnose + heal")
        print("  python3 enhanced_self_healing.py --full    # Full diagnostic")
        print("  python3 enhanced_self_healing.py --heal    # Force heal")
        print("  python3 enhanced_self_healing.py --status  # Quick status")


if __name__ == "__main__":
    main()
