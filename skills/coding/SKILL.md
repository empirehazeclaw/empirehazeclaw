---
name: coding
description: Full-Stack Development Skill für EmpireHazeClaw. Nutze diese Skill wenn du Websites, APIs, Scripts, OpenClaw Plugins oder automatisierte Tools bauen willst. Unterstützt Python, JavaScript/Node.js, Bash.
---

# 💻 Coding Skill

Full-Stack Development für EmpireHazeClaw's AI Hosting Business.

## Sprachen & Frameworks

| Sprache | Use Case | Priority |
|---------|----------|----------|
| **Python** | Scripts, Automation, AI/ML | 🔴 Hoch |
| **JavaScript/Node.js** | APIs, OpenClaw Plugins, Tools | 🔴 Hoch |
| **Bash** | Server Scripts, Cron Jobs, CLI | 🔴 Hoch |
| **TypeScript** | OpenClaw Plugins, React | 🟡 Mittel |
| **HTML/CSS** | Websites, Landing Pages | 🔴 Hoch |

## Kern-Bereiche

### 🌐 Frontend
- **React** - OpenClaw Plugins, interaktive UIs
- **HTML/CSS** - Landing Pages, Marketing Sites
- **Vercel** - Deployment (`vercel --prod --yes`)
- **Templates** - `de-template.html`, `com-template.html`

### ⚙️ Backend
- **Node.js** - APIs, Webhooks, Server
- **Express** - HTTP Server, REST APIs
- **Stripe** - Payments, Webhooks, Checkout Sessions
- **WebSocket** - Real-time communication

### 🔌 APIs & Integrations
- **Stripe API** - Payments, Subscriptions, Webhooks
- **GOG CLI** - Gmail/Email Integration
- **Telegram Bot API** - Notifications, Commands
- **Buffer API** - Social Media Posting
- **Tavily API** - Web Research

### 🐳 DevOps
- **Docker** - Container für Services
- **Nginx** - Reverse Proxy, Web Server
- **Systemd** - Service Management
- **Cron** - Scheduled Tasks

## Projekt-Struktur

```
/home/clawbot/.openclaw/workspace/
├── scripts/           # Python & JS Scripts
├── agents/            # Agenten (Python)
├── remotion-video/    # Video Production
├── website-rebuild/    # Vercel Websites
│   ├── new/de/        # DE Website
│   ├── new/com/       # EN Website
│   └── new/store/     # Shop
└── skills/            # OpenClaw Skills
```

## Deployment Commands

```bash
# Website Deploy (Vercel)
cd website-rebuild/new/[store|de|info] && vercel --prod --yes

# Service Neustart
openclaw gateway restart

# Nginx Reload
sudo nginx -s reload
```

## OpenClaw Plugin Entwicklung

```typescript
// plugins/mein-plugin/index.ts
import type { OpenClawPluginApi } from 'openclaw/plugin-sdk';

export default function createPlugin(api: OpenClawPluginApi) {
  return {
    name: 'mein-plugin',
    async onLoad() {
      // Plugin geladen
    },
    tools: [
      // Eigene Tools definieren
    ]
  };
}
```

## Environment Variables

```bash
# Email
GMAIL_USER=empirehazeclaw@gmail.com
GMAIL_APP_PASSWORD=xxx

# APIs
STRIPE_SECRET_KEY=sk_live_xxx
TAVILY_API_KEY=tvly-xxx
OPENAI_API_KEY=sk-xxx

# Vercel
VERCEL_TOKEN=vcp_xxx
```

## Scripts Sammlung

| Script | Zweck |
|--------|-------|
| `ttsnotify.js` | Text-to-Speech Benachrichtigungen |
| `autosync_v2.js` | Memory Auto-Sync |
| `email.js` | Email senden via GOG |
| `webhook.js` | Telegram/Webhook Alerts |
| `scheduled-workflows.js` | Cron Workflow Manager |

## Best Practices

1. **Security** - Keine API Keys in Code, .env nutzen
2. **Testing** - Vor Deploy testen
3. **Logging** - Logging für Fehlerbehebung
4. **Backup** - Git regelmäßig committen

---

## 🆕 Coding Patterns (gelernt 2026-04-10)

### Pattern: Test-Driven Scripting
1. Schreibe zuerst das Script
2. Baue dann Tests dafür
3. Nutze `test_framework.py` für automatische Tests

### Pattern: CLI mit zwei Modus
```python
# Modus 1: Import (für Tests/Tools)
def main_logic():
    return data

# Modus 2: CLI (für direkten Aufruf)
if __name__ == "__main__":
    print(main_logic())
```

### Pattern: Strukturierte Outputs
- Scripts sollen sowohl `return` als auch `print` können
- Für Integration mit anderen Tools

### Pattern: Error Handling
- Keine `except: pass`
- Explizite Fehlerbehandlung
- Logging für Debugging

### Pattern: Security First
- Keine `exec()` wo nicht nötig
- Input Validation
- Secrets aus Env Vars

