#!/usr/bin/env python3
"""
Simple Load Balancer - Distribute tasks across agents
"""
from collections import deque

class TaskBalancer:
    def __init__(self, agents):
        self.agents = deque(agents)
        self.stats = {a: 0 for a in agents}
    
    def assign(self, task):
        """Assign task to least busy agent"""
        agent = min(self.agents, key=lambda a: self.stats[a])
        self.stats[agent] += 1
        return agent
    
    def release(self, agent):
        """Mark agent as free"""
        self.stats[agent] -= 1

# Usage
if __name__ == "__main__":
    balancer = TaskBalancer(["revenue", "content", "mail", "research"])
    for i in range(10):
        agent = balancer.assign(f"task_{i}")
        print(f"Task {i} → {agent}")
