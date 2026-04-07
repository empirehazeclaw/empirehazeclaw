# MASTER TODO - Workspace Architect
*Erstellt: 2026-04-07 09:13 UTC*

---

## ✅ ARCHIVIERUNG ABGESCHLOSSEN

| Was | Alte Position | Neue Position | Status |
|-----|---------------|---------------|--------|
| agents/ Ordner | workspace/agents/ | archive/old_agents/ | ✅ |
| autonomous_loop.log | workspace/logs/ | archive/old_logs/ | ✅ |
| watchdog_cron.log | workspace/logs/ | archive/old_logs/ | ✅ |
| watchdog.log | workspace/logs/ | archive/old_logs/ | ✅ |
| watchdog_alerts.log | workspace/logs/ | archive/old_logs/ | ✅ |
| self_healing.log | workspace/logs/ | archive/old_logs/ | ✅ |
| memory losen Dateien (15x) | workspace/memory/*.md | workspace/memory/archive/ | ✅ |
| task_manager_v2.py | workspace/ | archive/old_scripts/ | ✅ |
| auto-delegate-v2.py | workspace/ | archive/old_scripts/ | ✅ |
| nightshift.sh | workspace/ | archive/old_scripts/ | ✅ |
| nightshift_v2.sh | workspace/ | archive/old_scripts/ | ✅ |
| nightshift_extended.sh | workspace/ | archive/old_scripts/ | ✅ |
| twitter_growth_v2.py | workspace/ | archive/old_scripts/ | ✅ |
| local_closer.js | workspace/ | archive/old_scripts/ | ✅ |
| local_closer_v2.js | workspace/ | archive/old_scripts/ | ✅ |
| local_closer_full.py | workspace/ | archive/old_scripts/ | ✅ |
| scrape_it_agencies.py | workspace/ | archive/old_scripts/ | ✅ |
| scrape_it_agencies2.py | workspace/ | archive/old_scripts/ | ✅ |
| scrape_it_agencies_fix.py | workspace/ | archive/old_scripts/ | ✅ |

---

## 📁 NEUE VERZEICHNISSTRUKTUR

```
workspace/
├── archive/
│   ├── old_agents/       ✅ (48 subdirs moved)
│   ├── old_logs/         ✅ (5 files, ~1.1MB)
│   ├── old_scripts/      ✅ (13 files)
│   └── old_versions/     (pre-existing)
├── active/              ✅ (empty - for ongoing dev)
├── configs/             ✅ (empty - for backup configs)
├── memory/
│   ├── archive/          ✅ (15 .md files consolidated)
│   └── [structured dirs preserved]
└── todos/
    └── MASTER_TODO.md    ✅ (this file)
```

---

## 🔴 PRIORITÄT 1 - BLOCKER

| Task | Status | Wer |
|------|--------|-----|
| Gateway restart (für QC Agent) | 🔴 Offen | Nico |
| GitHub Token rotieren | 🔴 Offen | Nico |
| Security Rotation Keys (6+ Keys) | 🔴 Offen | Nico |

---

## 🟡 PRIORITÄT 2 - DIESE WOCHE

| Task | Status | Wer |
|------|--------|-----|
| Resend Pro kaufen | 🟡 Offen | Nico |
| Twitter OAuth erneuern | 🟡 Offen | Nico |
| Reddit API Keys beantragen | 🟡 Offen | Nico |
| Discord Bot fixen | 🟡 Offen | OpenClaw |
| Google Analytics einbauen | 🟡 Offen | OpenClaw |

---

## 🟢 PRIORITÄT 3 - NÄCHSTE WOCHEN

| Task | Status | Wer |
|------|--------|-----|
| YouTube Kanal starten | 🟢 Offen | OpenClaw |
| 10 Sales bis Ende April | 🟢 Offen | OpenClaw |
| Lightning Address | 🟢 Offen | OpenClaw |

---

## 📦 NEUE ITEMS AUS ARCHIV-EXTRAKTION

| Task | Quelle | Status | Anmerkung |
|------|--------|--------|----------|
| Discord Bot finalisieren | old_agents | 🟡 Offen | Nie fertiggestellt |
| Buffer Video-Upload Alternative | old_agents | 🟢 Offen | Buffer-API unterstützt kein Video |
| Trading Bot überdenken | old_agents | 🟢 Offen | Nicht profitabel (Gebühren > Gewinn) |
| IT-Agenturen Scraper rechtlich prüfen | old_scripts | 🟡 Offen | Rechtliche Risiken unklar |

---

## 📊 ARCHIV ÜBERSICHT

| Kategorie | Anzahl | Gesamtgröße |
|----------|--------|-------------|
| old_agents | 48 dirs | ~20MB+ |
| old_logs | 5 files | ~1.1MB |
| old_scripts | 13 files | ~100KB |
| memory/archive | 15 files | ~4MB |

---

*Workspace Architect - Aufräumen abgeschlossen*
