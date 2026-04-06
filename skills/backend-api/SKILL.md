---
name: backend-api
description: Backend & API Development für EmpireHazeClaw. Nutze diese Skill wenn du APIs, Webhooks, Server-Side Logic oder Payment Integrationen bauen willst. Node.js, Express, Stripe, Webhooks.
---

# ⚙️ Backend & API Skill

Backend Development für EmpireHazeClaw's Services.

## Server Setup

| Service | Port | Status |
|---------|------|--------|
| OpenClaw Gateway | 18789 | ✅ Running |
| Mission Control | 8889 | ✅ Running |
| Websites | 80/443 | ✅ Live |

## APIs

### Stripe API
```javascript
// Stripe Keys
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

// Checkout Sessions
POST /create-checkout-session
POST /create-portal-session
```

### Gmail/GOG API
```javascript
// Via GOG CLI
gog send --to empfaenger@example.com --subject "Betreff" --body "Nachricht"

// Token Refresh
gog auth login --account empirehazeclaw@gmail.com
```

### Tavily API (Research)
```javascript
// Web Research
TAVILY_API_KEY=tvly-dev-...
```

## Webhooks

### Stripe Webhooks
```javascript
// Endpoint: /webhook/stripe
// Events: checkout.session.completed, customer.subscription.updated
```

### Telegram Webhooks
```javascript
// Bot Token: 8397732232:AAEIZqzMVSC-N6YVp0ef4Et1-v_tIproH9Y
```

## Server Scripts

| Script | Zweck |
|--------|-------|
| `server_ops_agent.py` | Server Health Monitoring |
| `stripe_webhook_handler.py` | Stripe Event Handling |

## Express.js Template

```javascript
const express = require('express');
const app = express();

app.use(express.json());
app.use(express.raw({ type: 'application/json' }));

// Stripe Webhook
app.post('/webhook/stripe', (req, res) => {
  // Handle Stripe event
});

// Health Check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on ${PORT}`));
```

## Environment

```bash
# Server
NODE_ENV=production
PORT=3000

# APIs
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
GMAIL_USER=empirehazeclaw@gmail.com
TAVILY_API_KEY=tvly-xxx
```
