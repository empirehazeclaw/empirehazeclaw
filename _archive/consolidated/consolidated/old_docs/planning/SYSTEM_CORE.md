# SYSTEM_CORE.md — EmpireHazeClaw Single Source of Truth

*Erstellt: 2026-03-28 | Version: 2.0 | Letztes Update: 2026-03-28 15:50*

**Vollständige Dokumentation:** `SYSTEM_BLUEPRINT.md` (Agent-Hierarchie, Cron-Abhängigkeiten, Data Flows)

---

## 🏰 SYSTEM ARCHITECTURE (auf einen Blick)

```
                        TELEGRAM (Nico)
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         OPENCLAW        AUTONOMOUS      CRON
         GATEWAY          LOOP          JOBS
              │              │              │
              │     ┌───────┴───────┐      │
              │     │  WATCHDOG     │      │
              │     │  (5min)       │      │
              │     └───────┬───────┘      │
              │             │              │
              └──────────────┼──────────────┘
                             │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────┴────┐      ┌─────┴────┐      ┌─────┴────┐
    │ REVENUE │      │ CONTENT  │      │ RESEARCH  │
    │ (Email) │      │ (Blog)   │      │ (Tavily) │
    └────┬────┘      └─────┬────┘      └─────┬────┘
         │                  │                  │
         ▼                  ▼                  ▼
    ┌─────────┐      ┌──────────┐      ┌──────────┐
    │ gmail_  │      │ blog_    │      │ tavily_  │
    │ api.py  │      │ agent.py │      │ search   │
    └────┬────┘      └──────────┘      └──────────┘
         │
         ▼
    OUTBOX (SMTP/Gmail)
```

---

## 🚩 PRIORITY FLAGS

| Flag | Bedeutung | Wann |
|------|-----------|------|
| 🔴 P1 | MUST CHECK | Vor jeder Antwort |
| 🟡 P2 | CHECK | Bei Entscheidungen |
| 🟢 P3 | INFO | Allgemein |

---

## 👤 ÜBER NICO

- **Name:** Nico
- **Telegram:** 5392634979
- **Email:** empirehazeclaw@gmail.com
- **Background:** KFZ Mechatroniker → Ingenieur Werkstoffkunde
- **Sprache:** Deutsch

---

## 🏢 HAUPTPRODUKT: MANAGED AI HOSTING (B2B)

**Kernel-Konzept:** OpenClaw Agents auf VPS — KI-Mitarbeiter für lokale KMUs

**Zielgruppe:** Bäckereien, Restaurants, Arztpraxen, Handwerker — wenig tech-affin aber profitieren von KI

**Use Cases:** Email Support, Chatbot, Reservierungs-Automatisierung, Recherche

| Plan | Setup | Monatlich | Zielgruppe |
|------|-------|-----------|------------|
| Starter | €149 | €99 | Developer, Small Business |
| Professional | €299 | €199 | Agencies, Mittelstand |
| Enterprise | €499 | €499 | Large Companies |

**Differenzierung:** 🇩🇪 Deutsche Server | 🔒 DSGVO | 🤖 OpenClaw vorinstalliert | 💼 Managed Service

**Stripe Links:**
- Starter: https://buy.stripe.com/fZudR97VGgiIdsB3Dw9k40z
- Professional: https://buy.stripe.com/7sY4gz6RC6I8agp7TM9k40H
- Enterprise: https://buy.stripe.com/5kQeVddg08Qg9clgqi9k40O

---

## 🌐 DOMAINS & SERVICES (VERCEL BIG 4 STANDARD)

| Domain | Zweck | Status |
|--------|-------|--------|
| empirehazeclaw.de | DE Corporate (HAUPT) | ✅ Live |
| empirehazeclaw.com | EN Corporate (Global) | ✅ Live |
| empirehazeclaw.store | E-Commerce / Revenue | ✅ Live |
| empirehazeclaw.info | Blog / Dokumentation | ✅ Live |

### Vercel Projects (BIG 4 ONLY)
```
de              → https://empirehazeclaw.de
com             → https://com-ebon.vercel.app (→ empirehazeclaw.com)
store           → https://empirehazeclaw.store
info            → https://empirehazeclaw.info
```

### ⚠️ NEUE PROJEKTE REGEL
**Keine neuen Vercel-Projekte ohne explizite Erlaubnis!**
Alle neuen Features = Sub-Page oder Sub-Domain der Big 4.

### Services
| Service | Status |
|---------|--------|
| OpenClaw Gateway (18789) | ✅ Auf diesem Server |
| Websites (80/443) | ✅ Alle 4 live |
| Vercel CLI | ✅ Installiert + Token konfiguriert |

---

## 💰 AKTIVE APIS

| API | Key-Prefix | Status |
|-----|------------|--------|
| Stripe | sk_live_... | ✅ Working |
| Tavily | tvly-dev-... | ✅ Working |
| GOG CLI | ~/.config/gogcli/ | ✅ Email OK |
| Printify | - | ✅ Verbunden |
| fal.ai | - | ✅ Bild/Video |
| Leonardo.ai | - | ✅ Images |

---

## ⚡ P1 REGELN

1. **Vor Twitter posten → FRAGEN**
2. **MEMORY.md lesen** (diese Datei!)
3. **SYSTEM_CORE.md** für aktuellen Systemstatus

---

## 🤖 KEY SCRIPTS

| Script | Nutzung |
|--------|---------|
| `gog gmail send --to X --subject Y --body Z` | Email senden |
| `python3 scripts/local_closer_rebuild_v3.py <url>` | Landingpage analysieren |
| `python3 autonomous/watchdog_agent.py --status` | Health Check |

---

## 🎯 REVENUE FOCUS (Q1-Q2 2026)

1. Kunden gewinnen (laufend)
2. Newsletter aufbauen
3. Social Media (TikTok gestartet)
4. Outreach Kampagne (crawl4ai + email)

---

## 📅 AKTIVE CRON JOBS

| Zeit | Job | Zweck |
|------|-----|-------|
| `*/5` min | watchdog.sh | Dead Man's Switch |
| `*/15` min | autonomous_loop.py | Quick Checks |
| 03:00 | night_shift.py | Night Operations |
| 08:00 | daily_report.py | Business Report |
| 09:00 | daily_outreach.py | Lead Outreach |
| 10:00 | morning_routine.py | Morning Start |

---

## 🤖 AKTIVE AGENTS (Core + Business-Relevant)

| Agent | Kategorie | Status |
|-------|-----------|--------|
| revenue_agent | SALES | ✅ |
| operations_agent | OPS | ✅ |
| content_agent | CONTENT | ✅ |
| research_agent | RESEARCH | ✅ |
| pod_agent | POD | ✅ |
| trading_bot_agent | TRADING | ⚠️ API Keys nötig |
| social_media_agent | SOCIAL | ⚠️ Config nötig |
| growth_agent | GROWTH | ✅ |
| verification_agent | QA | ✅ |
| librarian_agent | KNOWLEDGE | ✅ |

---

---

## 🔐 API KEYS — MISSING / TO CONFIGURE

| Key | Status | Wo eintragen | Aktion |
|-----|--------|--------------|--------|
| `GOG_ACCESS_TOKEN` | ❌ FEHLT | Environment | `gog auth` ausführen |
| `ALERT_WEBHOOK_URL` | ❌ FEHLT | Environment | Telegram/Slack Webhook |
| `STRIPE_SECRET_KEY` | ✅ OK | `.env` | — |
| `TAVILY_API_KEY` | ✅ OK | `.env` | — |

### Gmail Setup (für Outreach):
```bash
# Gog CLI installieren und auth:
brew install gog  # Mac
# oder: curl -fsSL ... | sh

gog auth --account empirehazeclaw@gmail.com
gog gmail send --to test@example.com --subject "Test" --body "Hello"
```

### Alert Webhook (optional):
```bash
# Telegram Bot Webhook:
export ALERT_WEBHOOK_URL="https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<CHAT_ID>"
```

---

## 🚨 SYSTEM STATUS (2026-03-28)

### ✅ WORKING
- OpenClaw Gateway (18789)
- Website Monitoring (4/4 sites up)
- Autonomous Loop + Watchdog
- GOG CLI Email
- Memory System

### ⚠️ MISSING / INCOMPLETE
- Twitter API Keys → social_config.json leer
- Trading Bot API Keys → ccxt installiert, aber Keys fehlen
- Stripe Webhook Script → nicht installiert
- Reddit API Keys → nicht beantragt

### ❌ NOT CONFIGURED
- MissionControl (alter Server 187.124.11.27 — nie aufgesetzt)
- LeadGen, AIChatbot, TradingBot (gleicher alter Server)

---

## 🔴 BLOCKERS (Revenue)

1. **0 Kunden** — kein pago
2. **Kein funktionierendes Outreach** — crm_leads.csv ist leer
3. **TikTok/Social ohne API** — Twitter OAuth abgelaufen

---

## 💓 HEARTBEAT / LAST ACTIVITY

| Component | Letzte Aktivität |
|-----------|------------------|
| watchdog | Läuft (alle 5 min) |
| autonomous_loop | Aktiv (alle 15 min) |
| Gateway | ✅ Läuft |

---

## 📊 AGENT INVENTUR

| Kategorie | Anzahl |
|-----------|--------|
| Core Agents (business) | ~15 |
| Codex Subagents | ~146 |
| Total | ~161 |

**Letzte Bereinigung:** 2026-03-28 — 109 Agents archiviert, 6 Risk-Agents gelöscht

---

## 🧠 MEMORY PROTOKOLL

**Keine Redundanz!** Klare Hierarchie:

| Ebene | File | Inhalt |
|-------|------|--------|
| Single Source | **SYSTEM_CORE.md** | Dies hier — Status + Business |
| Curated | **MEMORY.md** | Full Context für Chats |
| Daily | **memory/YYYY-MM-DD.md** | Raw Logs (Auto-Delete 30 Tage) |
| RAG | **knowledge/** | Vektor-DB für Recherche |

---

*Nächster Update: Bei jeder wichtigen Änderung*
