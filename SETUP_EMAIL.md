# 📧 Email Setup Guide

## Option 1: Gmail App Password (Empfohlen für Server)

### Schritt 1: App Password generieren

1. **2-Faktor-Auth aktivieren** (falls noch nicht):
   - https://myaccount.google.com/security
   - "2-Step Verification" einschalten

2. **App Password generieren**:
   - https://myaccount.google.com/apppasswords
   - App wählen: "Mail"
   - Gerät: "Other (Custom name)" → "Server"
   - **16-stelliges App Password kopieren** (Format: `xxxx xxxx xxxx xxxx`)

### Schritt 2: App Password hinterlegen

```bash
# Auf dem Server:
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"

# Testen:
python3 /home/clawbot/.openclaw/workspace/lib/email_smtp.py --to deine.email@gmail.com --subject "Test" --body "Hello World" --test
```

### Schritt 3: Persistenz (optional)

```bash
# In .bashrc oder .profile:
echo 'export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"' >> ~/.bashrc
echo 'export GMAIL_USER="empirehazeclaw@gmail.com"' >> ~/.bashrc
```

---

## Option 2: GOG CLI (Benötigt Browser-OAuth)

**Problem:** GOG OAuth erfordert einen Browser. Auf einem Headless-Server nicht möglich.

```bash
# Wenn du trotzdem GOG nutzen willst:
# 1. Lokal auf deinem Mac/PC OAuth durchführen
# 2. Token exportieren:
gog auth export > gog_token.json
# 3. Token auf Server übertragen
```

---

## Test nach Setup

```bash
# Test Email senden:
python3 /home/clawbot/.openclaw/workspace/lib/email_smtp.py \
  --to empirehazeclaw@gmail.com \
  --subject "Test von Server" \
  --body "Email funktioniert!"

# Oder über Email Sequence:
python3 /home/clawbot/.openclaw/workspace/email_sequence.py --status
```

---

## Troubleshooting

| Problem | Lösung |
|---------|-------|
| "Auth failed" | App Password falsch oder nicht gesetzt |
| "Credentials not found" | GMAIL_APP_PASSWORD env variable prüfen |
| "SMTP connection refused" | Port 587 nicht offen ( Firewall?) |

---

*Setup: 2026-03-28*
