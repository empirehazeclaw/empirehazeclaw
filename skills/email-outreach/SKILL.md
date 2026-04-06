---
name: email-outreach
description: Automatisiertes E-Mail Outreach für B2B Lead-Gewinnung. Nutze diese Skill wenn du E-Mail Kampagnen an potenzielle Kunden senden willst. Verwendet GOG CLI für Gmail.
---

# 📧 Email Outreach Skill

Automatisiertes E-Mail Outreach für EmpireHazeClaw.

## Nutzung

```bash
# Einzelne E-Mail senden
python3 /home/clawbot/.openclaw/workspace/scripts/automated_outreach.py --lead "max@beispiel.de" --template intro

# Kampagne starten
python3 /home/clawbot/.openclaw/workspace/scripts/email_sequence.py --campaign starter

# Outreach optimieren
python3 /home/clawbot/.openclaw/workspace/scripts/outreach_optimizer.py
```

## Kern-Scripts

| Script | Zweck |
|--------|-------|
| `automated_outreach.py` | Einzelne Leads kontaktieren |
| `email_sequence.py` | 4-Step Auto-Follow-up Sequence |
| `response_tracker.py` | Email Response Tracking |
| `outreach_optimizer.py` | Analyse + Verbesserungen |

## Workflow

1. **Lead generieren** → `lead_generator.py`
2. **Personalisieren** → `humanize_content.py`
3. **Senden** → `automated_outreach.py`
4. **Tracken** → `response_tracker.py`
5. **Optimieren** → `outreach_optimizer.py`

## Konfiguration

- SMTP: Gmail via GOG CLI
- Templates: 4-Step Sequence (Intro → Follow-up → Value → Close)
- Tracking: `data/sent_leads.json`, `data/email_sequence_log.json`
