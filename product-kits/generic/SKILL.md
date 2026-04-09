---
name: generic-ai-employee-kit
description: Generic AI Employee Package - Modulare KI-Mitarbeiter für alle Branchen. Email Agent + Support Agent + Scheduler Agent + Analytics Agent.
---

# 🤖 Generic AI Employee Kit

**Modulares KI-Mitarbeiter-System für alle Branchen**

## Enthaltene Agents (4 Module)

| Agent | Funktion | Alle Branchen |
|-------|---------|---------------|
| 📧 `email_agent.py` | E-Mails beantworten, sortieren, weiterleiten | ✅ |
| 🎧 `support_agent.py` | FAQs, Kundenanfragen, Tickets | ✅ |
| 📅 `scheduler_agent.py` | Termine buchen, erinnern, verwalten | ✅ |
| 📊 `analytics_agent.py` | Reports, Statistiken, Insights | ✅ |

## Quick Start

```bash
# 1. Setup Wizard starten
python3 scripts/setup_wizard.py

# 2. Konfiguration anpassen
nano config/email_config.json

# 3. Agents starten
python3 agents/email_agent.py
python3 agents/support_agent.py
python3 agents/scheduler_agent.py
python3 agents/analytics_agent.py

# 4. Oder alle via Cron
./deploy_kit.sh --email kunde@firma.de
```

## Deployment

```bash
# Auf Kundenserver:
curl -s https://empirehazeclaw.de/install | bash -s -- --email kunde@firma.de --agents email,support,scheduler,analytics
```

## Konfiguration

| Datei | Zweck |
|-------|-------|
| `config/email_config.json` | Hauptsystem-Konfiguration |
| `config/support_config.json` | Support Agent Einstellungen |
| `config/scheduler_config.json` | Terminplanung |
| `config/analytics_config.json` | Reporting |

## Branch-Kits

| Kit | Spezialisiert für |
|-----|------------------|
| `generic/` | Alle Branchen (Universell) |
| `restaurant/` | Restaurants, Cafés, Bars |
| `praxis/` | Arztpraxen, Therapeuten |

## Preisstruktur

| Package | Agents | Monatlich |
|---------|--------|-----------|
| Starter | 1 Agent | €99 |
| Professional | 2 Agents | €149 |
| Business | 3 Agents | €199 |
| Enterprise | Alle 4 + Custom | €499 |

## Agent Details

### 📧 Email Agent
- Auto-Response basierend auf Keywords
- IMAP/SMTP Integration
- Spam-Erkennung
- Logging aller Emails

### 🎧 Support Agent
- FAQ-basiertes Antwortsystem
- Ticket-Erstellung bei Eskalation
- Categorisierung von Anfragen
- 24h SLA Tracking

### 📅 Scheduler Agent
- Verfügbare Slots berechnen
- Termine buchen/stornieren
- Automatische Erinnerungen
- Kalender-Integration (bald)

### 📊 Analytics Agent
- Tägliche/Wöchentliche Reports
- Email-Volumen Statistik
- Ticket-Statistik
- Response-Time Tracking

## Data Files

| Datei | Inhalt |
|-------|--------|
| `data/email_log.json` | Alle Email-Interaktionen |
| `data/support_tickets.json` | Support Tickets |
| `data/appointments.json` | Termine |
| `data/faq.json` | FAQ Einträge |

## System Requirements

- Python 3.8+
- Linux Server (Ubuntu 20.04+)
- Gmail Account mit App Password ODER
- SMTP/IMAP Server

## Deployment Status

| Komponente | Status |
|-----------|--------|
| Email Agent | ✅ Ready |
| Support Agent | ✅ Ready |
| Scheduler Agent | ✅ Ready |
| Analytics Agent | ✅ Ready |
| Setup Wizard | ✅ Ready |
| Deploy Script | ✅ Ready |
| Branch Kits | 🔄 In Progress |
| Auto-Update | 🔄 Planned |
