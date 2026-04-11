# 🤖 EMPIREHAZECLAW - AGENT SYSTEM v10.0
*Last updated: 2026-04-05*

---

## ⚡ NEU in v10.0

| Feature | Beschreibung |
|---------|--------------|
| **Capability Evolver** | Self-Evolution Engine (authorized) |
| **Telegram Parser** | Chat History Import (35 Files, 9k+ Messages) |
| **Batch Exec** | Command Batching für Efficiency |
| **Knowledge Brain** | Unified Zettelkasten in memory/ |

---

## 🏢 SYSTEM ARCHITEKTUR

### Core Layer
```
┌─────────────────────────────────────────────────────────────┐
│                    CLAWMASTER (ICH)                          │
│  Telegram Channel → OpenClaw Gateway → Memory Brain         │
│  Primary: minimax/MiniMax-M2.7                       │
│  Fallback: GPT-4o-mini (OpenAI) → Nemotron 120B (Free) → Qwen3 Coder (Free) │
└─────────────────────────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
   ┌──────────┐       ┌──────────┐       ┌──────────┐
   │  Dev     │       │ Content  │       │ Revenue  │
   │ Scripts │       │ Blog/SEO │       │ Outreach │
   └──────────┘       └──────────┘       └──────────┘
```

---

## 🤖 SKILLS (9 Active)

| # | Skill | Pfad | Status |
|---|-------|------|--------|
| 1 | 🧬 Capability Evolver | `skills/capability-evolver/` | ✅ Active |
| 2 | 💻 Backend API | `skills/backend-api/` | ✅ |
| 3 | 🎨 Frontend | `skills/frontend/` | ✅ |
| 4 | 💻 Coding | `skills/coding/` | ✅ |
| 5 | ✍️ Content Creator | `skills/content-creator/` | ✅ |
| 6 | 📧 Email Outreach | `skills/email-outreach/` | ✅ |
| 7 | 🎯 Lead Intelligence | `skills/lead-intelligence/` | ✅ |
| 8 | 🎬 Video Renderer | `skills/video-renderer/` | ✅ |

---

## ⚡ AUTO-DELEGATION RULES

**Bei jeder User-Anfrage SOFORT prüfen:**

| Task Type | → Delegieren an | Beispiel |
|-----------|----------------|----------|
| `code/script/fix` | **dev** | "schreib mir ein script" |
| `research/analyse` | **research** | "recherchiere market" |
| `blog/content` | **content** | "schreib einen post" |
| `social/tiktok` | **social** | "poste auf twitter" |
| `sales/outreach` | **revenue** | "kontaktiere leads" |
| `website/frontend` | **frontend** | "mach die website" |

**NIE delegieren:** Hi, Danke, OK, STOP, Memory/Remember

---

## 🧠 MEMORY BRAIN (ZETTELKASTEN)

### Struktur
```
memory/
├── notes/                     # Atomic Notes
│   ├── ideas/                 # Neue Ideen
│   ├── concepts/              # Konzepte/Know-How
│   ├── insights/              # Erkenntnisse
│   ├── learnings/             # Lessons
│   └── permanent/             # Wichtige Notes
├── learnings/                 # Lessons Learned
├── decisions/                 # Entscheidungen
├── tags/                      # Tag Index
├── backlinks/                 # Backlink Graph
└── scripts/                   # Brain Tools
    ├── quick_capture.py       # Note erstellen
    ├── suggest_links.py      # Verbindungen finden
    ├── daily_review.py       # 5-min daily Review
    └── weekly_review.py      # Weekly Review
```

### Workflow
```
Capture → Suggest Links → Link → Review (daily/weekly)
```

---

## 📅 CRON JOBS (AUTOMATION)

| Zeit | Script | Zweck |
|------|--------|-------|
| */5 min | watchdog.sh | Dead Man's Switch |
| */15 min | autonomous_loop.py | Health Checks |
| 03:00 | night_shift.py | Backups, Heavy Ops |
| 08:00 | daily_report.py | Business Metrics |
| 09:00 | daily_outreach.py | Email Kampagne |
| 10:00 | morning_routine.py | News, Weather |
| 23:00 | autosync_v2.js | Memory Sync |
| 23:00 | batch_exec.py | Batch Commands |

---

## 🔐 SECURITY (Hardened 05.04.2026)

| Area | Status |
|------|--------|
| Firewall (UFW) | ✅ ON (deny-by-default) |
| Fail2ban | ✅ ON (sshd jail) |
| SSH Root Login | ✅ DEAKTIVIERT |
| Llama 70B | ✅ ENTFERNT |
| Capability Evolver | ✅ Authorized |

---

## 📊 PIPELINE STATUS

| Metric | Value |
|--------|-------|
| Leads CRM | 4,088 |
| Emails Gesendet | 73 |
| Responses | 0 |
| Customers | 0 |
| Revenue | €0 |

---

## 🔗 IMPORTANT LINKS

| Resource | URL |
|----------|-----|
| Shop | https://empirehazeclaw.store |
| Blog | https://empirehazeclaw.info |
| Dashboard | http://localhost:18789 |
| Gateway | ws://127.0.0.1:18789 |

---

## 🛠️ CRITICAL SCRIPTS

| Script | Nutzung |
|--------|---------|
| `check_delegate.py` | Auto-Delegation |
| `autosync_v2.js` | Memory Sync |
| `telegram_parser.py` | Chat Import |
| `batch_exec.py` | Command Batching |
| `response_tracker.py` | Email Tracking |

---

*v10.0 - Hardened & Unified*
