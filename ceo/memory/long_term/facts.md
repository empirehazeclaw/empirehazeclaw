# FACTS — Sir HazeClaw Long-Term Memory

_Letzte Aktualisierung: 2026-04-13_
_Migrated from: /workspace/MEMORY.md + /ceo/MEMORY.md_

---

## 👤 ÜBER NICO

- **Name:** Nico
- **Telegram:** 5392634979
- **Email:** empirehazeclaw@gmail.com
- **Sprache:** Deutsch
- **Background:** KFZ Mechatroniker → Ingenieur Werkstoffkunde
- **Started:** Ende Februar 2026

---

## 🏢 BUSINESS (EmpireHazeClaw)

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

## 📊 PIPELINE (Stand 2026-04-07)

| Metric | Value |
|--------|-------|
| Leads | 4,088 |
| Emails gesendet | 73 |
| Responses | 0 |
| Customers | 0 |
| Revenue | €0 |

---

## 🎯 PRIORITÄTEN (Q2 2026)

1. **ERSTE KUNDEN GEWINNEN** - P1 (0 Kunden, €0 Revenue)
2. Outreach Kampagne - 73 Emails, 0 Responses
3. Social Media (TikTok)
4. Blog Content

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

## ⏱️ TIMEOUT RULES (CRITICAL)

**SYSTEM KILLS ME AFTER ~60-90s REGARDLESS OF INSTRUCTIONS!**

| Task | Rule |
|------|------|
| < 60s | Direkt ausführen |
| > 60s (unwichtig) | Background mode (`&`) |
| > 60s (wichtig) | Cron Job |

---

*Facts are stable — only update when something changes.*