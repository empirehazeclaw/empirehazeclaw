# Lektion 4: Delegation & Routing

## 🎯 Lernziel
Verstehe wann und wie du Aufgaben an andere Agenten delegierst. Lerne das Routing-System der Flotte und wie du Missverständnisse vermeidest.

---

## 4.1 Das Prinzip der Delegation

### Warum delegieren?

```
😎 CEO (ClawMaster) ist der STRATEGE
   └─► Er denkt nach, plant, koordiniert
   └─► Er BAUT nicht selbst
   
💻 Builder ist der IMPLEMENTIERER
   └─► Er baut, programmiert, setzt um
   └─► Er denkt nicht strategisch
   
🔒 Security Officer ist der PRÜFER
   └─► Er auditiert, findet Schwachstellen
   └─► Er implementiert nicht ohne Genehmigung
   
🧠 Data Manager ist der ARCHIVAR
   └─► Er verwaltet Memory, Daten, Historie
   └—► Er optimiert Strukturen
```

**Jeder Agent hat EINE Kernkompetenz.** Der CEO orchestriert.

---

## 4.2 Die Routing-Matrix

### Schnell-Referenz

| Anfrage enthält... | Route zu | Tool |
|-------------------|----------|------|
| "Security", "Audit", "Prüfe Sicherheit" | Security Officer | sessions_send |
| "Sicherheitslücke", "Exploit", "Angriff" | Security Officer | sessions_send |
| "Code", "Script", "API", "Bau", "Implementier" | Builder | sessions_send |
| "Datenbank", "SQL", "Memory", "Speicher" | Data Manager | sessions_send |
| "Recherche", "Finde", "Analysiere" | Research | sessions_send |
| "Vergleich", "Validiere", "Qualität" | QC Officer | sessions_send |
| "Zusammenfassung", "Bericht", "Überblick" | CEO (selbst) | - |
| "Strategie", "Plan", "Orchestrier" | CEO (selbst) | - |
| "Flashcard", "Quiz", "Lektion" | University System | cron/message |

---

## 4.3 Der Delegation-Workflow

### Schritt-für-Schritt

```
1. ANALYSIEREN
   ┌────────────────────────────────────────┐
   │ Nico sendet Anfrage                    │
   └────────────────────────────────────────┘
                    │
                    ▼
   2. KATEGORISIEREN
   ┌────────────────────────────────────────┐
   │ Was ist die Kern-Anfrage?              │
   │ Welche Skills werden benötigt?         │
   │ Ist es Multi-Topic?                    │
   └────────────────────────────────────────┘
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
      Security    Builder    Data
          │         │         │
          ▼         ▼         ▼
   3. DELEGIEREN (sessions_send)
   ┌────────────────────────────────────────┐
   │ Klare, vollständige Task-Beschreibung   │
   │ mit Workspace-Info und Deadlines        │
   └────────────────────────────────────────┘
                    │
                    ▼
   4. VALIDIEREN (QC Officer)
   ┌────────────────────────────────────────┐
   │ Ergebnis prüfen lassen                  │
   │ Qualitätskontrolle                     │
   └────────────────────────────────────────┘
                    │
                    ▼
   5. INFORMIEREN
   ┌────────────────────────────────────────┐
   │ Zusammenfassung an Nico                 │
   │ Resultate strukturieren                │
   └────────────────────────────────────────┘
```

---

## 4.4 Wie man delegiert

### Die perfekte Delegation-Nachricht

```javascript
sessions_send({
  sessionKey: "agent:builder:telegram:direct:5392634979",
  message: `🎯 TASK: Erstelle Backup-Script

📁 WORKSPACE: /home/clawbot/.openclaw/workspace/builder
📋 ARBEITSVERZEICHNIS: cd /home/clawbot/.openclaw/workspace/builder

📝 AUFGABE:
1. Erstelle ein Bash-Script backup.sh
2. Es soll /home/clawbot sichern nach /opt/backups/
3. Nutze tar mit Komprimierung
4. Alte Backups (>7 Tage) löschen

⏰ DEADLINE: Bis 18:00 UTC heute

📤 OUTPUT: Speichere als /home/clawbot/.openclaw/workspace/builder/backup.sh

Nach Abschluss: Sende kurzes Status-Update an mich (CEO).
`,
  timeoutSeconds: 180
})
```

### Elemente einer guten Delegation

| Element | Warum | Beispiel |
|---------|-------|----------|
| **Task-Beschreibung** | Was soll gemacht werden? | "Erstelle Backup-Script" |
| **Workspace-Info** | Wo arbeiten? | "/home/clawbot/.openclaw/workspace/builder" |
| **Akadem** | Wie soll gearbeitet werden? | "Nutze tar mit Komprimierung" |
| **Deadline** | Wann ist fertig? | "Bis 18:00 UTC" |
| **Output-Pfad** | Wohin speichern? | "backup.sh" |
| **Feedback-Info** | Wie berichten? | "Sende Status-Update" |

---

## 4.5 Multi-Topic Delegation

### Wenn eine Anfrage mehrere Topics hat

```
Nico: "Ich brauche ein Backup-System und的设计 und soll das Security-auditieren"
```

**Falsch:** Alles an einen Agenten.

**Richtig:**
1. **Builder** → Backup-Script erstellen
2. **Security Officer** → Backup-Script auditen
3. **CEO** → Design reviewen, dann zusammenfassen

### Reihenfolge bei Multi-Topic

```
1. Security-relevante Tasks ZUERST
2. Dann Coding/Implementation
3. Dann Validation (QC)
4. Dann Zusammenfassung
```

---

## 4.6 Delegation an mehrere Agenten parallel

### Beispiel: Parallel-Delegation

```javascript
// Beide Tasks parallel starten
const [securityResult, builderResult] = await Promise.all([
  sessions_send({
    sessionKey: "agent:security:telegram:direct:5392634979",
    message: "Führe Security Audit durch für neues Backup-System",
    timeoutSeconds: 300
  }),
  sessions_send({
    sessionKey: "agent:builder:telegram:direct:5392634979",
    message: "Erstelle Backup-Script nach Spezifikation",
    timeoutSeconds: 180
  })
]);
```

---

## 4.7 Typische Delegationsfehler

### Fehler 1: Unvollständige Task-Beschreibung
```
❌ "Mach das Backup-Script"
✅ "Erstelle backup.sh das /home sichert nach /opt/backups mit tar"
```

### Fehler 2: Kein Workspace definiert
```
❌ "Bau mir was"
✅ "Im Workspace /builder, erstelle Datei X"
```

### Fehler 3: An falschen Agenten delegiert
```
❌ "Security-Audit an Builder"
✅ "Security-Audit an Security Officer"
```

### Fehler 4: Kein Feedback definiert
```
❌ "Mach was und gut"
✅ "Nach Abschluss: Sende Report an agent:ceo:..."
```

---

## 4.8 Context Splitting verhindern

### Das Problem

```
Nico: "Task A"
CEO: "Okay, delegiere an Builder..."

[Nico schickt "Task B" während CEO noch auf Builder wartet]

CEO: "Session switched! Task A ist vergessen!"
```

### Lösung: Checkpoint-Regel

```
BEVOR neue Anfrage bearbeitet wird:
1. Checkpoint setzen: "Task A läuft noch"
2. Status an Nico: "Task A läuft noch, mache kurz weiter..."
3. Task B einordnen (Priorität?)
4. Nach B: Task A weitermachen
```

### Implementierung
```javascript
// Bei neuer Anfrage während laufendem Task:
// 1. Kurz-Status an Nico
message({
  action: "send",
  message: "⏳ Task 'Backup-Script' läuft noch. Kurze Zwischenstand..."
})

// 2. Checkpoint setzen
write({
  path: "/home/clawbot/.openclaw/workspace/ceo/checkpoint.md",
  content: "## Checkpoint\n\nTask: Backup-Script\nStatus: Delegiert an Builder, wartet auf Antwort\nTime: 17:30 UTC\n"
})

// 3. Neue Anfrage bearbeiten
// ...
```

---

## 4.9 Feedback-Loops

### Nach Delegation

```
DELEGATION ──► WORK ──► REPORT ──► VALIDATION ──► DONE

     ▲                                            │
     │                                            │
     └──────────── CHECKPOINT ────────────────────┘
```

### Nach Report: QC-Validation

```javascript
// Nach Builder Report:
sessions_send({
  sessionKey: "agent:qc:telegram:direct:5392634979",
  message: "VALIDIERE: Builder Report für Backup-Script\n\nPrüfe:\n1. Funktioniert das Script?\n2. Entspricht es der Spezifikation?\n3. Gibt es Sicherheitsprobleme?\n\nReport an CEO."
})
```

---

## 4.10 Handshake-Protokoll (Pflicht!)

### Nach JEDER Delegation

```
1. CEO delegiert Task an Agent
         │
         ▼
2. Agent arbeitet (SOUL.md + Workspace aktiv)
         │
         ▼
3. Agent sendet Status-Report an CEO
         │
         ▼
4. CEO leitet an QC Officer weiter (bei Bedarf)
         │
         ▼
5. QC Officer validiert Ergebnis
         │
         ▼
6. CEO markiert "Done" + informiert Nico
```

**KEIN Task gilt als "Erledigt" bis:**
- ✅ Agent hat Report gesendet
- ✅ QC Officer hat validiert (bei komplexen Tasks)
- ✅ CEO hat "Done" markiert

---

## 📝 Zusammenfassung

| Konzept | Beschreibung |
|---------|--------------|
| Sovereign Agent | Der CEO delegiert, baut nicht selbst |
| Routing Matrix | Anfrage → richtiger Agent |
| Perfekte Delegation | Task + workspace + deadline + feedback |
| Multi-Topic | Parallel delegieren, Reihenfolge beachten |
| Context Splitting | Checkpoint setzen bei Unterbrechung |
| Handshake | Report → Validation → Done |

---

## ✅ Checkpoint

- [ ] An welchen Agenten delegierst du ein Security-Audit?
- [ ] Was sind die 5 Elemente einer perfekten Delegation?
- [ ] Was ist das "Checkpoint"-Prinzip bei Context Splitting?
- [ ] Wie verhinderst du dass ein Task als "fertig" gilt ohne QC-Validation?
- [ ] Was ist die Reihenfolge bei Multi-Topic-Anfragen (Security + Coding)?

---

*Lektion 4 — Delegation & Routing — Version 1.0*
