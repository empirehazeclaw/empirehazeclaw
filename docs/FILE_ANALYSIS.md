# File Analysis - Archive Decision Guide

**Erstellt:** 2026-04-11 11:17 UTC

---

## 📋 CATEGORIES

### 🔴 KEEP (Critical - Do NOT move)
```
HEARTBEAT.md        - System Status (wird von OpenClaw gelesen!)
IDENTITY.md          - Identity (wird von OpenClaw gelesen!)
SOUL.md              - Soul (wird von OpenClaw gelesen!)
USER.md              - User Info (wird von OpenClaw gelesen!)
TOOLS.md             - Tools Config (wird von OpenClaw gelesen!)
MEMORY.md            - Memory Context (wird von OpenClaw gelesen!)
AGENTS.md            - Agents Overview
DELIVERY_RULES.md    - Delivery Config
SYSTEM_ARCHITECTURE.md - NEW System Doc
SYSTEM_INVENTORY.md  - NEW Inventory
```

### 🟡 KEEP (Important but can archive location)
```
README.md            - Root README (useful but can be in docs/)
```

### 🟡 REVIEW BEFORE ARCHIVING (Important info inside)
```
AGENTS.md            - Has agent system info
SYSTEM_BLUEPRINT.md  - System architecture (BUT supersceded by SYSTEM_ARCHITECTURE.md)
```

### ⚠️ SAFE TO ARCHIVE (Old planning/reports - info captured elsewhere)

#### Old Agent Planning (2026-03-28):
```
AGENT_CONSOLIDATION_PLAN.md   - Old consolidation plan
AGENT_INVENTORY.md           - Old inventory (157 agents)
AGENT_ROI_AUDIT.md           - Old ROI audit
KILL_LIST_CRITERIA.md        - Old planning
```

#### Old Test/Audit Reports:
```
BACKUP_STATUS.md             - Old backup report (2026-04-05)
CHAOS_TEST.md                - Old chaos test (2026-03-28)
FUNCTIONAL_TEST.md           - Old functional test (2026-03-28)
MODEL_TEST_RESULTS.md        - Old model test (2026-04-05)
KNOWLEDGE_OVERVIEW.md        - Old knowledge system (2026-03-28)
SECURITY_AUDIT_MEMORY.md     - Old audit (2026-04-05)
SECURITY_HARDENING_STATUS.md - Old security (2026-04-05)
SECURITY_KNOWLEDGE.md        - Old security (2026-03-21)
SYSTEM_AUDIT_2026-04-09.md   - Old audit
SYSTEM_BLUEPRINT.md          - Old architecture (superseded)
SYSTEM_COMPLETE.md           - Old complete system (2026-03-14)
SYSTEM_CORE.md               - Old core doc (2026-03-28)
```

#### Old Vision/Planning:
```
VISION.md              - Old vision (2026-03)
FINAL_STATE.md        - Unclear purpose, OLD
DREAMS.md            - Old fleet vision
INDEX.md             - Duplicate of README
```

#### Old Setup/Integration:
```
SETUP_EMAIL.md       - Old email setup
STORE_INTEGRATION.md - Old store plan (2026-03-28)
REVENUE.md          - Old revenue focus (2026-03-28)
```

#### Old Marketing (2026-03-22):
```
blog_2026-03-22.md
launch-posts.md
linkedin-optimization.md
llm-models.md
reddit_2026-03-22.md
reddit_managed_ai_posts.md
reddit_prompt_cache_posts.md
social_2026-03-22_0.md
social_2026-03-22_1.md
social_2026-03-22_2.md
```

#### Old Campaign/Product:
```
automated_sales_funnel.md
brand.md
bug_report_voice_messages.md
customer-journey.md
features-comparison.md
metrics.md
one-pager.md
outreach-list.md
processes.md
product-catalog.md
quickstart.md
video_production_kit.md
werbevideo_script.md
gcp-oauth-schritt-fuer-schritt.md
gog-oauth-einrichten.md
gog-setup.md
oauth-client-id-schritt.md
wordpress-multisite-guide.md
managed_hosting_watchdog.md
notion-templates-roadmap.md
schmiede-suche.md
server-config.md
security_concept.md
team_capacity_check.md
tasks_until_1500.md
```

#### Duplicate/Obscure:
```
AGENTS_LLM_README.md  - Duplicate info
```

---

## 📊 SUMMARY

| Category | Count | Action |
|----------|-------|--------|
| KEEP (Critical) | 11 | Don't touch |
| KEEP (Important) | 1 | Keep or move to docs |
| REVIEW | 1 | Review before archive |
| ARCHIVE (Old Planning) | 15 | Safe to archive |
| ARCHIVE (Old Marketing) | 24 | Safe to archive |
| ARCHIVE (Old Setup) | 10 | Safe to archive |
| **TOTAL** | **~50** | **Can be archived** |

---

## 🎯 RECOMMENDED ACTIONS

1. **Keep Critical** - Leave where they are (read by OpenClaw)
2. **Archive Old Planning** - Move to `archive/old_docs/planning/`
3. **Archive Old Marketing** - Move to `archive/old_docs/marketing/`
4. **Archive Old Setup** - Move to `archive/old_docs/setup/`
5. **Keep README** - Maybe move to docs/ or keep

**Result:** Root will go from ~80 .md files to ~15

---

*Analysis: 2026-04-11 11:17 UTC*
*Source: ls *.md + head analysis*