#!/usr/bin/env python3
"""
Signal Injector for Mad-Dog Mode
=================================
Injects our system's signals into evolver's memory_graph.
This bridges our KG + Learning Loop to the mad-dog evolver.

Usage:
    python3 signal_injector.py --inject
"""

import json
from datetime import datetime
from pathlib import Path

EVOLVER_GRAPH = Path("/home/clawbot/.openclaw/workspace/skills/capability-evolver/memory/evolution/memory_graph.jsonl")
OUR_SIGNALS = Path("/home/clawbot/.openclaw/workspace/ceo/memory/evaluations/learning_loop_signal.json")


def read_our_signals():
    """Read signals from our Learning Loop."""
    if not OUR_SIGNALS.exists():
        return None
    with open(OUR_SIGNALS) as f:
        data = json.load(f)
    return data.get('signals', [])


def inject_signals(signals):
    """Inject signals as memory_graph events."""
    if not signals:
        print("No signals to inject")
        return
    
    # Build MemoryGraphEvent
    event = {
        "type": "MemoryGraphEvent",
        "kind": "signal",
        "id": f"mge_{int(datetime.now().timestamp()*1000)}_ceo_inject",
        "ts": datetime.now().isoformat(),
        "signal": {
            "key": "|".join(signals),
            "signals": signals,
            "error_signature": None,
            "source": "ceo_learning_loop"
        },
        "observed": {
            "agent": "ceo",
            "session_scope": "signal_injector",
            "drift_enabled": False,
            "review_mode": False,
            "dry_run": False,
            "system_health": "injected_from_learning_loop",
            "mood": "informed",
            "scan_ms": 0,
            "memory_size_bytes": 0,
            "recent_error_count": 0,
            "node": "v22.22.2",
            "platform": "linux",
            "cwd": "/home/clawbot/.openclaw/workspace/ceo",
            "evidence": {
                "recent_session_tail": "signal_injector",
                "today_log_tail": "signal_injector"
            }
        }
    }
    
    # Append to memory_graph.jsonl
    with open(EVOLVER_GRAPH, 'a') as f:
        f.write(json.dumps(event) + '\n')
    
    print(f"Injected {len(signals)} signals: {signals}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--inject', action='store_true', help='Inject signals from Learning Loop')
    args = parser.parse_args()
    
    if args.inject:
        signals = read_our_signals()
        if signals:
            print(f"Found {len(signals)} signals in Learning Loop")
            inject_signals(signals)
        else:
            print("No signals in Learning Loop")


if __name__ == '__main__':
    main()