# Builder Cleanup — Kill List
*Erstellt: 2026-04-07*

---

## ⚠️ DEPRECATED — Zum Löschen markiert

### task_manager_v2.py
- **Grund:** V3 + V4 existieren
- **Behalten:** `task_manager_v3.py`, `task_manager_v4.py`
- **Pfad:** `/home/clawbot/.openclaw/workspace/task_manager_v2.py`

### auto-delegate-v2.py
- **Grund:** v3 ist aktueller
- **Behalten:** `auto-delegate-v3.py`
- **Pfad:** `/home/clawbot/.openclaw/workspace/auto-delegate-v2.py`

### nightshift.sh / nightshift_v2.sh / nightshift_extended.sh
- **Grund:** `night_shift.py` ist die aktuelle Implementierung
- **Behalten:** `night_shift.py` (im workspace root suchen)
- **Pfade:**
  - `/home/clawbot/.openclaw/workspace/nightshift.sh`
  - `/home/clawbot/.openclaw/workspace/nightshift_v2.sh`
  - `/home/clawbot/.openclaw/workspace/nightshift_extended.sh`

### scrape_it_agencies.py / scrape_it_agencies2.py / scrape_it_agencies_fix.py
- **Grund:** Nur aktuellste Version behalten
- **Behalten:** `scrape_it_agencies3.py`
- **Pfade:**
  - `/home/clawbot/.openclaw/workspace/scrape_it_agencies.py`
  - `/home/clawbot/.openclaw/workspace/scrape_it_agencies2.py`
  - `/home/clawbot/.openclaw/workspace/scrape_it_agencies_fix.py`

### twitter_growth_v2.py
- **Grund:** v3 ist aktueller
- **Behalten:** `twitter_growth_v3.py`
- **Pfad:** `/home/clawbot/.openclaw/workspace/twitter_growth_v2.py`

### local_closer.js / local_closer_v2.js / local_closer_full.py
- **Grund:** v3.js ist aktuellste Version
- **Behalten:** `local_closer_v3.js`
- **Pfade:**
  - `/home/clawbot/.openclaw/workspace/local_closer.js`
  - `/home/clawbot/.openclaw/workspace/local_closer_v2.js`
  - `/home/clawbot/.openclaw/workspace/local_closer_full.py`

### agent-delegator.js / auto-delegate.js / smart-auto-delegate.py
- **Grund:** Nur einen behalten — Konsolidierung nötig
- **Pfade:**
  - `/home/clawbot/.openclaw/workspace/agent-delegator.js`
  - `/home/clawbot/.openclaw/workspace/auto-delegate.js`
  - `/home/clawbot/.openclaw/workspace/smart-auto-delegate.py`

---

## 📋 Zusammenfassung

| Kategorie | Löschen | Behalten |
|----------|--------|---------|
| task_manager | v2 | v3, v4 |
| auto-delegate | v2 | v3 |
| nightshift | .sh, v2.sh, extended.sh | night_shift.py |
| scrape_it_agencies | .py, 2, _fix | 3 |
| twitter_growth | v2 | v3 |
| local_closer | .js, v2, full.py | v3.js |
| delegator Scripts | alle 3 | einen wählen |

---

**Hinweis:** Die eigentlichen Löschbefehle wurden NICHT ausgeführt — diese Liste dient als Review/Checkliste. Löschung nach Bestätigung durchführen.
