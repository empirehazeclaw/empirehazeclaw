# SYSTEM_BLUEPRINT.md — EmpireHazeClaw Complete Architecture

*Erstellt: 2026-03-28 | Version: 1.0 | Status: LIVE*

---

## 1. ARCHITEKTUR-HIERARCHIE (TOP-DOWN)

```
╔══════════════════════════════════════════════════════════════════════════╗
║                         EMPIREHAZECLAW                                    ║
║                    Complete System Architecture                             ║
╚══════════════════════════════════════════════════════════════════════════╝

                              ┌─────────────────┐
                              │   TELEGRAM      │  ← User Input (Nico)
                              │   (Direct)      │
                              └────────┬────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
           ┌────────────────┐ ┌──────────────┐ ┌─────────────────┐
           │  OPENCLAW       │ │   AUTONOMOUS │ │   CRON         │
           │  MAIN AGENT     │ │   LOOP       │ │   SCHEDULER    │
           │  (Gateway)      │ │  (15min)     │ │  (7 Jobs)      │
           └────────┬────────┘ └──────┬───────┘ └────────┬────────┘
                    │                   │                   │
                    │         ┌───────┴───────┐          │
                    │         ▼               ▼          │
                    │   ┌──────────┐   ┌──────────┐    │
                    │   │ WATCHDOG  │   │  SELF    │    │
                    │   │ (5min)   │   │  HEALING │    │
                    │   └──────────┘   └──────────┘    │
                    │         │               │         │
                    │         └───────┬───────┘         │
                    │                 │                 │
                    ▼                 ▼                 ▼
           ┌─────────────────────────────────────────────────────┐
           │                   LAYER 1: VERTICAL AGENTS          │
           │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
           │  │ REVENUE │ │ CONTENT │ │ RESEARCH│ │ SUPPORT │  │
           │  │ (Sales) │ │(Marketing)│ (Data) │ │ (Ops)  │  │
           │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │
           │       │            │            │           │       │
           │       ▼            ▼            ▼           ▼       │
           │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐    │
           │  │ Email  │  │ Blog   │  │ Tavily │  │ Stripe │    │
           │  │Outreach│  │ Agent  │  │ Search │  │Webhook │    │
           │  └────────┘  └────────┘  └────────┘  └────────┘    │
           └─────────────────────────────────────────────────────────┘
                                       │
                                       ▼
           ┌─────────────────────────────────────────────────────────┐
           │                   LAYER 2: WORKERS (Scripts)          │
           │                                                         │
           │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
           │  │ gmail_   │  │ stripe_   │  │ lead_    │          │
           │  │ api.py   │  │ webhook.py│  │ scraper.py│          │
           │  └──────────┘  └──────────┘  └──────────┘          │
           │                                                         │
           │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
           │  │ file_    │  │ cron_    │  │ notify_  │          │
           │  │ lock.py  │  │ scheduler │  │ script   │          │
           │  └──────────┘  └──────────┘  └──────────┘          │
           └─────────────────────────────────────────────────────────┘
                                       │
                                       ▼
           ┌─────────────────────────────────────────────────────────┐
           │                   LAYER 3: DATA (Storage)               │
           │                                                         │
           │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
           │  │SYSTEM_   │  │ crm_     │  │ logs/    │              │
           │  │CORE.md   │  │ leads.csv│  │ *.log    │              │
           │  └──────────┘  └──────────┘  └──────────┘              │
           └─────────────────────────────────────────────────────────┘
```

---

## 2. AGENT CLUSTER (157 Total)

### 💰 LAYER 1: REVENUE CLUSTER (15 Agents)
| Agent | Status | Funktion |
|-------|--------|----------|
| revenue_agent.py | ✅ | Master Sales Agent |
| cold_outreach_agent.py | ✅ | Email Kampagnen |
| lead_gen_agent.py | ✅ | Lead Mining |
| lead_intelligence_agent.py | ✅ | Lead Scoring |
| lead_qualifier_agent.py | ✅ | Lead Qualification |
| sales_executor_agent.py | ✅ | Sales Execution |
| sales_assistant_agent.py | ⚠️ | Sales Support |
| revenue_analyst_agent.py | ⚠️ | Revenue Analytics |
| customer_acquisition_agent.py | ✅ | Customer acquisition |
| conversion_agent.py | ✅ | Conversion optimization |
| pricing_agent.py | ✅ | Pricing strategy |

### 📝 LAYER 1: CONTENT CLUSTER (12 Agents)
| Agent | Status | Funktion |
|-------|--------|----------|
| content_agent.py | ✅ | Master Content Agent |
| content_production_agent.py | ✅ | Content Creation |
| blog_writer_agent.py | ✅ | Blog Posts |
| copywriter_agent.py | ✅ | Copywriting |
| social_media_agent.py | ✅ | Social Management |
| seo_writer_agent.py | ✅ | SEO Content |

### 🔬 LAYER 1: RESEARCH CLUSTER (8 Agents)
| Agent | Status | Funktion |
|-------|--------|----------|
| research_agent.py | ✅ | Master Research |
| market_research_agent.py | ✅ | Market Analysis |
| competitor_analysis_agent.py | ✅ | Competitor Research |
| trend_scout_agent.py | ✅ | Trend Discovery |

### 🏗️ LAYER 1: OPERATIONS CLUSTER (10 Agents)
| Agent | Status | Funktion |
|-------|--------|----------|
| operations_agent.py | ✅ | Master Operations |
| server_ops_agent.py | ✅ | Server Management |
| security_agent.py | ✅ | Security Monitoring |
| deployment_agent.py | ✅ | Deployment Automation |
| monitoring_agent.py | ✅ | System Monitoring |

### 🎨 LAYER 1: POD CLUSTER (6 Agents)
| Agent | Status | Funktion |
|-------|--------|----------|
| pod_agent.py | ✅ | Print-on-Demand Master |
| printify_uploader.py | ✅ | Printify Integration |
| etsy_agent.py | ✅ | Etsy Publishing |

### 📊 LAYER 1: TRADING CLUSTER (5 Agents)
| Agent | Status | Funktion |
|-------|--------|----------|
| trading_bot_agent.py | ⚠️ | Trading Master (braucht API Keys) |
| ai_trading_bot_v2.py | ⚠️ | AI Trading (braucht ccxt) |
| trading_scanner.py | ⚠️ | Signal Scanner |

### 🔧 LAYER 1: SUPPORT CLUSTER (4 Agents)
| Agent | Status | Funktion |
|-------|--------|----------|
| customer_support_agent.py | ✅ | Support Master |
| helpdesk_agent.py | ✅ | Helpdesk |
| onboarding_agent.py | ✅ | Customer Onboarding |

---

## 3. CRON JOBS & ABHÄNGIGKEITEN

```
┌──────────────────────────────────────────────────────────────────────┐
│                    CRON TIMELINE (24h)                              │
└──────────────────────────────────────────────────────────────────────┘

00:00 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       │                                                                  │
05:00  │  ┌─────────────────┐                                               │
       │  │ nightly_tests   │  ← Test critical paths                        │
       │  └────────┬────────┘                                               │
       │           │                                                        │
03:00  │  ┌────────┴────────┐                                               │
       │  │  night_shift.py  │  ← Heavy ops: git push, blog gen            │
       │  └────────┬────────┘                                               │
       │           │                                                        │
08:00  │  ┌────────┴────────┐                                               │
       │  │ daily_report.py  │  ← Business metrics                           │
       │  └────────┬────────┘                                               │
       │           │                                                        │
09:00  │  ┌────────┴────────┐                                               │
       │  │ daily_outreach  │  ← Email Kampagne Step 1/2/3                │
       │  └────────┬────────┘                                               │
       │           │                                                        │
10:00  │  ┌────────┴────────┐                                               │
       │  │ morning_routine  │  ← Weather, News, Readiness                  │
       │  └────────┬────────┘                                               │
       │           │                                                        │
       │  ┌────────┴────────┐                                               │
10:30  │  │ Social Content  │  ← Buffer/TikTok Posting                     │
       │  └────────┬────────┘                                               │
       │           │                                                        │
*/5    │  ┌────────┴────────┐                                               │
       │  │  watchdog.sh    │  ← Dead Man's Switch                         │
       │  └────────┬────────┘                                               │
       │           │                                                        │
*/15   │  ┌────────┴────────┐                                               │
       │  │autonomous_loop.py│  ← Health checks                             │
       │  └─────────────────┘                                               │
       │                                                                     │
20:00  │  ┌─────────────────┐                                               │
       │  │evening_summary  │  ← Daily close                               │
       │  └─────────────────┘                                               │

CRON DEPENDENCY GRAPH:
─────────────────────
watchdog.sh (5min)
    └─→ autonomous_loop.py (15min)
            └─→ self_healing.py
                    └─→ restart services if DOWN

night_shift.py (3h)
    └─→ git push
    └─→ blog generation

daily_outreach.py (9h)
    └─→ email_sequence.py
            └─→ gmail_api.py
                    └─→ crm_leads.csv

daily_report.py (8h)
    └─→ SYSTEM_CORE.md update
    └─→ REVENUE.md update
```

---

## 4. DATENFLUSS-AUDIT

```
╔══════════════════════════════════════════════════════════════════════════╗
║                         DATA JOURNEY MAP                                   ║
╚══════════════════════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────────────────────────────────────┐
  │ INPUT SOURCES                                                        │
  └─────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │  Tavily    │    │  Stripe     │    │  Manual     │    │  Websites   │
  │  (Research)│    │  (Payment)  │    │  (Telegram) │    │  (Scraping) │
  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
         │                   │                   │                   │
         ▼                   ▼                   ▼                   ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ PROCESSING LAYER                                                        │
  └─────────────────────────────────────────────────────────────────────┘

         │                   │                   │                   │
         ▼                   ▼                   │                   │
  ┌─────────────┐    ┌─────────────┐            │                   │
  │ research_   │    │ stripe_     │            │                   │
  │ agent.py    │    │ webhook.py  │            │                   │
  └──────┬──────┘    └──────┬──────┘            │                   │
         │                   │                   │                   │
         ▼                   ▼                   ▼                   ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                          STORAGE                                      │
  └─────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │ SYSTEM_     │    │ data/       │    │ data/       │    │ memory/     │
  │ CORE.md     │    │ customers.json│   │ crm_leads.csv│  │ YYYY-MM-DD  │
  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └─────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ OUTPUT LAYER                                                        │
  └─────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │  Emails     │    │  Stripe     │    │  Alerts     │    │  Logs       │
  │  (Outreach) │    │  (Sales)   │    │  (Telegram) │    │  (Audit)    │
  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 5. SICHERHEITS- & STABILITÄTS-MATRIX

### 🔒 FILE LOCKING (file_lock.py)

| File | Geschützt | Lock-Typ |
|------|-----------|-----------|
| SYSTEM_CORE.md | ✅ | fcntl.EX |
| REVENUE.md | ✅ | fcntl.EX |
| data/crm_leads.csv | ✅ | fcntl.EX |
| data/customers.json | ✅ | fcntl.EX |
| data/sent_emails.json | ✅ | fcntl.EX |
| logs/*.log | ✅ | fcntl.SH (append) |
| MEMORY.md | ⚠️ | Nicht aktiv (geplant) |

### 🔧 SELF-HEALING MATRIX

| Subsystem | Healer | Trigger | Action |
|-----------|--------|---------|--------|
| event_listener.js | self_healing.py | Process DOWN | Restart via subprocess |
| autonomous_loop.py | watchdog.sh | PID not found | Restart |
| Stripe Webhook | autonomous_loop.py | Port 5005 not listening | Restart via subprocess |
| Email Queue | email_sequence.py | GOG failure | Write to failed_queue.json |

### 🔐 SECRETS MANAGEMENT

| Secret | Location | Access | Permissions |
|--------|----------|--------|-------------|
| GOG OAuth Token | ~/.config/gogcli/token.env | Read: gmail_api.py | 600 ✅ |
| Stripe Secret | .env (nicht in workspace) | Read: stripe_webhook.py | Nur env |
| API Keys | .credentials/ | Read: via .env | 600 |
| Gmail App Password | Environment | Read: email_smtp.py | env only |

---

## 6. BLIND SPOTS & ORPHANED COMPONENTS

### ⚠️ ORPHANED COMPONENTS (keine Verbindung zu anderen)

| Component | Problem | Risk |
|-----------|---------|------|
| event_listener.js | Wird nie aufgerufen | Niedrig |
| parallel_executor.py | Nie in Crontab | Niedrig |
| smart_delegate.py | Ruft nicht-existierende Scripts auf | Mittel |
| central_logging.py | Server nie gestartet | Niedrig |
| delegator_daemon.py | Nie als Service gestartet | Mittel |

### 🚨 SCALABILITY ISSUES (bei 100 parallelen Nutzern)

| Bottleneck | Problem | Impact |
|------------|---------|--------|
| File Locking auf CRM | Bei 100 Nutzern = Massiver Contention | Hoch |
| Git Push im night_shift | Sequential, blockiert alles | Mittel |
| Email Queue | Kein echtes Queue-System (nur JSON) | Hoch |
| Tavily API | Rate Limit 1000/month | Hoch |
| GOG OAuth | Token refresh nicht automatisch | Mittel |

---

## 7. CRITICAL PATH FOR FIRST REVENUE

```
LEAD GENERATION
  research_agent.py → crm_leads.csv
         │
         ▼
OUTREACH
  email_sequence.py → gmail_api.py → GOG OAuth → SMTP → Empfänger
         │
         ▼
CONVERSION
  Stripe Checkout (Kunde zahlt)
         │
         ▼
WEBHOOK
  stripe_webhook.py → customers.json → onboarding_queue.json
         │
         ▼
ONBOARDING
  onboarding_agent.py → Willkommens-Email
```

---

## 8. QUICK REFERENCE COMMANDS

```bash
# System Status
python3 autonomous/watchdog_agent.py --status
python3 autonomous_loop.py --quick

# Email Kampagne
python3 email_sequence.py --status
python3 email_sequence.py --campaign --step 1 --count 10

# CRM
cat data/crm_leads.csv | head -10

# Logs
tail -50 logs/outreach.log
tail -50 logs/autonomous_loop.log

# Git Backup
cd /home/clawbot/.openclaw/workspace
git add -A && git commit -m "Auto-backup $(date)"

# Token Refresh
python3 gog_refresh_token.py
```

---

## 9. FILE PERMISSIONS (SECURE)

```bash
# Critical files (600)
chmod 600 ~/.config/gogcli/token.env
chmod 600 ~/.config/gogcli/credentials.json
chmod 600 ~/.config/gogcli/client_secret.json

# Workspace (644 for read, 600 for sensitive)
chmod 644 *.md
chmod 600 .credentials/*.json
```

---

## 10. EMERGENCY PROCEDURES

### Red Button
```bash
# 1. ALLES STOPPEN
touch /home/clawbot/.openclaw/workspace/.EMERGENCY_STOP

# 2. Git Reset
git -C /home/clawbot/.openclaw/workspace reset --hard HEAD~1

# 3. Credentials widerrufen
# Stripe Dashboard → Rotate Key
# Google Cloud → OAuth → Revoke Token
```

### Recovery
```bash
# From last known good commit
git -C /home/clawbot/.openclaw/workspace log --oneline -5
git -C /home/clawbot/.openclaw/workspace reset --hard <commit-hash>
```

---

*Letzte Aktualisierung: 2026-03-28 15:50 UTC*
