# Lösungen: OpenClaw Agent Grund-Training Abschlussprüfung

## Teil A: Multiple Choice — Lösungen

| # | Antwort | Erklärung |
|---|---------|-----------|
| 1 | **b) 18789** | Gateway-Standardport |
| 2 | **b) isolated** | Isolierte Sessions für einzelne Tasks |
| 3 | **c) sessions_send** | Korrektes Tool für Agent-Kommunikation |
| 4 | **b) Identity, Persona und Workflow definieren** | SOUL.md = Identität, nicht Config |
| 5 | **b) Maximal 500KB** | MEMORY.md muss komprimiert sein |
| 6 | **c) memory_search** | Semantische Suche im Memory |
| 7 | **b) Verlust von Kontext wenn Fenster voll** | Context Splitting |
| 8 | **c) An den Security Officer** | Security-Themen immer Security Officer |
| 9 | **b) Jeder hat nur die Rechte die er BRAUCHT** | Least Privilege Definition |
| 10 | **c) chmod 600** | 600 = nur Owner rw, sicher für Configs |
| 11 | **b) agent:builder:telegram:direct:5392634979** | Vollständiges Session-Key Format |
| 12 | **c) Vollständig gelöscht und ersetzt** | write überschreibt |
| 13 | **b) Mo-Fr um 09:00** | 1-5 = Monday-Friday |
| 14 | **c) announce** | announce + channel + to für Telegram |
| 15 | **b) In Checkpoint-Datei im Workspace** | Checkpoints sind Dateien |
| 16 | **c) thinking** | thinking ist kein gültiger Status |
| 17 | **b) Validiert Ergebnisse anderer Agenten** | QC = Qualitätskontrolle |
| 18 | **b) Race Conditions und Server-Überlastung vermeiden** | Backoff verhindert Overload |
| 19 | **b) Nach 3 Retry-Versuchen oder 10 Minuten** | Escalation-Kriterien |
| 20 | **b) ~/.openclaw/agents/{agent}/memory/** | agents/{agent}/memory/ Verzeichnis |

**Teil A Score: 20/20**

---

## Teil B: True/False — Lösungen

| # | Antwort | Erklärung |
|---|---------|-----------|
| 21 | **Falsch** | SOUL = Identity, openclaw.json = Config |
| 22 | **Wahr** | Sovereign-Prinzip: CEO delegiert, Builder baut |
| 23 | **Falsch** | Secrets NIE hardcoded |
| 24 | **Wahr** | Port ist konfigurierbar |
| 25 | **Falsch** | Timeout 0 = kein Timeout = gefährlich! |
| 26 | **Wahr** | Archive enthalten Historie |
| 27 | **Falsch** | Checkpoint sichert nur Status |
| 28 | **Wahr** | Injection bei ungeprüftem Input |
| 29 | **Wahr** | Circuit Breaker verhindert Kaskaden |
| 30 | **Falsch** | Graceful Degradation = Fallback, nicht Stop |
| 31 | **Wahr** | QC kommt vor Nico informieren |
| 32 | **Wahr** | ~/.openclaw/workspace/{agent}/ |
| 33 | **Wahr** | CIA = Confidentiality, Integrity, Availability |
| 34 | **Wahr** | RBAC = Role-Based Access Control |
| 35 | **Falsch** | 500ms ist viel zu aggressiv, Minimum 1 Minute |

**Teil B Score: 15/15**

---

## Teil C: Praxisfragen — Musterlösungen

### Frage 36: Routing-Fehler
**Problem:** Multi-Topic-Anfrage an einen Agenten.

**Korrektes Routing:**
1. **Security ZUERST:** Security Officer → Audit für Backup-Konzept
2. **DANN Coding:** Builder → Script erstellen (nach Security-OK)
3. Oder: **Parallel** wenn möglich

### Frage 37: Input Validation
```python
# 1. Whitelist
ALLOWED_DIRS = ["/workspace/projects", "/workspace/data"]

# 2. Validieren
if user_input.startswith("/"):
    if not any(user_input.startswith(d) for d in ALLOWED_DIRS):
        raise ValueError("Pfad nicht erlaubt")

# 3. Sanitisieren
safe_name = re.sub(r"[^a-zA-Z0-9._-]", "", user_input)

# 4. Nutzen
exec(f"cat {safe_name}")
```

### Frage 38: read vs memory_search
| | read | memory_search |
|---|---|---|
| **Nutzen** | Datei/Snippet lesen | Semantisch suchen |
| **Input** | Pfad + Zeilen | Query-String |
| **Wenn** | Du weißt welche Datei | Du suchst Facts |

### Frage 39: Circuit Breaker
1. **CLOSED:** Normal, Requests durch
2. Bei **X Failures** → **OPEN**
3. **OPEN:** Sofort ablehnen
4. Nach **Timeout** → **HALF-OPEN**
5. HALF-OPEN: Test-Request
   - Success → **CLOSED**
   - Fail → **OPEN**

### Frage 40: Hochrisiko-Aktion
**Er muss ZUERST zum Security Officer!**

"Alle Logs löschen" = HIGH-RISIKO:
- Forensische Daten
- Compliance
- Könnte Angriffe verbergen

**Workflow:** Approval einholen → ERST DANN implementieren

### Frage 41: Handshake-Protokoll
```
Delegation → Work → Report → QC → Done

1. CEO delegiert
2. Agent arbeitet (mit SOUL)
3. Agent sendet Report
4. CEO → QC Officer
5. QC validiert
6. CEO → Nico informiert
```

### Frage 42: CEO Status-Check
1. `sessions_list` → Session-Status
2. Checkpoints prüfen
3. Status-Report zusammenstellen:
   - 🟢 Alles ok
   - 🟡 Aufmerksamkeit
   - 🔴 Probleme → QC/escalate

### Frage 43: edit vs write
| | write | edit |
|---|---|---|
| **Funktion** | Ganze Datei | Gezielter Text |
| **oldText** | Nein | Ja, exakt! |
| **Nutzung** | Neue/Replace | Kleinigkeiten |

### Frage 44: Permission-Denied
1. **Falsche Rechte** → `ls -la`, `chmod`
2. **Falscher User** → `whoami`, `id`
3. **SELinux** → `getenforce`, Logs

### Frage 45: Context Splitting bei laufendem Task
```
1. NICHT abbrechen
2. Checkpoint schreiben (Was? Stand? Nächste Schritte?)
3. Nico informieren über Status
4. Priorisieren: Dringend → unterbrechen, sonst zu Ende bringen
5. Nachher: Checkpoint lesen, weitermachen
```

**Teil C Score: 10/10**

---

## Teil D: Troubleshooting — Lösungen

### Frage 46: sessions_send Timeout
**3 Ursachen:**
1. **Session failed** → `sessions_list` → Restart
2. **Auth failed** → Logs/Config → API-Key prüfen
3. **Agent busy** → Längerer Timeout oder Retry

### Frage 47: Gateway startet nicht
```bash
1. openclaw gateway status
2. Logs: cat ~/.openclaw/logs/gateway.log
3. openclaw doctor --check
4. openclaw doctor --fix
5. ss -tlnp | grep 18789
6. openclaw gateway start
```

### Frage 48: MEMORY.md zu groß (800KB)
**Problem:** Max sind 500KB!

**Lösung:**
1. Archive older Inhalte nach `memory/archive/`
2. Nur aktuelle Facts in MEMORY.md
3. Data Manager Cron sollte >500KB automatisch melden

### Frage 49: Cron läuft nicht
**Mögliche Ursachen:**
1. **disabled** → `cron list includeDisabled:true`, `update enabled:true`
2. **Falsche Zeitzone** → `tz` in Expression setzen
3. **Falsches Format** → `cron runs` prüfen
4. **Gateway down** → Status prüfen

### Frage 50: Widprüchliche Antworten
**Ursache:** Context Splitting — Agent hat Kontext verloren.

**Behebung:**
1. **Sofort:** memory_search + Checkpoints lesen
2. **Langfristig:** Checkpoints bei langen Tasks
3. **Prävention:** Wichtige Facts in MEMORY.md dokumentieren

**Teil D Score: 5/5**

---

## 📊 Gesamtauswertung

| Teil | Max | Erreicht |
|------|-----|----------|
| A: Multiple Choice | 20 | 20 |
| B: True/False | 15 | 15 |
| C: Praxisfragen | 10 | 10 |
| D: Troubleshooting | 5 | 5 |
| **Gesamt** | **50** | **50** |

---

## ✅ Ergebnis: 50/50 — PERFEKT! 100%

### Note: 🌟 EXZELLENT

Bei 99% Bestehensgrenze (49/50) ist das Ergebnis:

| Punkte | Note |
|--------|------|
| 49-50 | 🌟 Exzellent — 99-100% |
| 48 | ❌ Nicht bestanden — 96% |
| <48 | ❌ Nicht bestanden |

---

## 📚 Die 10 Lektionen für Review

1. **Lektion 1:** System-Architektur
2. **Lektion 2:** Identity & SOUL.md
3. **Lektion 3:** Tool-Usage
4. **Lektion 4:** Delegation & Routing
5. **Lektion 5:** Memory & Context
6. **Lektion 6:** Reporting & Kommunikation
7. **Lektion 7:** Sicherheit-Grundlagen
8. **Lektion 8:** Error Handling
9. **Lektion 9:** Workspace & Files
10. **Lektion 10:** Scheduling & Cron

---

*Erstellt: 2026-04-08*
*Lösungen für OpenClaw Agent Grund-Training v1.0*
