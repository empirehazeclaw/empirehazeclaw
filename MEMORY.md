# MEMORY.md - EmpireHazeClaw Core Context

*Ultimative Source of Truth - wird in direkten Chats geladen*
*Zuletzt bereinigt: 2026-04-07*
*Archivierte History: memory/archive/2026-04-telegram-dumps.md*

---

## 👤 NICO (Founder)
- **Name:** Nico
- **Telegram:** 5392634979
- **Email:** empirehazeclaw@gmail.com
- **Sprache:** Deutsch
- **Background:** KFZ Mechatroniker → Ingenieur Werkstoffkunde

---

## 🏢 UNSER BUSINESS

### Hauptprodukt: MANAGED AI HOSTING
**KI-Mitarbeiter für deutsche KMUs (Bäckereien, Restaurants, Arztpraxen)**

| Plan | Setup | Monat |
|------|-------|-------|
| Starter | €149 | €99 |
| Professional | €299 | €199 |
| Enterprise | €499 | €499 |

**Differenzierung:** Deutsche Server, DSGVO, Managed Service, OpenClaw

### Domains (alle ✅ Live)
- empirehazeclaw.com (EN Corporate)
- empirehazeclaw.de (DE Corporate)
- empirehazeclaw.store (Shop)
- empirehazeclaw.info (Blog)

---

## 🎯 PRIORITÄTEN (Q2 2026)

1. **ERSTE KUNDEN GEWINNEN** - P1 (0 Kunden, €0 Revenue)
2. Outreach Kampagne - 73 Emails, 0 Responses
3. Social Media (TikTok)
4. Blog Content

---

## 📧 EMAIL SYSTEM
- **GOG CLI:** `gog gmail send --to X --subject Y --body Z`
- **Bounce Handler:** `scripts/outreach_bounce_handler.py`

---

## 🛠️ SYSTEM STATUS

| Component | Status | Info |
|-----------|--------|------|
| OpenClaw Gateway | ✅ 2026.4.5 | Port 18789 |
| Telegram | ✅ | Bot Token: 8397...oH9Y |
| MetaClaw | ✅ | Port 30000, skills_only mode |
| LCM Plugin | ✅ | threshold 0.75 |
| Stripe | ✅ | Auto-Fulfillment |
| MiniMax | ✅ | M2.7 Model |
| Node.js | ✅ | v22.22.2 |

### APIs (Stand 2026-04-07):
| API | Status | Key |
|-----|--------|-----|
| MiniMax | ✅ OK | secrets.env |
| OpenAI | ⚠️ Rate Limited | - |
| Stripe | ✅ OK | secrets.env |
| Brave Search | ✅ OK | secrets.env |
| OpenRouter | ✅ OK | secrets.env |
| Buffer | ❌ INVALID | Rotieren! |
| Leonardo AI | ❌ INVALID | Rotieren! |
| Gmail | ⚠️ Issue | App Password? |

---

## 🤖 AUTO-DELEGATION

| Task | Delegieren an |
|------|---------------|
| code/script/fix | builder |
| research/analyse | research |
| blog/content | content |
| social/tiktok | social |
| sales/outreach | revenue |
| website/frontend | frontend |

---

## 🔴 TOP PRIORITIES (Active)

1. **ERSTE KUNDEN GEWINNEN** - 0 Kunden ist Hauptproblem
2. **Outreach Response Rate verbessern** - Email Sequence überarbeiten
3. **Buffer + Leonardo Tokens erneuern**

### Offene Security Keys:
| Key | Status |
|-----|--------|
| Buffer Token | ❌ INVALID |
| Leonardo AI | ❌ INVALID |
| Telegram Bot | ⏳ Rotieren |
| Restic | ⏳ Rotieren |
| GitHub PAT | ✅ Erneuert |
| Google AIza | ⏳ Rotieren |
| SECRET_KEY | ⏳ Rotieren |

---

## ⚡ ARBEITSREGELN

1. **Vor Twitter posten → FRAGEN**
2. **memory_search** bei Fakten-Fragen
3. **"Geht nicht"** → "Schwierig wegen X, probiere Y"
4. **3 Versuche** bevor aufgeben
5. **Nico informieren** wenn wirklich nicht weiterkommt

---

## 📊 PIPELINE (Stand 2026-04-07)

| Metric | Value |
|--------|-------|
| Leads | 4,088 |
| Emails gesendet | 73 |
| Responses | 0 |
| Customers | 0 |
| Revenue | €0 |

---

## 🧠 KNOWLEDGE BRAIN

| Directory | Content |
|-----------|---------|
| memory/notes/ | Atomic Notes (fleeting/ideas/insights/concepts/permanent) |
| memory/decisions/ | Entscheidungen |
| memory/learnings/ | Lessons Learned |
| memory/archive/ | Archivierte History |
| workspace/knowledge/ | Knowledge Graph |

**Workflow:** Capture → Tag → Review (daily/weekly)

---

## 🏗️ SYSTEM ARCHITEKTUR

```
OpenClaw Gateway (:18789)
├── Telegram Channel
├── MetaClaw Proxy (:30000) → MiniMax M2.7
├── LCM Plugin (Compaction)
├── Memory System (SQLite + Files)
└── 6 Agents: CEO, Security, Data, Research, Builder, QC
```

---

## 📁 CRITICAL PATHS

| Path | Use |
|------|-----|
| /home/clawbot/.openclaw/workspace/ | Main workspace |
| /home/clawbot/.openclaw/secrets/ | API Keys (600 permissions) |
| /home/clawbot/.openclaw/memory/ | Memory Brain |
| /home/clawbot/MetaClaw/ | MetaClaw installation |
| /home/clawbot/.metaclaw/skills/ | MetaClaw Skills (36 geladen) |

---

## 🦞 Sir HazeClaw (CEO)

- Sovereign Orchestrator für alle Agents
- Routing: Security → Security Officer, Data → Data Manager, Code → Builder
- QC Officer validiert nach jedem Task
- Sovereign Cron Jobs: 10:00 Security, 11:00 Data, 12:00 Builder, 13:00 Research

---

*Letzte große Bereinigung: 2026-04-07 (438KB → ~20KB)*
