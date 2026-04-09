#!/usr/bin/env python3
"""
🎯 LLM Wrapper - For other agents to use smart LLM routing

Usage in other agents:
    from scripts.use_llm import query_llm
    
    result = query_llm("What is Python?", priority="speed")
    print(result["response"])
"""

import sys
import json
from pathlib import Path

def query_llm(prompt, priority="balanced", use_cache=True, strategy="round_robin"):
    """
    Query LLM with smart routing.
    
    Returns: {
        "success": bool,
        "response": str,
        "model": str,
        "latency": int,
        "cost": float,
        "cached": bool
    }
    """
    # Import the router
    sys.path.insert(0, str(Path(__file__).parent))
    from llm_router import LLMRouter
    
    router = LLMRouter()
    return router.query(
        prompt=prompt,
        priority=priority,
        use_cache=use_cache,
        strategy=strategy
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM Query Wrapper")
    parser.add_argument("query", help="Query to execute")
    parser.add_argument("--priority", "-p", default="balanced",
                       choices=["speed", "quality", "cost", "balanced"])
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--strategy", "-s", default="round_robin")
    
    args = parser.parse_args()
    
    result = query_llm(
        prompt=args.query,
        priority=args.priority,
        use_cache=not args.no_cache,
        strategy=args.strategy
    )
    
    if result["success"]:
        print(f"✅ {result['model']}")
        print(f"Latency: {result.get('latency', 0)}ms | Cost: ${result.get('cost', 0):.6f}")
        print(f"\n{result['response']}")
    else:
        print(f"❌ Failed: {result.get('error')}")
