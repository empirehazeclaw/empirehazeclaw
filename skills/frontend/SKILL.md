---
name: frontend
description: Frontend Development für EmpireHazeClaw Websites. Nutze diese Skill wenn du Landing Pages, den Shop oder Blog bearbeiten willst. Vercel Deployment, Dark Theme Design, DE/EN Bilingual.
---

# 🌐 Frontend Skill

Website Development für EmpireHazeClaw's Online Presence.

## Unsere Websites

| Domain | Zweck | Stack |
|--------|-------|-------|
| empirehazeclaw.store | Shop (Stripe) | HTML/CSS/JS |
| empirehazeclaw.de | DE Corporate | HTML/CSS/JS |
| empirehazeclaw.com | EN Corporate | HTML/CSS/JS |
| empirehazeclaw.info | Blog | HTML/CSS/JS |

## Design System

### Farben
```css
--bg-primary: #0a0a0a;
--bg-secondary: #1a1a2e;
--accent: #00ff88;
--text: #ffffff;
--text-muted: #888888;
```

### Fonts
- **Headlines:** Syne (Google Fonts)
- **Body:** Outfit (Google Fonts)

### Template Files
```
website-rebuild/
├── de-template.html    # DE Design Template
├── com-template.html    # EN Design Template
├── store-template.html  # Shop Template
└── info-template.html  # Blog Template
```

## Deployment

```bash
# Vercel Deploy ( Production )
cd website-rebuild/new/[store|de|info]
vercel --prod --yes

# Vercel Token
# vcp_REDACTED
```

## Shop Features

- **Stripe Checkout** - Payment Links
- **Bilingual** - Auto-Detection DE/EN
- **Dark Theme** - Modern, Clean
- **Responsive** - Mobile First

## Stripe Checkout Sessions

```javascript
// Produkte
Restaurant AI Starter: cs_live_a1eZWpWAlqa0eV41ByRPVoD2n7iTp2H0jcgjKTnfbd8 (€29)
Automation Scripts:   cs_live_a1Yu9wjgdT5q7BRjkEyBQpKb3dLvfETUTJvA2RgHsCb (€49)
Notion Templates:     cs_live_a1VRVn2xCiREJYS7r4VtNiFv6JWIU6hBg6nEpOh1v0 (€19)
```

## Blog

- Auto-Post via Cron (Sonntag 6:00 Uhr)
- SEO optimiert
- Themen: KI, Business Automation, DSGVO

## Newsletter

- Footer Component: `templates/newsletter-footer.html`
- Subscriber Data: `data/newsletter-subscribers.json`
