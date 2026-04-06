# Website Coder Agent - SPEC.md
*Updated: 2026-03-23*

## Our Websites (CURRENT)

| Domain | Project | Content | Status |
|--------|---------|---------|--------|
| empirehazeclaw.de | de | 🇩🇪 German Corporate | ✅ Live |
| empirehazeclaw.com | com | 🇬🇧 English Corporate | ✅ Live |
| empirehazeclaw.store | store | 🛒 Shop + Stripe | ✅ Live |
| empirehazeclaw.info | info | 📰 Blog (83 Posts) | ✅ Live |

## Design System

### Colors (Mandatory!)
- Primary: #00ff88 (Mint Green)
- Background: #0a0a0f (Dark)
- Cards: #12121a

### Fonts
- Headlines: Syne (Google Fonts)
- Body: Outfit (Google Fonts)

## Deployment

### Locations
- Source: `/home/clawbot/.openclaw/workspace/website-rebuild/final/`
- Projects: `de`, `com`, `store`, `info`

### Commands
```bash
cd /home/clawbot/.openclaw/workspace/website-rebuild/final/[de|com|store|info]
vercel --prod --yes
```

### Vercel Dashboard (if issues)
https://vercel.com/dashboard/domains

## Store Products (Stripe)

| Product | Price | Stripe Link |
|---------|-------|-------------|
| Managed AI Starter | 99€/Mo | https://buy.stripe.com/fZudR97VGgiIdsB3Dw9k40z |
| Managed AI Pro | 199€/Mo | https://buy.stripe.com/7sY4gz6RC6I8agp7TM9k40H |
| Managed AI Enterprise | 499€/Mo | https://buy.stripe.com/5kQeVddg08Qg9clgqi9k40O |
| Trading Bot Basic | 79€/Mo | https://buy.stripe.com/9B67sL6RCeaAagpca29k40Q |
| Trading Bot Pro | 199€/Mo | https://buy.stripe.com/5kQdR9gsc9Ukbktgqi9k40X |
| Discord Bot | 79€ | https://buy.stripe.com/6oU5kDdg06I8agpfme9k40U |
| Landing Page | 199€ | https://buy.stripe.com/9B628ra3OgiI4W50rk9k40W |

## Blog

- 83 posts from old server
- Universal styling: `universal-style.js`
- Located: `/info/posts/`

## Standards

See: `WEBSITE_STANDARDS.md`
