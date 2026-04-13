
## Email System (Updated 2026-03-26)

### Configuration
| Provider | Status | Usage |
|----------|--------|-------|
| Gmail (GOG CLI) | ✅ ACTIVE | All emails - transactional, outreach, receipts |
| Brevo | ❌ REMOVED | No longer used |
| Resend | ❌ REMOVED | No longer used |

### Email Scripts
| Script | Purpose |
|--------|---------|
| `scripts/email.js` | Main email sender via Gmail API |
| `scripts/send_email_gmail.js` | Direct Gmail API integration |

### Usage
```bash
node scripts/email.js <to> <subject> <body>
```

### Technical Details
- Uses Gmail API (not SMTP)
- OAuth token from GOG CLI (`~/.config/gogcli/token.env`)
- No external email providers needed
