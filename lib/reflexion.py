"""
🔄 REFLEXION AGENT
=================
Self-healing and error recovery
"""

import sys
import asyncio
sys.path.insert(0, '.')

from core.reflexion_agent import ReflexionAgent

# Create instance with name
reflexion = ReflexionAgent(name="system", max_retries=3)

async def analyze_error(error):
    """Analyze and fix errors"""
    # Simplified - full implementation would use LLM
    return {"status": "analyzed", "error": str(error)}

async def heal(task, error):
    """Attempt to heal from error"""
    return await reflexion.run_with_reflexion(task)

def heal_sync(task, error):
    """Sync wrapper for heal"""
    return asyncio.run(heal(task, error))

if __name__ == "__main__":
    result = heal_sync("post tweet", "API rate limit")
    print(f"🔄 Reflexion: {result}")
