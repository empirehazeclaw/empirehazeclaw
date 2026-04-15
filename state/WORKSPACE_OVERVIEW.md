# OpenClaw Workspace Overview — Nico's Setup
**Generated:** 2026-04-15 20:13 UTC  
**Agent:** CEO (minimax/MiniMax-M2.7)  
**Host:** srv1432586 · Linux 6.8.0-106-generic · Node.js v22.22.2

---

## 🧭 Architecture

```
/home/clawbot/.openclaw/
├── workspace/          ← Main working directory (CEO lives here)
├── agents/ceo/         ← CEO agent config, memory, sessions
├── extensions/         ← Plugin system
└── node_modules/       ← Core dependencies
```

**Gateway:** `ws://127.0.0.1:18789` — local systemd service, always running  
**Channel:** Telegram (user 5392634979 — Nico)  
**Sessions:** 789 logged | Model: MiniMax-M2.7 | Context: ~205k tokens

---

## 📁 Directory Map

### Core Agent Spaces
| Path | Purpose |
|------|---------|
| `ceo/` | **Active agent workspace** — SOUL.md, memory, skills, docs, AGENTS.md |
| `ceo_backup_2026-04-13_1953/` | Dated backup snapshot before recent changes |
| `autonomous/` | Sub-agents: daily routine, watchdog, master orchestrator, sandbox |
| `agent_runner/` | Python-based agent execution engine |

### Knowledge & Memory
| Path | Purpose |
|------|---------|
| `memory/` | Long-term memory storage, session analysis, habit tracking, vault |
| `learnings/` | Accumulated insights and lessons |
| `data/reflections/` | Self-reflection logs |
| `data/learning_loop/` | Learning coordinator + loop state |
| `data/evolvers/` | Autonomous capability evolvers |
| `data/improvements/` | Applied improvements log |
| `state/` | System-state snapshots |

### Skills System
| Path | Purpose |
|------|---------|
| `skills/` | 20+ active skills: bug-hunter, code-review, self-improvement, guardrails, ... |
| `skills/_library/` | Skill library index and metadata |
| `auto_skill_creator/` | Automatic skill creation system |

### Coding & Dev
| Path | Purpose |
|------|---------|
| `coding/` | OpenCL deep inspector (C/C++/Python) |
| `api/` | Stripe webhook integrations, Express API |
| `api_gateway/` | Python gateway server |
| `dashboard/` | JSON + Python API servers for monitoring |
| `saas-pipeline/` | Full SaaS automation pipeline (automate/validate/research/run) |
| `core_ultralight/` | Lightweight core system with manifest + requirements |

### Automation & Scripts
| Path | Purpose |
|------|---------|
| `automation/` | auto_mode, auto_optimizer, auto_repair, daily_report, social_poster |
| `scripts/` | 30+ Python/bash scripts: cron_watchdog, error_reducer, backup_manager... |
| `cron_manager.js` | Central cron orchestration |
| `workflows/` | AI research pipeline, social-media automation, product launch docs |
| `pipeline/` | blog, content, social generators + humanizer |
| `hooks/` | pre-commit git hooks |

### Content & Marketing
| Path | Purpose |
|------|---------|
| `content-queue/` | Weekly plans, social posts, gastro content |
| `ready-to-post/` | Pre-built outreach, sales FAQ, pitch deck, video ideas, Twitter/LinkedIn posts |
| `prompts/` | Master prompt library, business prompts |
| `queue/twitter_queue.md` | Queued tweets |
| `reference/` | Trend research PDFs, Deutschland politik 2026 |
| `tech/` | AI video/image generator research, recommended tools |

### Business & Revenue
| Path | Purpose |
|------|---------|
| `revenue/` | business-model.md, pricing-strategy.md |
| `product-kits/` | generic + restaurant product kit templates |
| `clawmart-submission/` | ClawMart skill submission package |

### Monitoring & Ops
| Path | Purpose |
|------|---------|
| `monitoring/` | api_monitor, health_monitor, performance_monitor, auto_repair |
| `system/` | VPS knowledge base, self-healing, autonomous recovery, idle trigger |
| `logs/` | 20+ log files: heartbeat, cron_watchdog, error_reduction, security... |
| `backup/` | Backup rotation, security audit/monitor, session cleanup |
| `backups/` | Archived tar.gz backups of OpenClaw state |
| `rollback/` | Workspace rollback bundles |

### Docs & Analysis
| Path | Purpose |
|------|---------|
| `docs/` | AGENT_SELF_IMPROVER_PLAN, AUTONOMOUS_LEARNING_PLAN, MEMORY_ARCHITECTURE, KG_ANALYSIS... |
| `analysis/` | auto_cost_tracker, trend_hunter, trend_intel, trend_research |
| `data/cache/` | Cached data |
| `logs/bug_hunter/` | Bug hunting logs |
| `logs/improvements/` | Improvement tracking |

### Assets & Media
| Path | Purpose |
|------|---------|
| `assets/gep/` | GEP assets |
| `TEMPORARY/audio/` | Temp audio files |
| `TEMPORARY/logs/` | Temporary logs |
| `remotion-video/` | Remotion video generation project |

### Utilities
| Path | Purpose |
|------|---------|
| `lib/` | Shared Python libraries: agent_factory, alerts, caching, cron_scheduler, database, email_smtp, logger, monitoring... |
| `utils/` | env_helper |
| `templates/` | Business prompts, customer case, meeting notes, invoice, product spec |

---

## 🔴 Security Audit Flags

```
CRITICAL: Discord guilds: open policy with no allowlist — mention-gated trigger only
WARN: Reverse proxy headers not trusted (gateway.bind is loopback)
WARN: gateway.nodes.denyCommands uses exact matching only (not shell-text filtering)
WARN: Unpinned npm plugin install: voice-call (@openclaw/voice-call)
```

---

## 📊 Disk Usage
| Mount | Size | Used | Available | Use% |
|-------|------|------|-----------|------|
| `/` (sda1) | 96G | 28G | 69G | 29% |
| `/run` (tmpfs) | 795M | 1.1M | 794M | 1% |
| `/dev/shm` (tmpfs) | 3.9G | 0 | 3.9G | 0% |

---

## 🚀 Active Capabilities

- **Sub-agents:** daily routine, watchdog, master orchestrator, event listener
- **Cron jobs:** Morning routine, nightly bundle, health checks, social poster
- **Self-healing:** auto_repair, cron_error_healer, watchdog_agent
- **Self-improvement:** agent_self_improver, capability_evolver, loop_prevention
- **Skills:** 20+ active skills with self-improvement loop built in
- **Memory:** Vector search ready, 37 files, 304 chunks, semantic + FTS
- **Backup:** Auto-backup with rotation, rollback system

---

*Document generated by CEO agent on 2026-04-15 — saved to `state/WORKSPACE_OVERVIEW.md`*
