---
name: web-orchestrator
description: Autonomes Web-Management für EmpireHazeClaw's 4 Vercel Domains. Überwacht Performance, SEO, Deployments und synchronisiert Content DE↔EN.
---

# 🌐 Web Orchestrator Skill

**Autonomes Web-Management für alle 4 Vercel Domains**

## Domains

| Domain | Sprache | Zweck |
|--------|---------|-------|
| empirehazeclaw.de | DE | Lokale SEO, deutsche Nutzer |
| empirehazeclaw.com | EN | Globale Skalierung |
| empirehazeclaw.info | DE/EN | Blog, Wissensdatenbank |
| empirehazeclaw.store | DE/EN | E-Commerce |

## Scripts

### Daily Health Check
```bash
python3 /home/clawbot/.openclaw/workspace/web-orchestrator/scripts/daily_health_check.py
```
- Prüft alle 4 Domains auf Erreichbarkeit
- Misst Latenz
- Loggt nach `monitoring/health_log.json`
- Erstellt Alert bei Fehlern

### Weekly SEO Audit
```bash
python3 /home/clawbot/.openclaw/workspace/web-orchestrator/scripts/seo_audit.py
```
- Analysiert Title, Meta, H1, Alt-Tags
- Prüft OG Tags für Social
- Score 0-100 pro Domain
- Report: `monitoring/seo_audit_report.json`

### Content Sync DE↔EN
```bash
python3 /home/clawbot/.openclaw/workspace/web-orchestrator/scripts/content_sync.py
```
- Erkennt neue Blog-Posts auf .info
- Erstellt Sync-Jobs für Übersetzung
- Vorbereitung für Auto-Translation

### Deployment Watcher
```bash
python3 /home/clawbot/.openclaw/workspace/web-orchestrator/scripts/deployment_watcher.py
```
- Prüft letzte 24h Deployments
- Analysiert Build-Fehler
- Loggt nach `deployments/deploy_log.json`

### Vercel Deploy
```bash
# Deploy einzelne Site
python3 /home/clawbot/.openclaw/workspace/web-orchestrator/scripts/vercel_deploy.py de

# Deploy alle Sites
python3 /home/clawbot/.openclaw/workspace/web-orchestrator/scripts/vercel_deploy.py

# Preview Branch
python3 /home/clawbot/.openclaw/workspace/web-orchestrator/scripts/vercel_deploy.py store --preview
```

## Cron Jobs

| Job | Schedule | Script |
|-----|----------|--------|
| Daily Health | 0 8 * * * | daily_health_check.py |
| SEO Audit | 0 9 * * 0 | seo_audit.py |
| Content Sync | 0 */6 * * * | content_sync.py |
| Deploy Watcher | */15 * * * * | deployment_watcher.py |

## Monitoring Files

```
monitoring/
├── health_log.json      # Alle Health Checks
├── alerts.json          # Fehler-Alerts
├── seo_audit_report.json # Letzter SEO Report
└── sync_data/
    ├── synced_content.json  # Sync-Tracking
    └── sync_jobs_pending.json # Offene Sync-Jobs

deployments/
├── deploy_log.json     # Alle Deployments
└── errors.json         # Build-Fehler
```

## Arbeitsweise

1. **Proaktiv** - Ich handle ohne zu fragen
2. **Bei Issues** - Analysiere und fixe wenn möglich
3. **Preview zuerst** - Größere Änderungen als Preview deployen
4. **Dokumentieren** - Alle Actions in Memory speichern

## Bei Problemen

- Health Check fehlgeschlagen → Alert loggen → Telegram Benachrichtigung
- SEO Score < 50 → Sofort analysieren → Fix vorschlagen
- Build Error → Logs analysieren → Fix anwenden
- Content Update → Sync Job erstellen → Übersetzung vorbereiten

## Vercel API Token

```
vcp_REDACTED
```
