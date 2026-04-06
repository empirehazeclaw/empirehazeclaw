# 🏗️ BUILDER SKILL

## Overview
This skill guides the Builder Agent in creating and maintaining the EmpireHazeClaw agent fleet.

## Core Capabilities

### 1. Agent Creation
When creating a new agent:
1. Create workspace: `/home/clawbot/.openclaw/workspace/<agent-id>/`
2. Create SOUL.md with agent identity
3. Create AGENTS.md with responsibilities
4. Add to `agents.list[]` in openclaw.json
5. Create memory directories
6. Set up skills configuration
7. Restart gateway

### 2. Script Development
When building scripts:
1. Use Python or JavaScript (Node.js)
2. Add shebang for executables
3. Include error handling
4. Document with comments
5. Place in appropriate directory
6. Set executable permissions

### 3. System Health Checks
Performs:
- Gateway status
- Cron jobs status
- Disk space
- Memory usage
- Error logs review

### 4. File Organization
```
builder/
├── memory/
│   ├── notes/        # Daily notes, todos
│   ├── decisions/    # Architectural decisions
│   └── learnings/    # Lessons learned
├── skills/           # Skill definitions
└── work/            # Active projects
```

## Usage
Invoke when:
- Building new agents
- Creating automation scripts
- Performing health checks
- Debugging system issues
- Updating documentation

## Quality Standards
- All scripts must have error handling
- Document every decision in memory
- Report status after each major task
- Follow existing code patterns
