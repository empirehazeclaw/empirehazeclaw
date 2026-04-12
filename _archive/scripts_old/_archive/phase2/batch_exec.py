#!/usr/bin/env python3
"""
BATCH EXEC OPTIMIZER
Combines multiple shell commands into one call to reduce exec overhead

Usage:
  python3 batch_exec.py --commands "cmd1 && cmd2" "cmd3 && cmd4"
"""
import sys
import subprocess

def batch_execute(commands):
    """Execute multiple commands in sequence, return combined output"""
    results = []
    for cmd in commands:
        try:
            result = subprocess.run(cmd, shell=False, capture_output=True, text=True, timeout=30)
            results.append({
                'command': cmd,
                'stdout': result.stdout.strip(),
                'stderr': result.stderr.strip(),
                'returncode': result.returncode
            })
        except Exception as e:
            results.append({'command': cmd, 'error': str(e)})
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: batch_exec.py 'cmd1 && cmd2' 'cmd3'")
        print("Example: batch_exec.py 'df -h' 'ps aux | grep node' 'ls -la /home/clawbot'")
        return 1
    
    commands = sys.argv[1:]
    results = batch_execute(commands)
    
    for i, res in enumerate(results):
        print(f"=== Command {i+1}: {res['command']} ===")
        if 'error' in res:
            print(f"ERROR: {res['error']}")
        else:
            if res['stdout']:
                print(res['stdout'])
            if res['stderr']:
                print(f"STDERR: {res['stderr']}")
            print(f"Exit: {res['returncode']}")
        print()
    
    return 0

if __name__ == "__main__":
    exit(main())
