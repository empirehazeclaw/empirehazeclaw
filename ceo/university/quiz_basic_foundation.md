# 🏛️ OpenClaw Agent Grund-Training — Abschlussprüfung

## Prüfung für alle Agenten — Version 1.0

**Maximale Punktzahl:** 50 Punkte
**Bestehensgrenze:** 99% = **49 von 50 Punkten** ⚠️
**Erlaubte Hilfsmittel:** None (keine externen Quellen)
**Zeit:** Flexibel (kein Limit)

---

## ⚠️ WICHTIG: Diese Prüfung ist NICHT trivial!

Diese Prüfung testet **tiefes Verständnis**, nicht auswendig lernen.
Bei 99% Bestehensgrenze ist **jede Frage kritisch**.

**Musterantworten sind am Ende des Dokuments.**

---

## TEIL A: Multiple Choice (20 Fragen — 20 Punkte)

### Frage 1 (1 Punkt)
Der OpenClaw Gateway läuft standardmäßig auf welchem Port?

a) 8080
b) 18789
c) 3000
d) 443

<details>
<summary>Lösung</summary>
**Antwort: b) 18789** — Der Gateway-Standardport ist 18789.
</details>

---

### Frage 2 (1 Punkt)
Welcher Session-Typ wird für **einmalige, isolierte Tasks** verwendet?

a) `main`
b) `isolated`
c) `persistent`
d) `worker`

<details>
<summary>Lösung</summary>
**Antwort: b) `isolated`** — Isolierte Sessions sind für einzelne Tasks gedacht und werden nach Abschluss beendet.
</details>

---

### Frage 3 (1 Punkt)
Ein Agent sendet eine Nachricht an einen anderen Agenten. Welches Tool wird verwendet?

a) `message_send`
b) `agent_message`
c) `sessions_send`
d) `send_to_agent`

<details>
<summary>Lösung</summary>
**Antwort: c) `sessions_send`** — Das ist das korrekte Tool für Agent-zu-Agent-Kommunikation.
</details>

---

### Frage 4 (1 Punkt)
Was ist der Hauptzweck der SOUL.md?

a) Technische Konfiguration speichern
b) Identity, Persona und Workflow definieren
c) Memory-Daten speichern
d) Cron-Jobs konfigurieren

<details>
<summary>Lösung</summary>
**Antwort: b)** — SOUL.md definiert wer der Agent ist, wie er arbeitet und seine Kernprinzipien.
</details>

---

### Frage 5 (1 Punkt)
Die MEMORY.md sollte wie groß sein (Maximum)?

a) Maximal 100KB
b) Maximal 500KB
c) Maximal 5MB
d) Unbegrenzt

<details>
<summary>Lösung</summary>
**Antwort: b) Maximal 500KB** — MEMORY.md sollte komprimiert sein und maximal einige KB, nicht Hunderte.
</details>

---

### Frage 6 (1 Punkt)
Welches Tool wird für **semantische Suche** im Memory verwendet?

a) `grep`
b) `find`
c) `memory_search`
d) `search_memory`

<details>
<summary>Lösung</summary>
**Antwort: c) `memory_search`** — Das offizielle Tool für semantische Memory-Suche.
</details>

---

### Frage 7 (1 Punkt)
Was ist Context Splitting?

a) Ein Fehler beim Kopieren von Dateien
b) Verlust von Kontext wenn das Kontextfenster voll ist
c) Ein Sicherheitsproblem bei Commands
d) Ein Bug im Gateway

<details>
<summary>Lösung</summary>
**Antwort: b)** — Context Splitting passiert wenn das Kontext-Fenster voll ist und älterer Kontext entfernt wird.
</details>

---

### Frage 8 (1 Punkt)
Ein CEO-Agent sieht eine Anfrage für Security-Audit. Wohin routet er?

a) Direkt an sich selbst
b) An den Builder
c) An den Security Officer
d) An Research

<details>
<summary>Lösung</summary>
**Antwort: c) An den Security Officer** — Security-Themen gehen IMMER zum Security Officer.
</details>

---

### Frage 9 (1 Punkt)
Was bedeutet Least Privilege?

a) Mitarbeiter sollten minimal bezahlt werden
b) Jeder hat nur die Rechte die er BRAUCHT, nicht mehr
c) privilegierte Befehle müssen als erstes ausgeführt werden
d) Linux hat Vorrang

<details>
<summary>Lösung</summary>
**Antwort: b)** — Least Privilege bedeutet maximal eingeschränkte Rechte — nur das absolute Minimum das nötig ist.
</details>

---

### Frage 10 (1 Punkt)
Welcher Befehl setzt die korrekten Rechte für eine Config-Datei?

a) `chmod 777 openclaw.json`
b) `chmod 644 openclaw.json`
c) `chmod 600 openclaw.json`
d) `chmod 111 openclaw.json`

<details>
<summary>Lösung</summary>
**Antwort: c) chmod 600** — 600 bedeutet nur Owner kann lesen/schreiben — sicher für Config-Files.
</details>

---

### Frage 11 (1 Punkt)
Was ist das richtige Format für einen Session-Key eines Builder-Agenten auf Telegram?

a) `builder:telegram:5392634979`
b) `agent:builder:telegram:direct:5392634979`
c) `telegram:builder:5392634979`
d) `builder-agent-telegram-direct`

<details>
<summary>Lösung</summary>
**Antwort: b)** — Format: `agent:{agentId}:{channel}:{direction}:{chatId}`
</details>

---

### Frage 12 (1 Punkt)
Eine Datei wird mit `write` überschrieben. Was passiert mit dem ursprünglichen Inhalt?

a) Er wird archiviert
b) Er wird Teil eines Backups
c) Er wird vollständig gelöscht und ersetzt
d) Er wird in memory/ verschoben

<details>
<summary>Lösung</summary>
**Antwort: c)** — write überschreibt die gesamte Datei — alter Inhalt ist weg.
</details>

---

### Frage 13 (1 Punkt)
Der Cron-Ausdruck `0 9 * * 1-5` bedeutet:

a) Jeden Tag um 09:00
b) Mo-Fr um 09:00
c) Jeden Monat um 09:00
d) Alle 9 Stunden

<details>
<summary>Lösung</summary>
**Antwort: b) Mo-Fr um 09:00** — 1-5 = Monday to Friday.
</details>

---

### Frage 14 (1 Punkt)
Welches Delivery-Mode wird für **direkte Telegram-Nachrichten** an Nico verwendet?

a) `direct`
b) `push`
c) `announce`
d) `telegram`

<details>
<summary>Lösung</summary>
**Antwort: c) `announce`** — announce mit channel: "telegram" und to: "5392634979".
</details>

---

### Frage 15 (1 Punkt)
Was ist der richtige Weg um einen Checkpoint zu setzen?

a) Per E-Mail an Nico senden
b) In einer Checkpoint-Datei im Workspace speichern
c) Als Discord-Nachricht senden
d) Nur im Kurzzeitgedächtnis behalten

<details>
<summary>Lösung</summary>
**Antwort: b)** — Checkpoints werden als Datei im Workspace gespeichert für Recovery.
</details>

---

### Frage 16 (1 Punkt)
Was ist **KEIN** gültiger Status in task_report.json?

a) `done`
b) `in_progress`
c) `thinking`
d) `error`

<details>
<summary>Lösung</summary>
**Antwort: c) `thinking`** — Gültige Status sind: done, in_progress, warning, error, blocked.
</details>

---

### Frage 17 (1 Punkt)
Welche Aktion führt der QC Officer laut dem Handshake-Protokoll aus?

a) Erstellt Code
b) Validiert Ergebnisse anderer Agenten
c) Sendet Nachrichten an Nico
d) Verwaltet Cron-Jobs

<details>
<summary>Lösung</summary>
**Antwort: b)** — QC Officer validiert Ergebnisse bevor sie als "done" gelten.
</details>

---

### Frage 18 (1 Punkt)
Was ist bei exponention Backoff der Zweck der steigenden Wartezeiten?

a) Energie sparen
b) Race Conditions und Server-Überlastung vermeiden
c) Die Batterie schonen
d) Mehr Aufgaben zu erledigen

<details>
<summary>Lösung</summary>
**Antwort: b)** — Exponential Backoff verhindert dass wiederholte Retries ein ausgefallenes System überlasten.
</details>

---

### Frage 19 (1 Punkt)
Wann sollte man **NICHT** selbst reparieren, sondern eskalieren?

a) Bei kleinen Fehlern
b) Nach 3 Retry-Versuchen oder 10 Minuten Debugging ohne Lösung
c) Bei Dateioperationen
d) Bei geplanten Crons

<details>
<summary>Lösung</summary>
**Antwort: b)** — Escalation nach 3 Retries oder 10 Minuten wenn das Problem nicht lösbar ist.
</details>

---

### Frage 20 (1 Punkt)
Welche Datei enthält das agent-spezifische Gedächtnis eines Agents?

a) `~/.openclaw/workspace/{agent}/MEMORY.md`
b) `~/.openclaw/agents/{agent}/memory/`
c) `~/.openclaw/memory/agent_{agent}.md`
d) `~/.openclaw/{agent}/memory.txt`

<details>
<summary>Lösung</summary>
**Antwort: b)** — agents/{agent}/memory/ enthält das agent-spezifische Memory mit notes/, decisions/, learnings/.
</details>

---

## TEIL B: True/False (15 Fragen — 15 Punkte)

### Frage 21 (1 Punkt)
Die SOUL.md ersetzt die openclaw.json vollständig.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: b) Falsch** — SOUL.md definiert Identity/Workflow, openclaw.json definiert technische Config.
</details>

---

### Frage 22 (1 Punkt)
Ein CEO-Agent sollte NIEMALS direkt Code schreiben sondern immer an den Builder delegieren.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: a) Wahr** — Sovereign-Prinzip: CEO orchestriert, Builder implementiert.
</details>

---

### Frage 23 (1 Punkt)
API-Keys dürfen temporär im Code sein solange sie funktionieren.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: b) Falsch** — Secrets gehören IMMER in Environment/Secrets, NIEMALS hardcoded im Code.
</details>

---

### Frage 24 (1 Punkt)
Der Standardport des Gateways ist 18789 und kann in der Config geändert werden.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: a) Wahr** — Der Port ist konfigurierbar in openclaw.json unter gateway.port.
</details>

---

### Frage 25 (1 Punkt)
Ein Timeout von 0 bedeutet "unendlich warten".

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: b) Falsch** — Timeout 0 bedeutet kein Timeout = **NIEMALS** setzen! Timeouts sind essentiell.
</details>

---

### Frage 26 (1 Punkt)
Memory-Archive enthalten historische Daten die aus MEMORY.md komprimiert wurden.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: a) Wahr** — Archive in memory/archive/ enthalten historische Daten.
</details>

---

### Frage 27 (1 Punkt)
Ein Checkpoint kann ein laufendes Projekt komplett ersetzen.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: b) Falsch** — Checkpoint ist eine Sicherung des Status, kein Ersatz für eigentliches Arbeiten.
</details>

---

### Frage 28 (1 Punkt)
Command Injection ist möglich wenn Benutzer-Eingaben ungeprüft in exec-Befehle eingefügt werden.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: a) Wahr** — "'; rm -rf /" ist ein klassisches Injection-Beispiel.
</details>

---

### Frage 29 (1 Punkt)
Der Circuit Breaker verhindert dass ein einzelner Service-Ausfall das gesamte System blockiert.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: a) Wahr** — Circuit Breaker öffnet bei zu vielen Failures und verhindert Kaskaden-Ausfälle.
</details>

---

### Frage 30 (1 Punkt)
Graceful Degradation bedeutet dass das System bei Teil-Ausfällen komplett stoppt.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: b) Falsch** — Graceful Degradation bedeutet Fallback nutzen statt Total-Stop.
</details>

---

### Frage 31 (1 Punkt)
Der Q C Officer kommt VOR dem Informieren von Nico in der Workflow-Reihenfolge.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: a) Wahr** — Workflow: Delegation → Work → Report → QC Validation → Inform Nico.
</details>

---

### Frage 32 (1 Punkt)
Alle 10 Agenten-Workspaces liegen unter ~/.openclaw/workspace/.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: a) Wahr** — Workspace-Struktur: ~/.openclaw/workspace/{ceo,builder,security,data,research,qc}/
</details>

---

### Frage 33 (1 Punkt)
Die CIA-Triade steht für Confidentiality, Integrity, Availability.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: a) Wahr** — Die CIA-Triade sind die drei Grundpfeiler der Informationssicherheit.
</details>

---

### Frage 34 (1 Punkt)
RBAC bedeutet "Role-Based Access Control" und definiert wer was darf.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: a) Wahr** — RBAC ist das Zugriffskontrollsystem das Agent-Rollen zu Permissions mappt.
</details>

---

### Frage 35 (1 Punkt)
Ein Cron-Job mit `schedule: { kind: "every", everyMs: 500 }` ist akzeptabel.

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: b) Falsch** — 500ms ist viel zu aggressiv. Minimum sollte mindestens 1 Minute (60000ms) sein.
</details>

---

## TEIL C: Praxisfragen (10 Fragen — 10 Punkte)

### Frage 36 (1 Punkt)
Nico schickt: "Mach ein Backup von /home und prüfe die Security".

Was ist der Routing-Fehler hier und wie routingst du korrekt?

<details>
<summary>Lösung</summary>
**Problem:** "Mach Backup" (Coding) UND "prüfe Security" (Security) — beides an einen Agenten.

**Korrektes Routing:**
1. **ZUERST** Security: Security Officer → Security Audit für Backup-Script
2. **DANN** Coding: Builder → Backup-Script erstellen (nach Security-OK)
3. Alternativ: Parallel — Security Officer auditiert während Builder baut

Der CEO sollte NICHT selbst coden oder selbst Security machen.
</details>

---

### Frage 37 (1 Punkt)
Du schreibst ein Script das Benutzer-Input verarbeitet. Der User gibt einen Dateinamen ein. Erkläre kurz wie du Input Validation korrekt implementierst.

<details>
<summary>Lösung</summary>
```python
# 1. Whitelist definieren
ALLOWED_DIRS = ["/workspace/projects", "/workspace/data"]

# 2. Input nehmen
user_input = request.params["filename"]

# 3. Validieren
if user_input.startswith("/"):
    # Absolute Pfade verbieten oder gegen Whitelist prüfen
    if not any(user_input.startswith(d) for d in ALLOWED_DIRS):
        raise ValueError("Pfad nicht erlaubt")

# 4. Sanitisieren (Sonderzeichen entfernen)
safe_name = re.sub(r"[^a-zA-Z0-9._-]", "", user_input)

# 5. Erst jetzt nutzen
exec(f"cat {safe_name}")
```
</details>

---

### Frage 38 (1 Punkt)
Was ist der Unterschied zwischen `read` und `memory_search`? Wann nutzt du welches?

<details>
<summary>Lösung</summary>
| | `read` | `memory_search` |
|---|---|---|
| **Nutzen** | Ganze Datei oder Snippet lesen | Semantisch im Memory suchen |
| **Input** | Pfad + Zeilen | Query-String |
| **Output** | Datei-Inhalt | Snippets mit Quelle |
| **Nutzen wenn** | Du weißt welche Datei | Du suchst nach Info |

**Beispiel:**
- "Lies SOUL.md" → `read({path: "SOUL.md"})`
- "Was haben wir letztens über Backups entschieden?" → `memory_search({query: "Backup Entscheidung"})`
</details>

---

### Frage 39 (1 Punkt)
Erkläre das Circuit Breaker Pattern in eigenen Worten. Wie funktioniert es?

<details>
<summary>Lösung</summary>
**Circuit Breaker verhindert Kaskaden-Ausfälle:**

1. **CLOSED (Normal):** Requests gehen durch
2. Bei **X Failures** → Springt auf **OPEN**
3. **OPEN:** Requests werden sofort abgelehnt ("Circuit ist offen")
4. Nach **Timeout** → **HALF-OPEN** (Test-Modus)
5. HALF-OPEN: Nächster Request wird durchgelassen
   - **Success** → CLOSED (zurück zu Normal)
   - **Fail** → OPEN (wieder zu)

**Analogie:** Wie ein elektrischer Sicherungskasten — bei Überlastung springt die Sicherung raus um Schlimmeres zu verhindern.
</details>

---

### Frage 40 (1 Punkt)
Du bist Builder-Agent und Nico gibt dir den Auftrag: "Erstelle ein Script das alle Log-Files löscht". Was musst du zuerst tun und warum?

<details>
<summary>Lösung</summary>
**Ich muss zuerst zum Security Officer routen!**

Grund: "Alle Log-Files löschen" ist eine **HIGH-RISIKO** Aktion:
- Logs können forensisch wichtig sein
- Löschung könnte Security-Events verbergen
- Kann Compliance-verletzen

**Korrekter Workflow:**
1. Builder erkennt: Das ist Hochrisiko
2. Builder fragt: "Approval für Bulk-Log-Delete?"
3. Security Officer oder Nico genehmigt
4. ERST DANN implementieren

**KEIN** Builder sollte Hochrisiko-Aktionen ohne Approval machen!
</details>

---

### Frage 41 (1 Punkt)
Erkläre das Handshake-Protokoll mit deinen eigenen Worten. Was passiert nach jeder Delegation?

<details>
<summary>Lösung</summary>
```
DELEGATION → WORK → REPORT → QC → DONE

1. CEO delegiert Task an Agent
2. Agent arbeitet in seiner Session mit eigener SOUL
3. Agent sendet Ergebnis-Report an CEO
4. CEO leitet an QC Officer zur Validierung
5. QC Officer prüft: Funktioniert es? Ist es sicher?
6. QC sendet Validierungs-Report an CEO
7. CEO markiert "Done" und informiert Nico

KEIN Task gilt als "Erledigt" bis:
- ✅ Report gesendet
- ✅ QC validiert (bei komplexen Tasks)
- ✅ CEO "Done" markiert
```
</details>

---

### Frage 42 (1 Punkt)
Du bist CEO und Nico fragt: "Was läuft gerade bei der Flotte?" Du hast aber schon 15 Minuten nichts mehr gehört. Wie gehst du vor?

<details>
<summary>Lösung</summary>
1. **Heartbeat senden** an alle aktiven Agenten
2. **sessions_list** nutzen um Session-Status zu prüfen
3. **Checkpoints** prüfen in relevanten Workspaces
4. **Status-Report** an Nico mit:
   - Grüner Status wenn alles ok
   - Gelb wenn Aufmerksamkeit nötig
   - Rot wenn Probleme (und QC/escalation gestartet)

**Wichtig:** Ich sollte NIEMALS raten. Lieber kurze Status-Abfrage als falsche Annahme.
</details>

---

### Frage 43 (1 Punkt)
Was ist der Unterschied zwischen `edit` und `write`? Wann nutzt du welches?

<details>
<summary>Lösung</summary>
| | `write` | `edit` |
|---|---|---|
| **Funktion** | Überschreibt gesamte Datei | Ersetzt spezifischen Text |
| **oldText nötig** | Nein | Ja, muss exakt matchen |
| **Risk** | Kann alles löschen | Gezielte Änderung |
| **Nutzung** | Neue Dateien, Replace | Kleinigkeiten ändern |

**Beispiel:**
- Neue Config erstellen → `write`
- `"debug": false` zu `"debug": true` → `edit`
- Neue Zeile in bestehender Datei → `edit`

**Faustregel:** Wenn Datei existiert und du nur eine kleine Änderung machst → `edit`. Alles andere → `read` erst, dann `write`.
</details>

---

### Frage 44 (1 Punkt)
Ein exec-Befehl liefert einen Permission-Denied-Fehler. Nenne 3 mögliche Ursachen und wie du sie diagnostizierst.

<details>
<summary>Lösung</summary>
**3 mögliche Ursachen:**

1. **Falsche Dateirechte**
   - Diagnose: `ls -la /pfad/zur/datei`
   - Lösung: `chmod 644 datei` (oder 600 für Configs)

2. **Prozess läuft als falscher User**
   - Diagnose: `whoami` und `id`
   - Lösung: Als richtiger User starten oder sudo

3. **SELinux/AppArmor blockiert**
   - Diagnose: `getenforce` oder Logs prüfen
   - Lösung: Policy anpassen oder deaktivieren (mit Bedacht!)

**Allgemein:**
```bash
# Wer bin ich?
whoami

# Was darf ich?
id

# Was darf die Datei?
ls -la /pfad

# Ist der Port belegt?
ss -tlnp | grep port
```
</details>

---

### Frage 45 (1 Punkt)
Du arbeitest an einem komplexen Task. Plötzlich kommt Nico mit einer dringenden Anfrage. Deine aktuelle Arbeit ist noch nicht fertig. Wie handelst du das?

<details>
<summary>Lösung</summary>
**Checkpoint-Regel anwenden:**

1. **NICHT** den laufenden Task abbrechen
2. **NICHT** die neue Anfrage ignorieren
3. **Wohlüberlegt priorisieren:**

```
a) Checkpoint schreiben:
   - Was läuft gerade?
   - Letzter Stand?
   - Nächste Schritte?
   - Erwartete Zeit bis Fertig?

b) Nico kurz informieren:
   "⏳ Task X läuft noch (80%), mache kurz weiter...
   Wie dringend ist die neue Anfrage?"
   
c) Entscheiden:
   - Dringend → Task unterbrechen, Nico's Anfrage
   - Kann warten → Task zu Ende bringen

d) Nach Task-Fertigstellung:
   - Checkpoint lesen
   - Bei Nico's Anfrage weitermachen
```
</details>

---

## TEIL D: Troubleshooting (5 Fragen — 5 Punkte)

### Frage 46 (1 Punkt)
**Problem:** `sessions_send` zu einem Agenten gibt Timeout zurück, aber der Agent existiert.

Nenne 3 mögliche Ursachen und für jede eine Lösung.

<details>
<summary>Lösung</summary>
**1. Agent-Session ist "failed" oder gestorben**
- Diagnose: `sessions_list` → Status prüfen
- Lösung: Agent-Session muss neu gestartet werden (Gateway-Restart oder warten auf Auto-Recovery)

**2. Model-Authentication fehlgeschlagen**
- Diagnose: Logs prüfen, Model-Config prüfen
- Lösung: API-Key prüfen, Model wechseln, openclaw.json validieren

**3. Agent ist mit anderem Task beschäftigt**
- Diagnose: Session-Status "busy" prüfen
- Lösung: Längeren Timeout setzen oder später erneut versuchen

**4. Netzwerk-Problem (bei Remote-Modellen)**
- Diagnose: `curl` zum API-Endpunkt
- Lösung: Netzwerk-Probleme beheben, Retry mit Backoff
</details>

---

### Frage 47 (1 Punkt)
**Problem:** Der Gateway startet nicht. `openclaw gateway status` zeigt "not running", aber `ss -tlnp | grep 18789` zeigt nichts.

Erkläre dein Debugging-Vorgehen Schritt für Schritt.

<details>
<summary>Lösung</summary>
```bash
# Schritt 1: Gateway-Status prüfen
openclaw gateway status

# Schritt 2: Logs analysieren
cat ~/.openclaw/logs/gateway.log
# oder
cat /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log

# Schritt 3: Config validieren
openclaw doctor --check

# Schritt 4: Config reparieren falls nötig
openclaw doctor --fix

# Schritt 5: Port-Probleme prüfen
ss -tlnp | grep 18789
netstat -tlnp | grep 18789

# Schritt 6: Gateway starten
openclaw gateway start

# Schritt 7: Erneut prüfen
openclaw gateway status

# Schritt 8: Falls immer noch Problem → Node.js Version prüfen
node --version
```
</details>

---

### Frage 48 (1 Punkt)
**Problem:** MEMORY.md ist 800KB groß. Das System wird langsam beim Durchsuchen.

Was ist das Problem und wie behebst du es?

<details>
<summary>Lösung</summary>
**Problem:** MEMORY.md sollte maximal 500KB sein. 800KB ist zu groß.

**Behebung:**
1. **Komprimieren:**
   - Archiviere alte/thematische Abschnitte
   - Behalte nur das Wesentliche
   - Verschiebe Details nach memory/archive/

2. **Strukturierung:**
   ```
   ~/.openclaw/memory/
   ├── MEMORY.md              # Max 500KB, nur aktuelle Facts
   └── archive/
       ├── 2026-04-backup-decisions.md
       ├── 2026-03-project-x.md
       └── ...
   ```

3. **Automatisierung:**
   - Data Manager Cron sollte MEMORY.md automatisch prüfen
   - Bei >500KB → Automatisch komprimieren oder Alert

4. **Temporary Fix:**
   - Manuell older Inhalte nach archive/ verschieben
   - MEMORY.md neu schreiben mit nur aktuellem Stand
</details>

---

### Frage 49 (1 Punkt)
**Problem:** Ein Cron-Job wurde erstellt (`cron add`), aber er läuft nicht zur erwarteten Zeit.

Nenne mögliche Ursachen und wie du das debugst.

<details>
<summary>Lösung</summary>
**Mögliche Ursachen:**

1. **Job ist disabled**
   - Debug: `cron({action: "list", includeDisabled: true})`
   - Lösung: `cron({action: "update", enabled: true})`

2. **Zeitzone falsch**
   - Debug: Prüfe `tz` in Cron-Expression
   - Lösung: `tz: "Europe/Berlin"` setzen wenn in Berlin

3. **Schedule-Expression falsch**
   - Debug: `cron({action: "runs", jobId: "..."})`
   - Lösung: Expression prüfen (z.B. `0 9 * * *` = täglich 09:00)

4. **Gateway läuft nicht**
   - Debug: `openclaw gateway status`
   - Lösung: `openclaw gateway start`

5. **Payload fehlerhaft**
   - Debug: Job-Details prüfen
   - Lösung: Payload korrigieren
</details>

---

### Frage 50 (1 Punkt)
**Problem:** Ein Agent antwortetwidersprüchlich auf die gleiche Frage (einmal ja, einmal nein).

Erkläre was wahrscheinlich passiert und wie du es behebst.

<details>
<summary>Lösung</summary>
**Wahrscheinliche Ursache: Context Splitting**

Der Agent hat nicht mehr den vollständigen Kontext:
- Kontext-Fenster ist voll
- Ältere Infos wurden entfernt
- Agent "weiß" nicht mehr was vorher gesagt wurde

**Behebung:**

1. **Sofort-Maßnahme:**
   - Agent anweisen: "Lies Checkpoint falls vorhanden"
   - memory_search nutzen um vergangene Fakten zu holen
   - Mit Citations arbeiten: "Laut MEMORY.md#45..."

2. **Langfristig:**
   - Checkpoints bei langen Tasks schreiben
   - MEMORY.md komprimieren (weniger Context-Verbrauch)
   - Wichtige Fakten in Dateien speichern (nicht nur im Chat)

3. **Prävention:**
   - Bei wichtigen Entscheidungen: Immer in MEMORY.md dokumentieren
   - "Recall-Pipeline" nutzen: memory_search → memory_get → Fakten mit Quelle
   - Nie annehmen dass Agent sich erinnert — immer explizit liefern
</details>

---

## 📊 Auswertung

| Teil | Fragen | Punkte |
|------|--------|--------|
| A: Multiple Choice | 20 | 20 |
| B: True/False | 15 | 15 |
| C: Praxisfragen | 10 | 10 |
| D: Troubleshooting | 5 | 5 |
| **Gesamt** | **50** | **50** |

---

## 🎯 Bestehensgrenze

| Punkte | Ergebnis |
|--------|----------|
| **49-50** | ✅ **BESTANDEN** — 99%+ |
| 48 | ❌ **NICHT BESTANDEN** — 96% |
| <48 | ❌ **NICHT BESTANDEN** |

---

⚠️ **Bei 99% Bestehensgrenze ist jede Frage kritisch!**

---

*Prüfung erstellt: 2026-04-08*
*Für OpenClaw Agent Grund-Training v1.0*
