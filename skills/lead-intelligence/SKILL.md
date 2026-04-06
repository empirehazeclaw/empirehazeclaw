---
name: lead-intelligence
description: B2B Lead Generation und Scoring für EmpireHazeClaw. Nutze diese Skill wenn du neue potenzielle Kunden finden und bewerten willst. Analysiert Branchen und qualifiziert Leads nach Conversion-Chancen.
---

# 🎯 Lead Intelligence Skill

B2B Lead Generation und Scoring für EmpireHazeClaw's Managed AI Hosting.

## Nutzung

```bash
# Neue Leads generieren
python3 /home/clawbot/.openclaw/workspace/scripts/lead_generator.py --industry gastro --location de

# CRM updaten
python3 /home/clawbot/.openclaw/workspace/scripts/crm_manager.py --add-leads

# Revenue prognostizieren
python3 /home/clawbot/.openclaw/workspace/scripts/revenue_forecaster.py --days 30
```

## Kern-Scripts

| Script | Zweck |
|--------|-------|
| `lead_generator.py` | B2B Leads aus Branchen scrapen |
| `crm_manager.py` | Lead Pipeline verwalten |
| `revenue_forecaster.py` | Revenue-Prognose 30 Tage |

## Lead Scoring

| Score | Qualität | Aktion |
|-------|----------|--------|
| 80-100 | 🔥 Hot | Sofort kontaktieren |
| 50-79 | 🟡 Warm | In Sequenz aufnehmen |
| 20-49 | 🟢 Cold | Nurture Campaign |
| 0-19 | ⚪ Lost | Archivieren |

## Zielbranchen

- 🍽️ Gastro (Restaurants, Cafés)
- 🏥 Gesundheit (Arztpraxen, Apotheken)
- 🔧 Handwerk (SHK, Elektriker)
- 🏢 Service (Dienstleister)

## Daten

- Leads: `data/crm_leads.csv`
- Bounced: `data/bounced_leads.json`
- Sequenz-Log: `data/email_sequence_log.json`
