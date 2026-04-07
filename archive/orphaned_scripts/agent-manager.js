#!/usr/bin/env node
/**
 * Agent Manager - Better parallel agent handling
 * 
 * Improvements:
 * 1. Auto-announce (already works)
 * 2. Max 3 agents guideline
 * 3. Better briefing
 */

const MAX_AGENTS = 3;

class AgentManager {
  constructor() {
    this.active = new Map();
    this.completed = [];
    this.failed = [];
  }
  
  // Check if we can spawn more agents
  canSpawn() {
    return this.active.size < MAX_AGENTS;
  }
  
  // Get current status
  status() {
    return {
      active: this.active.size,
      max: MAX_AGENTS,
      canSpawn: this.canSpawn(),
      agents: Array.from(this.active.values()).map(a => ({ id: a.id, task: a.task?.slice(0, 50) }))
    };
  }
  
  // Add agent
  add(id, task) {
    this.active.set(id, { id, task, started: Date.now() });
  }
  
  // Mark complete
  complete(id, result) {
    this.active.delete(id);
    this.completed.push({ id, result, time: Date.now() });
  }
  
  // Mark failed
  fail(id, error) {
    this.active.delete(id);
    this.failed.push({ id, error, time: Date.now() });
  }
  
  // Generate briefing template
  static briefing(task, context, expected) {
    return `
## Task: ${task}

## Context:
${context}

## Expected:
${expected}

## Guidelines:
- Max ${MAX_AGENTS} agents at once
- Report completion immediately
- Keep updates brief
`;
  }
}

module.exports = { AgentManager, MAX_AGENTS };
