# Detailed Kill List v2 — Builder Workspace Analysis
*Erstellt: 2026-04-07 10:32 UTC*
*Workspace: /home/clawbot/.openclaw/workspace*

---

## Scripts zum Löschen (MIT BEGRÜNDUNG)

### 🔴 Veraltet — Neuere Version existiert

| File | Grund | Alternative |
|------|-------|------------|
| `task_manager_v3.py` | V4 existiert (v4 ist aktueller) | `task_manager_v4.py` behalten |
| `workflow_executor.py` | v2 existiert (v2 ist aktueller) | `workflow_executor_v2.py` behalten |
| `parallel-workflow.js` | v3 existiert (v3 ist aktueller) | `parallel-workflow-v3.js` behalten |
| `auto-delegate.js` | v3 existiert | `auto-delegate-v3.py` behalten |
| `local_closer.js` | v3.js existiert | `local_closer_v3.js` behalten |
| `twitter_growth_v2.py` | v3 existiert | `twitter_growth_v3.py` behalten |
| `autosync.js` | v2 existiert | `autosync_v2.js` behalten |

### 🟡 Duplikate (Identisch oder fast identisch)

| File | Grund | Alternative |
|------|-------|------------|
| `api/stripe-webhook.js` | Nahezu identisch zu `api/stripe/webhook.js` (nur Kommentar unterschiedlich) | `api/stripe/webhook.js` behalten |
| `paper_trading.py` | Komplett unterschiedliche Implementierung als `trading/paper_trading.py` — aber beide proprietär | trading/paper_trading.py behalten (aktueller) |
| `email_sequence.py` | Nur 260 Zeilen, unterscheidet sich stark von `scripts/email_sequence.py` (842 Zeilen) | `scripts/email_sequence.py` (vollständigere Version) |
| `database.py` | Nur 147 Zeilen vs `lib/database.py` oder `central_db.py` | Prüfen welches aktiver verwendet wird |

### 🟠 Stub / Placeholder Scripts

| File | Grund | Aktion |
|------|-------|--------|
| `run_agent.py` | Nur 32 Zeilen, Stub | Prüfen ob von größerem Script verwendet |
| `spawn_agent.py` | 1982 Bytes, könnte verwaist sein | Via grep prüfen |
| `delegate.py` | 1281 Bytes, Mini-Wrapper | Prüfen |
| `quick_research.py` | Nur 419 Bytes | Mit `simple_research.py` vergleichen |
| `quick_revenue.py` | Nur 528 Bytes | Mit `revenue_tracker.py` vergleichen |

### 🔴 Backup/Test Scripts (Executables ohne Hauptversion)

| File | Grund | Alternative |
|------|-------|------------|
| `implement_agents_batch.js` | 1924 Bytes, Executable, aber `implement_agents_batch.py` (7450 Bytes) ist vollständiger | `.py` Version behalten |
| `stripe-webhook-handler.py` | 7181 Bytes, Executable, veraltete Implementierung? | Prüfen: `api/stripe-webhook/index.js` |
| `self_testing.py` | 10661 Bytes, Executable | Prüfen ob aktiv verwendet |

### 🟠 API Duplikate (Stripe)

| File | Grund | Alternative |
|------|-------|------------|
| `api/stripe-webhook-status.js` (130B) | Winzig, fast leer | `api/stripe-webhook-status/index.js` (457B) behalten |
| `api/index.js` (335B) | Winzig | Braucht Review ob nötig |

---

## Scripts zum Behalten (mit Begründung)

| File | Begründung |
|------|------------|
| `task_manager_v4.py` | Aktuellste Version der task_manager Serie |
| `workflow_executor_v2.py` | Aktuellste Version |
| `parallel-workflow-v3.js` | Aktuellste Version |
| `autosync_v2.js` | Aktuellste autosync Version |
| `trading/paper_trading.py` | Komplexer als root paper_trading.py |
| `trading/ai_trading_bot_v2.py` | Kern-Bot für Trading |
| `central_db.py` | Haupt-Datenbank-Modul |
| `lib/database.py` | Library-Version, möglicherweise von anderen Scripts importiert |
| `scripts/email_sequence.py` | Vollständigere Version (842 vs 260 Zeilen) |
| `scripts/telegram_alert.py` | Aktuell (2026-04-06) |
| `scripts/memory_hybrid_search.py` | Aktuell (2026-04-06) |
| `api/stripe-webhook/index.js` | Aktuelle Stripe Integration |
| `api/stripe-webhook-status/index.js` | Vollständiger als die root Version |
| `skills/capability-evolver/` | Ganzes Skill-System, aktiv in Verwendung |
| `security/` | Security relevante Scripts |
| `autonomous/` | Autonome Agenten |

---

## 🔍 Problematische Bereiche

### 1. Duplikate mit unterschiedlichem Inhalt
Einige Dateien haben den gleichen Namen aber komplett unterschiedlichen Inhalt:
- `daily_review.py` vs `memory/scripts/daily_review.py`
- `memory_cleanup.py` vs `backup/memory_cleanup.py`
- `log_rotation.py` vs `backup/log_rotation.py`

### 2. Viele kleine Stub-Scripts
~100+ Scripts unter 1000 Bytes die möglicherweise ungenutzt sind.

### 3. Executable Scripts ohne Hauptversion
Mehrere `.py` und `.js` Dateien mit execute-Bit (chmod +x) die keine Hauptversion als Gegenstück haben.

---

## 📊 Statistik

| Kategorie | Anzahl |
|-----------|--------|
| Scripts analysiert | ~400 |
| Veraltete Versionen (v2→v3, etc) | ~15 |
| Duplikate identisch | ~5 |
| Duplikate unterschiedlich | ~10 |
| Stub/Placeholder | ~20 |
| Executables ohne Hauptversion | ~10 |

---

## ✅ Empfohlene Aktionen

1. **Sofort löschen:** task_manager_v3.py, workflow_executor.py, parallel-workflow.js, auto-delegate.js, local_closer.js, twitter_growth_v2.py, autosync.js
2. **Review:** api/stripe-webhook.js, paper_trading.py, email_sequence.py
3. **Investigate:** self_testing.py, strategic_command.py, orchestrator.py, parallel_executor.py (diese sind größer und haben wahrscheinlich Abhängigkeiten)

---

*Erstellt durch Builder Agent — Sovereign Workflow*