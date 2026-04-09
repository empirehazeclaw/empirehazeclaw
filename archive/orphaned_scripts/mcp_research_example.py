#!/usr/bin/env python3
"""
Beispiel: Research Agent mit MCP Tools
Usage: python3 scripts/mcp_research_example.py
"""

import asyncio
import sys
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE))


class ResearchAgentMCP:
    """Research Agent mit MCP-Tool-Unterstützung"""
    
    def __init__(self):
        from core.base_agent import BaseAgent
        
        self.agent = BaseAgent(
            name="ResearchAgent",
            system_prompt="""Du bist ein exzellenter Research-Agent.
            Du suchst aktiv nach Informationen, fasst Ergebnisse zusammen
            und lieferst strukturierte Antworten.""",
            mcp_servers=[
                {
                    "name": "openclaw",
                    "command": [sys.executable, str(WORKSPACE / "core" / "mcp_server.py")],
                    "env": {"PYTHONPATH": str(WORKSPACE)}
                }
            ]
        )
    
    async def research(self, topic: str) -> str:
        """Führe Research zu einem Thema durch"""
        
        # 1. Liste verfügbare Tools
        tools = await self.agent.list_mcp_tools()
        print(f"🔧 Verfügbare Tools: {[t['name'] for t in tools]}")
        
        # 2. Suche im Web
        print(f"\n🔍 Suche nach: {topic}")
        search_result = await self.agent.call_mcp_tool(
            "openclaw",
            "web_search",
            {"query": topic, "count": 3, "freshness": "month"}
        )
        
        # 3. Check Memory für frühere Research
        print("\n🧠 Check Memory...")
        memory_result = await self.agent.call_mcp_tool(
            "openclaw",
            "memory_search",
            {"query": topic, "limit": 3}
        )
        
        # 4. Baue Ergebnis
        result = f"""
## Research: {topic}

### Suchergebnisse
{search_result.get('result', 'Keine Ergebnisse') if search_result else 'Fehler'}

### Relevante Memory-Einträge
{f'{memory_result.get('files_found', 0)} Dateien gefunden' if memory_result else 'Keine'}
"""
        
        return result
    
    async def close(self):
        await self.agent.cleanup()


async def main():
    print("=" * 60)
    print("🧪 MCP Research Agent Demo")
    print("=" * 60)
    
    agent = ResearchAgentMCP()
    
    try:
        # Test verschiedene Research Queries
        topics = [
            "KI Trends 2026",
            "OpenAI GPT-5",
        ]
        
        for topic in topics:
            print(f"\n{'='*40}")
            result = await agent.research(topic)
            print(result[:500] + "..." if len(result) > 500 else result)
        
        print("\n✅ Demo abgeschlossen!")
        
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())