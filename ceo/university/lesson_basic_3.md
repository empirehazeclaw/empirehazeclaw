# Lektion 3: Tool-Usage — Der Werkzeugkasten

## 🎯 Lernziel
Verstehe und beherrsche die wichtigsten Tools in OpenClaw. Nach dieser Lektion kannst du Dateien lesen/schreiben, Shell-Befehle ausführen, Agenten steuern und Zeitaufgaben verwalten.

---

## 3.1 exec — Shell-Befehle ausführen

### Grundsyntax
```javascript
exec({
  command: "ls -la /home/clawbot/.openclaw",
  timeout: 30
})
```

### Wichtige Parameter

| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `command` | string | Der Shell-Befehl |
| `timeout` | number | Timeout in Sekunden |
| `workdir` | string | Arbeitsverzeichnis |
| `background` | boolean | Im Hintergrund starten |
| `elevated` | boolean | Mit root-Rechten |

### Beispiele

```javascript
// Einfacher Befehl
exec({ command: "ls -la" })

// Mit Timeout
exec({ command: "find / -name '*.log'", timeout: 60 })

// Im Hintergrund
exec({ command: "python3 server.py", background: true })

// Mit Workdir
exec({ command: "npm run build", workdir: "/project" })

// Mit Umgebungsvariablen
exec({ 
  command: "echo $HOME",
  env: { HOME: "/tmp", NODE_ENV: "production" }
})
```

### Sicherheitshinweis
**NIEMALS** Benutzer-Eingaben direkt in exec-Befehle einfügen ohne Validierung!

```javascript
// ❌ UNSICHER
exec({ command: `ls ${userInput}` })

// ✅ SICHER
exec({ command: "ls", args: [userInput] }) // wenn möglich
// oder validiere vorher
const safeInput = userInput.replace(/[^a-zA-Z0-9.-]/g, "");
exec({ command: `ls ${safeInput}` })
```

---

## 3.2 read — Dateien lesen

### Grundsyntax
```javascript
read({ path: "/home/clawbot/.openclaw/config.json" })
read({ path: "relative/zur/workspace/datei.md" })
```

### Parameter

| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `path` | string | Pfad zur Datei |
| `offset` | number | Zeile zum Starten (1-indexed) |
| `limit` | number | Maximale Zeilenanzahl |

### Beispiele
```javascript
// Ganze Datei lesen
read({ path: "/home/clawbot/.openclaw/MEMORY.md" })

// Ab Zeile 100, max 50 Zeilen
read({ path: "large_file.txt", offset: 100, limit: 50 })

// Erste 20 Zeilen
read({ path: "log.txt", limit: 20 })
```

---

## 3.3 write — Dateien schreiben

### Grundsyntax
```javascript
write({
  path: "/home/clawbot/.openclaw/workspace/new_file.md",
  content: "# Hello World\n\nDies ist der Inhalt."
})
```

### Wichtige Features

1. **Überschreibt bestehende Dateien** — Vorsicht!
2. **Erstellt Elternverzeichnisse automatisch**
3. **Kein append-Modus** — erst lesen, dann überschreiben

### Beispiel: Bearbeiten mit read + write
```javascript
// 1. Lies bestehende Datei
const content = read({ path: "config.json" })

// 2. Modifiziere Inhalt (in Variable)
// content = content.replace(/old/, "new")

// 3. Schreibe zurück
write({ path: "config.json", content: newContent })
```

---

## 3.4 edit — Gezielte Textersetzung

### Grundsyntax
```javascript
edit({
  path: "file.txt",
  oldText: "alter text",
  newText: "neuer text"
})
```

### Wichtig: Exact Match
Der `oldText` muss **exakt** übereinstimmen (inkl. Whitespace, Newlines).

### Beispiele
```javascript
// Einfache Ersetzung
edit({
  path: "config.json",
  oldText: '"debug": false',
  newText: '"debug": true'
})

// Mit Newlines
edit({
  path: "README.md",
  oldText: "## Alte Überschrift\n\nText hier.",
  newText: "## Neue Überschrift\n\nNeuer Text."
})
```

### Mehrere Edits gleichzeitig
```javascript
edit({
  path: "config.json",
  edits: [
    { oldText: "wert1", newText: "neuer_wert1" },
    { oldText: "wert2", newText: "neuer_wert2" }
  ]
})
```

---

## 3.5 sessions_send — Agent-zu-Agent Kommunikation

### Grundsyntax
```javascript
sessions_send({
  sessionKey: "agent:builder:telegram:direct:5392634979",
  message: "Führe folgendes aus: ...",
  timeoutSeconds: 120
})
```

### Session-Keys der Flotte

| Agent | Session-Key |
|-------|-------------|
| CEO | `agent:ceo:telegram:direct:5392634979` |
| Builder | `agent:builder:telegram:direct:5392634979` |
| Security Officer | `agent:security:telegram:direct:5392634979` |
| Data Manager | `agent:data:telegram:direct:5392634979` |
| Research | `agent:research:telegram:direct:5392634979` |
| QC Officer | `agent:qc:telegram:direct:5392634979` |

### Timeout-Handling
```javascript
// Kurzer Timeout für schnelle Antworten
sessions_send({ sessionKey, message, timeoutSeconds: 30 })

// Langer Timeout für komplexe Tasks
sessions_send({ sessionKey, message, timeoutSeconds: 300 })
```

---

## 3.6 sessions_list — Aktive Sessions anzeigen

### Grundsyntax
```javascript
sessions_list({ kinds: ["agent"], messageLimit: 3 })
```

### Parameter

| Parameter | Beschreibung |
|-----------|--------------|
| `kinds` | Filter: "agent", "main", "acp" |
| `messageLimit` | Letzte N Nachrichten pro Session |
| `activeMinutes` | Nur Sessions aktiv in den letzten N Minuten |

### Rückgabe
```javascript
{
  sessions: [
    {
      key: "agent:builder:telegram:direct:5392634979",
      status: "running",
      updatedAt: 1775668548554,
      ...
    }
  ]
}
```

---

## 3.7 cron — Geplante Tasks

### Aktionen

| Aktion | Beschreibung |
|--------|--------------|
| `list` | Alle Cron-Jobs auflisten |
| `add` | Neuen Cron-Job erstellen |
| `update` | Bestehenden Job ändern |
| `remove` | Job löschen |
| `run` | Job sofort ausführen |
| `runs` | Run-History anzeigen |

### Job erstellen (add)
```javascript
cron({
  action: "add",
  job: {
    name: "Tägliches Backup",
    schedule: { kind: "cron", expr: "0 2 * * *" },
    sessionTarget: "isolated",
    payload: {
      kind: "agentTurn",
      message: "Führe Backup durch..."
    },
    delivery: { mode: "announce", channel: "telegram", to: "5392634979" }
  }
})
```

### Schedule-Typen

```javascript
// Cron-Ausdruck
{ kind: "cron", expr: "0 2 * * *" }           // Täglich 02:00
{ kind: "cron", expr: "0 9 * * 1-5" }         // Mo-Fr 09:00
{ kind: "cron", expr: "0 0 18 * * 0" }         // Sonntag 18:00

// Einmalig
{ kind: "at", at: "2026-04-15T10:00:00Z" }

// Intervall
{ kind: "every", everyMs: 3600000 }            // Alle Stunde
```

---

## 3.8 message — Nachrichten senden

### Telegram
```javascript
message({
  action: "send",
  channel: "telegram",
  target: "5392634979",
  message: "Hallo Nico! Status-Update..."
})
```

### Mit Buttons
```javascript
message({
  action: "send",
  channel: "telegram",
  target: "5392634979",
  message: "Was möchtest du tun?",
  buttons: [
    [{ text: "Status", callback_data: "status" }],
    [{ text: "Backup", callback_data: "backup" }]
  ]
})
```

---

## 3.9 subagents — Sub-Agenten verwalten

### Spawnen
```javascript
sessions_spawn({
  task: "Führe diese Analyse durch...",
  runtime: "subagent",
  mode: "run"           // oder "session"
})
```

### Auflisten
```javascript
subagents({ action: "list" })
```

### Killen
```javascript
subagents({ action: "kill", target: "subagent-session-key" })
```

---

## 3.10 memory_search — Gedächtnis durchsuchen

```javascript
memory_search({
  query: "Security Keys Rotation",
  maxResults: 5
})
```

---

## ⚠️ Sicherheitsregeln

1. **NIEMALS** Benutzer-Eingaben ungeprüft in exec
2. **NIEMALS** API-Keys in Code hardcodieren → Secrets nutzen
3. **IMMER** Least Privilege — nicht mehr Rechte als nötig
4. **Prüfe** Datei-Inhalte bevor du sie ausführst

---

## 📝 Zusammenfassung: Tool-Referenz

| Tool | Nutzen | Typische Verwendung |
|------|--------|---------------------|
| `exec` | Shell-Befehle | Dateien listen, Prozesse starten |
| `read` | Dateien lesen | Config lesen, Logs analysieren |
| `write` | Dateien schreiben | Reports erstellen, Config ändern |
| `edit` | Gezielt ändern | Einzelne Werte anpassen |
| `sessions_send` | Agent-Kommunikation | Delegation |
| `sessions_list` | Debugging | Session-Status prüfen |
| `cron` | Automation | Geplante Tasks |
| `message` | Telegram/Discord | Nico informieren |
| `subagents` | Parallelarbeit | Nebenläufige Tasks |

---

## ✅ Checkpoint

- [ ] Wie führst du einen Shell-Befehl mit Timeout aus?
- [ ] Was ist der Unterschied zwischen read und write?
- [ ] Wie sendest du eine Nachricht an den Builder Agent?
- [ ] Wie erstellst du einen Cron-Job der täglich um 9 Uhr läuft?
- [ ] Was musst du beachten bevor du Benutzer-Eingaben in exec verwendest?

---

*Lektion 3 — Tool-Usage — Version 1.0*
