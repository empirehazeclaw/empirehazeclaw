#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          AGENT REGISTRY & DISPATCHER                        ║
║          Extensible Agent System                            ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Dynamische Agent-Registrierung
  - Capability-basiertes Routing
  - Keyword-Matching
  - Fallback-Mechanismus

Hinweis: LLM-Routing wird NICHT verwendet
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [REGISTRY] %(message)s")
log = logging.getLogger("openclaw.registry")


class AgentType(str, Enum):
    """Vordefinierte Agent-Typen"""
    RESEARCH = "research"
    CONTENT = "content"
    REVENUE = "revenue"
    CODING = "coding"
    OPERATIONS = "operations"
    GROWTH = "growth"
    POD = "pod"
    SECURITY = "security"  # NEU
    MAIL = "mail"  # NEU


@dataclass
class AgentCapability:
    """Fähigkeiten eines Agenten"""
    agent_type: AgentType
    name: str
    keywords: List[str]
    description: str
    avg_duration_s: float = 5.0
    parallel_safe: bool = True


@dataclass
class AgentInfo:
    """Info über einen registrierten Agent"""
    agent_type: AgentType
    name: str
    handler: Callable
    capabilities: List[AgentCapability]
    enabled: bool = True
    stats: Dict[str, Any] = field(default_factory=lambda: {
        "total_calls": 0,
        "successful": 0,
        "failed": 0,
        "total_duration": 0.0
    })


class AgentRegistry:
    """
    Zentrale Agent-Registry
    
    Usage:
        registry = AgentRegistry()
        
        # Agent registrieren
        @registry.register(AgentType.REVENUE, ["email", "outreach", "lead"])
        async def revenue_handler(action, params):
            return "Done"
        
        # Agent finden
        agent = registry.find_agent("Sende Outreach Email")
    """
    
    def __init__(self):
        self.agents: Dict[AgentType, AgentInfo] = {}
        self.capability_index: Dict[str, Set[AgentType]] = {}  # keyword -> agent types
        
    def register(
        self,
        agent_type: AgentType,
        keywords: List[str],
        description: str = "",
        avg_duration: float = 5.0,
        parallel_safe: bool = True
    ):
        """
        Decorator zum Registrieren eines Agenten
        
        Example:
            @registry.register(
                AgentType.REVENUE,
                ["email", "outreach", "lead", "sales"],
                "Revenue & Sales Agent"
            )
            async def revenue_handler(action, params):
                ...
        """
        def decorator(handler: Callable):
            # Create capability
            capability = AgentCapability(
                agent_type=agent_type,
                name=agent_type.value,
                keywords=keywords,
                description=description,
                avg_duration_s=avg_duration,
                parallel_safe=parallel_safe
            )
            
            # Create agent info
            agent_info = AgentInfo(
                agent_type=agent_type,
                name=agent_type.value,
                handler=handler,
                capabilities=[capability],
                enabled=True
            )
            
            # Register
            self.agents[agent_type] = agent_info
            
            # Build keyword index
            for keyword in keywords:
                if keyword not in self.capability_index:
                    self.capability_index[keyword] = set()
                self.capability_index[keyword].add(agent_type)
            
            log.info(f"✅ Agent registriert: {agent_type.value} | Keywords: {keywords[:3]}...")
            
            return handler
        
        return decorator
    
    def register_handler(self, agent_type: AgentType, handler: Callable, keywords: List[str]):
        """Manuelle Registrierung (ohne Decorator)"""
        capability = AgentCapability(
            agent_type=agent_type,
            name=agent_type.value,
            keywords=keywords,
            description=""
        )
        
        self.agents[agent_type] = AgentInfo(
            agent_type=agent_type,
            name=agent_type.value,
            handler=handler,
            capabilities=[capability]
        )
        
        for keyword in keywords:
            if keyword not in self.capability_index:
                self.capability_index[keyword] = set()
            self.capability_index[keyword].add(agent_type)
        
        log.info(f"✅ Handler registriert: {agent_type.value}")
    
    def find_agent(self, task: str) -> Optional[AgentInfo]:
        """
        Finde besten Agenten für eine Task
        
        Nutzt Keyword-Matching:
        1. Extrahiere Keywords aus Task
        2. Finde Agenten mit meisten Matches
        3. Fallback zu Default
        """
        task_lower = task.lower()
        scores: Dict[AgentType, int] = {}
        
        # Score each agent
        for agent_type, agent_info in self.agents.items():
            if not agent_info.enabled:
                continue
                
            score = 0
            for capability in agent_info.capabilities:
                for keyword in capability.keywords:
                    if keyword.lower() in task_lower:
                        score += 1
            
            if score > 0:
                scores[agent_type] = score
        
        if not scores:
            # Fallback: return first enabled agent
            enabled = [a for a in self.agents.values() if a.enabled]
            return enabled[0] if enabled else None
        
        # Return highest scoring
        best = max(scores, key=scores.get)
        return self.agents[best]
    
    def find_agents_for_workflow(self, task: str) -> List[AgentInfo]:
        """
        Finde ALLE relevanten Agenten für eine Task (für Workflows)
        """
        task_lower = task.lower()
        scores: Dict[AgentType, int] = {}
        
        for agent_type, agent_info in self.agents.items():
            if not agent_info.enabled:
                continue
                
            score = 0
            for capability in agent_info.capabilities:
                for keyword in capability.keywords:
                    if keyword.lower() in task_lower:
                        score += 1
            
            if score > 0:
                scores[agent_type] = score
        
        # Sort by score
        sorted_agents = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        return [self.agents[at] for at in sorted_agents]
    
    def list_agents(self) -> List[AgentInfo]:
        """Liste alle registrierten Agenten"""
        return list(self.agents.values())
    
    def get_agent(self, agent_type: AgentType) -> Optional[AgentInfo]:
        """Hol einen spezifischen Agenten"""
        return self.agents.get(agent_type)
    
    def enable_agent(self, agent_type: AgentType):
        """Aktiviere einen Agenten"""
        if agent_type in self.agents:
            self.agents[agent_type].enabled = True
            log.info(f"✅ Agent enabled: {agent_type.value}")
    
    def disable_agent(self, agent_type: AgentType):
        """Deaktiviere einen Agenten"""
        if agent_type in self.agents:
            self.agents[agent_type].enabled = False
            log.info(f"⏸️ Agent disabled: {agent_type.value}")
    
    def update_stats(self, agent_type: AgentType, success: bool, duration: float):
        """Update Agent-Statistiken"""
        if agent_type in self.agents:
            stats = self.agents[agent_type].stats
            stats["total_calls"] += 1
            if success:
                stats["successful"] += 1
            else:
                stats["failed"] += 1
            stats["total_duration"] += duration
    
    def get_stats(self) -> Dict:
        """Zeige Statistiken für alle Agenten"""
        return {
            agent_type.value: info.stats 
            for agent_type, info in self.agents.items()
        }


# Global registry instance
_global_registry = AgentRegistry()


def get_registry() -> AgentRegistry:
    """Hol die globale Registry"""
    return _global_registry


# Decorator for easy registration
def register_agent(keywords: List[str], description: str = ""):
    """
    Decorator für Agent-Registrierung
    
    Example:
        @register_agent(["email", "outreach"], "Revenue Agent")
        async def revenue_handler(action, params):
            ...
    """
    def decorator(func: Callable):
        # Auto-detect agent type from function name
        name = func.__name__.lower()
        
        if "revenue" in name or "sales" in name:
            agent_type = AgentType.REVENUE
        elif "research" in name:
            agent_type = AgentType.RESEARCH
        elif "content" in name or "blog" in name:
            agent_type = AgentType.CONTENT
        elif "coding" in name or "code" in name or "dev" in name:
            agent_type = AgentType.CODING
        elif "security" in name or "audit" in name:
            agent_type = AgentType.SECURITY
        elif "operations" in name or "ops" in name:
            agent_type = AgentType.OPERATIONS
        elif "growth" in name or "social" in name:
            agent_type = AgentType.GROWTH
        elif "pod" in name or "print" in name:
            agent_type = AgentType.POD
        else:
            agent_type = AgentType.RESEARCH  # Default
        
        _global_registry.register_handler(agent_type, func, keywords)
        
        return func
    
    return decorator


# Example usage
if __name__ == "__main__":
    import asyncio
    
    registry = get_registry()
    
    # Register handlers
    @registry.register(
        AgentType.RESEARCH,
        ["search", "recherche", "finde", "analyse", "web"],
        "Research & Web Search"
    )
    async def research_handler(action, params):
        await asyncio.sleep(0.1)
        return {"status": "success", "data": "Research done"}
    
    @registry.register(
        AgentType.REVENUE,
        ["email", "outreach", "lead", "sales", "kunde"],
        "Sales & Revenue"
    )
    async def revenue_handler(action, params):
        await asyncio.sleep(0.1)
        return {"status": "success", "data": "Revenue done"}
    
    @registry.register(
        AgentType.CONTENT,
        ["blog", "artikel", "content", "schreibe", "post"],
        "Content Creation"
    )
    async def content_handler(action, params):
        await asyncio.sleep(0.1)
        return {"status": "success", "data": "Content done"}
    
    # Test
    print("\n🤖 REGISTRY TEST\n")
    
    agents = registry.list_agents()
    for agent in agents:
        print(f"  {agent.agent_type.value:12} | {agent.enabled}")
    
    print("\n🔍 FIND AGENT TESTS:")
    
    tests = [
        "Recherchiere KI Trends",
        "Sende Outreach Email an Lead",
        "Schreibe Blog Artikel",
        "Fix das Bug im Code"
    ]
    
    for task in tests:
        agent = registry.find_agent(task)
        print(f"  Task: '{task}'")
        print(f"  → Agent: {agent.agent_type.value if agent else 'None'}\n")
    
    print("\n📊 STATS:")
    print(json.dumps(registry.get_stats(), indent=2))
