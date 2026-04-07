# LEGACY KNOWLEDGE BASE
*Extracted from old_agents/ and old_scripts/ archives — 2026-04-07*

---

## 📜 PROJEKT HISTORIE & MEILENSTEINE

### Gründung & Vision
- **Projektname:** EmpireHazeClaw — AI Agent Flotte
- **Boss:** Nico — steuert die Flotte via Telegram
- **Server:** srv1432586 (Hostinger VPS, Ubuntu-basiert)
- **Erste Versionen:** Tim → Clawbot User auf Server

### Meilensteine (aus Chat-Historie extrahiert)

| Datum | Meilenstein | Status |
|-------|-------------|--------|
| Feb 2026 | OpenClaw Installation auf VPS | ✅ |
| Feb 2026 | Gateway-Probleme (ECONNREFUSED, Config-Fehler) | 🔧 |
| Feb 2026 | Docker Installation + Container Setup | ✅ |
| Feb 2026 | Telegram Bot (@Dev_bot11bot) verbunden | ✅ |
| Feb 2026 | Ollama mit Llama 3.2:3b lokal | ✅ |
| Feb 2026 | Tailscale VPN aktiv | ✅ |
| Mrz 2026 | Multi-Agent System (Research, Content, Revenue) | ✅ |
| Mrz 2026 | WooCommerce Shop live | ✅ |
| Mrz 2026 | Stripe Payment Links funktionieren | ✅ |
| Mrz 2026 | Brevo Newsletter integriert | ✅ |
| Mrz 2026 | Trading Bot (+0.55% p.a., nicht profitabel) | 📝 |
| Mrz 2026 | Auto-Fulfillment (Stripe → Auslieferung) | ✅ |
| Mrz 2026 | B2B Outreach Kampagne (IT-Firmen) | ✅ |
| Mrz 2026 | Blog System vereinheitlicht | ✅ |
| Mrz 2026 | 6 Produkte auf Verkaufsstandard | ✅ |
| Apr 2026 | Workspace Architect — Aufräumen | ✅ |
| Apr 2026 | CEO-Flotten-Modell eingeführt | ✅ |

---

## 🧠 EINZIGARTIGE LOGIKEN (aus alten Agents extrahiert)

### 1. DAG Executor — Parallele Task-Ausführung
```python
# Unterstützt Abhängigkeiten + parallele Ausführung
# Auto-Retry bei Fehlern (max 2 retries)
# Async/Await-basierte Architektur
```
**Status:** Archiviert — aktuelle Flotte nutzt OpenClaw Subagent-System

### 2. Memory Agent — 5-Typen Gedächtnis
```
EPISODIC  = Task-Historie + Ergebnisse
SEMANTIC  = Fakten, Wissen, Dokumente
PROCEDURAL= Gelernte Muster & Best Practices
FEEDBACK  = Qualitätsbewertungen
ERROR     = Fehler-Patterns
```
**Besonderheit:** ChromaDB Vector Store + Sentence Transformers (lokal, kostenlos)

### 3. Workflow Engine — Vordefinierte Pipelines
```
content_pipeline: Research → Content → Distribution
sales_pipeline:   Find Leads → Outreach → Follow-up
code_review:      Research → Code → Deploy
security_audit:   CVE Scan → Fix → Verify
daily_routine:    Trends → Content → Social
```
**Status:** Archiviert — Builders Workflows als Alternative

### 4. Orchestrator — Keyword-basiertes Routing
- Analysiert Task → Detektiert Keywords → Wählt Agenten
- Complexity-Erkennung (simple vs multi-step)
- Auto-Workflow-Erstellung basierend auf Task-Typ
- Model-Routing (coding→Claude, content→Claude, security→Claude)

### 5. Mail Agent (Brevo) — Email-System
- Templates: Cold Outreach, Follow-up, Newsletter, Auto-Reply, Welcome, Sales
- Tone-Adaptation (Formal, Professional, Friendly, Assertive, Apologetic, Urgent)
- Brevo SMTP Integration

### 6. Coding Agent — Auto-Debugging
```python
MAX_DEBUG_ITERATIONS = 3
# Auto-Fixes für:
# - IndentationError
# - SyntaxError
# - ImportError / ModuleNotFoundError
# - NameError
# - TypeError
```
- Docker Sandbox Execution (wenn verfügbar)
- Multi-Language Support (Python, JS, Bash, SQL, Rust, Go)

### 7. Twitter Growth v2 — Auto-Engagement
```
TARGET_KEYWORDS = ["AI Agent", "SaaS Startup", "Tech Automation", "ChatGPT API", "Build in Public"]
DAILY_LIMIT = 5
# Nutzt xurl für Twitter API
# Safe engagement limits
```

### 8. Nightshift Extended — Cron-Loop Script
```bash
# Läuft 19:00 - 07:00
# Alle 30min: Leads, Follow-ups, Health Check
# Alle 2h: Revenue Agent
# Morning/Evening: Content Generation
# Alle 3h: Research
```

### 9. Agent Registry — Capability-basiertes Routing
- Dynamische Agent-Registrierung mit Keywords
- Fallback-Mechanismus
- Stats-Tracking (total_calls, successful, failed, duration)

### 10. Shopify Manager — E-Commerce Operations
- Product Management
- Order Tracking
- Inventory Management
- Logging + Error Handling

---

## 🛠 SPEZIAL-TOOLS (archivierte Scripts)

### old_scripts/
| Script | Funktion | Status |
|--------|----------|--------|
| `twitter_growth_v2.py` | Auto-Twitter Engagement via xurl | 🔒 Token benötigt |
| `nightshift_extended.sh` | Automated Night Shift Loop | ✅ Wiederverwendbar |
| `nightshift.sh` / `nightshift_v2.sh` | Ältere Versionen | 📝 Referenz |
| `local_closer.js` / `local_closer_v2.js` / `local_closer_full.py` | Sales/Lead Closer? | ❓ Unklar |
| `scrape_it_agencies.py` / `scrape_it_agencies2.py` / `scrape_it_agencies_fix.py` | IT-Agenturen scraper | ⚠️ Rechtlich prüfen |
| `auto-delegate-v2.py` | Auto-Task-Delegation | ✅ Referenz für CEO |
| `task_manager_v2.py` | Task Management | ✅ Referenz |

### old_agents/Agents (48 Ordner)
| Agent | Category | Bemerkung |
|-------|----------|-----------|
| `research_agent` | Research | Tavily, Web Search |
| `content_agent` | Content | Blog, Social, Newsletter |
| `revenue_agent` | Sales | Outreach, CRM, Follow-up |
| `coding_agent` | Dev | Code Generation, Docker, Auto-Debug |
| `operations_agent` | Ops | Monitoring, Backups, Health |
| `growth_agent` | Marketing | Twitter, LinkedIn |
| `pod_agent` | POD | Etsy, Printify |
| `mail_agent` | Communication | Brevo SMTP |
| `security_*` (7 Agents) | Security | Audits, Compliance |
| `ecommerce_*` (12 Agents) | E-Commerce | Shopify, Amazon, Inventory |
| `finance_*` (10 Agents) | Finance | Trading, Budget, Invoice |
| `hr_*` (9 Agents) | HR | Resume, Onboarding, Reviews |
| `startup_*` (3 Agents) | Startup | Pitch Deck, Investor Outreach |

---

## 📊 AKTUELLER STAND (April 2026)

### Aktiv im Einsatz
- **OpenClaw** als Haupt-Framework
- **CEO-Modell:** ClawMaster (CEO) → Builder, Security Officer, Data Manager
- **Telegram** als primärer Channel
- **7 aktive Agents** (lt. Nico's Flotte)

### Archiviert
- Alle 48 old_agents/ (Python-basiert, eigenständig)
- Alle old_scripts/ (13 Files)
- Alle old_logs/ (5 Files, ~1.1MB)

---

## 🎯 OFFENE PUNKTE (aus Archiv extrahiert)

### Technisch offen
- Discord Bot noch nicht fertig
- Google Analytics Integration offen
- Twitter OAuth erneuern
- Reddit API Keys beantragen
- Resend Pro Kaufen

### Business offen
- YouTube Kanal starten
- 10 Sales bis Ende April
- Lightning Address einrichten

### Archiv-bezogen
- Archive endgültig löschen nach Bestätigung

---

## ⚠️ WARNUNGEN & LESSONS LEARNED

1. **Gateway Restart killt alle Child-Prozesse** — Nie Gateway restarten während Bot-Instanzen laufen
2. **Trading Bot ist nicht profitabel** — +0.55% p.a. wird durch Binance Gebühren (-1.6%) negativ
3. **Buffer API unterstützt keine Video-Uploads** — API Limitation
4. **Docker Socket Permissions** — Immer `chmod 666 /var/run/docker.sock` nach Server-Restart
5. **Machine-ID Probleme** — Bei VPS-Neuinstallation muss /etc/machine-id regeneriert werden
6. **XDG_RUNTIME_DIR** — Bei systemd user services: `export XDG_RUNTIME_DIR=/run/user/$(id -u)`

---

*Erstellt: 2026-04-07 — Data Extraction Specialist Subagent*
*Archiv-Pfade: /archive/old_agents/ + /archive/old_scripts/*
