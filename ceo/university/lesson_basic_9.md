# Lektion 9: Workspace & File Operations

## 🎯 Lernziel
Verstehe die Workspace-Struktur, Datei-Operationen und Pfad-Handling. Jeder Agent arbeitet im Workspace — korrektes Datei-Management ist essentiell.

---

## 9.1 Workspace-Architektur

### Hauptverzeichnis
```
~/.openclaw/workspace/
├── ceo/                  # CEO Workspace
│   ├── SOUL.md           # CEO Identität
│   ├── IDENTITY.md       # Persönliche Details
│   ├── HEARTBEAT.md      # Aktive Tasks
│   ├── MEMORY.md         # (optional)
│   ├── memory/            # CEO Memory
│   │   ├── notes/
│   │   ├── decisions/
│   │   └── learnings/
│   └── work/             # Aktuelle Tasks
├── builder/              # Builder Workspace
├── security/             # Security Officer Workspace
├── data/                 # Data Manager Workspace
├── research/             # Research Workspace
└── qc/                  # QC Officer Workspace
```

### Agent-spezifische Verzeichnisse
```
~/.openclaw/agents/
├── ceo/
│   ├── agent/           # Agent-Config
│   │   └── models.json
│   └── sessions/        # Session-History
├── builder/
│   └── ...
└── ...
```

---

## 9.2 Pfade verstehen

### Absolute vs. Relative Pfade

```javascript
// Absolute Pfade — komplett von Root
read({ path: "/home/clawbot/.openclaw/MEMORY.md" })
read({ path: "/home/clawbot/.openclaw/workspace/ceo/SOUL.md" })

// Relative Pfade — vom aktuellen Workdir
read({ path: "SOUL.md" })  // Im Workdir /workspace/ceo
read({ path: "../builder/test.py" }) // Eine Ebene hoch
```

### Wichtig: Workdir

```
Default Workdir: /home/clawbot/.openclaw/workspace/ceo/

read({ path: "test.txt" })
// Liest: /home/clawbot/.openclaw/workspace/ceo/test.txt

read({ path: "../security/SOUL.md" })
// Liest: /home/clawbot/.openclaw/workspace/security/SOUL.md
```

---

## 9.3 Dateien Lesen

### Grundlagen

```javascript
// Vollständige Datei
read({ path: "/home/clawbot/.openclaw/workspace/ceo/SOUL.md" })

// Mit Zeilen-Limit (erste 50 Zeilen)
read({ path: "large_file.txt", limit: 50 })

// Ab bestimmter Zeile
read({ path: "log.txt", offset: 100, limit: 20 })
```

### Dateien mit Image-Unterstützung
```javascript
// Bilder werden als Attachment angezeigt
read({ path: "diagram.png" })
read({ path: "screenshot.jpg" })
```

---

## 9.4 Dateien Schreiben

### write — Vollständiges Überschreiben

```javascript
write({
  path: "/home/clawbot/.openclaw/workspace/ceo/test.md",
  content: "# Test\n\nHallo Welt!"
})
```

**Wichtig:** write überschreibt die gesamte Datei!

### write mit Parent-Directories
```javascript
// Erstellt fehlende Verzeichnisse automatisch
write({
  path: "/home/clawbot/.openclaw/workspace/ceo/newdir/newfile.md",
  content: "..."
})
// Erstellt: workspace/ceo/newdir/
```

---

## 9.5 Dateien Editieren

### edit — Gezielte Änderung

```javascript
edit({
  path: "config.json",
  oldText: '"debug": false',
  newText: '"debug": true'
})
```

### oldText muss EXAKT matchen

```javascript
// ❌ FALSCH — Whitespace unterschiedlich
edit({
  path: "file.txt",
  oldText: "text",
  newText: "newtext"
})

// ✅ RICHTIG
edit({
  path: "file.txt",
  oldText: "alter text",  // Exakt wie im Original
  newText: "neuer text"
})
```

### Mehrere Edits gleichzeitig

```javascript
edit({
  path: "config.json",
  edits: [
    { oldText: '"key1": "old"', newText: '"key1": "new"' },
    { oldText: '"key2": "old"', newText: '"key2": "new"' }
  ]
})
```

---

## 9.6 exec — Datei-Operationen

### Shell-Befehle für Files

```bash
# Listen
ls -la /workspace/ceo
ls -lt /workspace/*  # Nach Zeit sortiert

# Lesen
cat file.txt
head -20 file.txt
tail -100 file.txt

# Schreiben
echo "content" > file.txt
cat > file.txt << 'EOF'
multiline
content
EOF

# Kopieren
cp source.txt backup.txt
cp -r dir/ backup/

# Verschieben
mv old.txt new.txt

# Löschen (VORSICHT!)
rm file.txt
rm -rf directory/  # Rekursiv + force

# Verzeichnis erstellen
mkdir -p newdir/subdir

# Größe prüfen
du -sh /workspace/*
```

---

## 9.7 Dateitypen

| Typ | Erkennung | Tools |
|-----|-----------|-------|
| `.txt` | Klartext | read, cat |
| `.md` | Markdown | read, write |
| `.json` | JSON | read, write, jq |
| `.py` | Python | read, exec mit python3 |
| `.sh` | Bash | read, exec mit bash |
| `.log` | Log-Dateien | tail, grep |
| `.db`, `.sqlite` | Datenbank | sqlite3 CLI |

---

## 9.8 Backups

### Wichtige Dateien sichern

```
WAS SICHERN:
✅ ~/.openclaw/openclaw.json      (Config)
✅ ~/.openclaw/workspace/         (Workspaces)
✅ ~/.openclaw/agents/            (Agent-Configs)
✅ ~/.openclaw/memory/            (Memory)
✅ ~/.openclaw/secrets/           (Secrets)

WAS NICHT:
❌ ~/.openclaw/logs/              (Logs, nicht kritisch)
❌ /tmp/                          (Temporär)
```

### Backup-Script erstellen

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/openclaw"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Config sichern
tar -czf $BACKUP_DIR/config_$DATE.tar.gz ~/.openclaw/openclaw.json

# Workspaces sichern
tar -czf $BACKUP_DIR/workspaces_$DATE.tar.gz ~/.openclaw/workspace/

# Alte Backups löschen (>7 Tage)
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup $DATE fertig"
```

---

## 9.9 Dateirechte

### Unix-Dateirechte

```
rwx rwx rwx
│   │   │
│   │   └── Andere
│   └───── Gruppe
└──────── Owner

r = 4 (Lesen)
w = 2 (Schreiben)
x = 1 (Ausführen)
```

### Wichtige Rechte

| Rechte | Bedeutung | Beispiel |
|--------|-----------|----------|
| `600` | Nur Owner lesen/schreiben | Config-Files |
| `644` | Owner rw, alle lesen | Normale Files |
| `755` | Owner rwx, alle rx | Scripts, Directories |
| `700` | Nur Owner alles | Private Verzeichnisse |

### Rechte setzen

```bash
chmod 600 ~/.openclaw/openclaw.json
chmod 700 ~/.ssh/
chmod 644 ~/.ssh/authorized_keys
```

---

## 9.10 Pfade in Configs

### Niemals Hardcoded

```javascript
// ❌ SCHLECHT
const path = "/home/clawbot/.openclaw/workspace/ceo";

// ✅ GUT
const workspace = process.env.OPENCLAW_WORKSPACE || 
  "/home/clawbot/.openclaw/workspace";
const ceoDir = `${workspace}/ceo`;
```

### Pfade in openclaw.json

```json
{
  "gateway": {
    "port": 18789
  },
  "agents": {
    "ceo": {
      "workspace": "/home/clawbot/.openclaw/workspace/ceo",
      "agentDir": "/home/clawbot/.openclaw/agents/ceo/agent"
    }
  }
}
```

---

## 9.11 Dateien finden

### find-Befehl

```bash
# Alle .md Dateien im Workspace
find /home/clawbot/.openclaw/workspace -name "*.md"

# Alle JSON-Dateien
find /home/clawbot/.openclaw -name "*.json"

# Nach Größe
find /home/clawbot/.openclaw/workspace -size +1M

# Nach Zeit (letzte 24h)
find /home/clawbot/.openclaw/workspace -mtime -1

# Nach Typ
find /home/clawbot/.openclaw -type f -name "*.md"
```

---

## 9.12 Dateien durchsuchen

### grep

```bash
# Nach Text suchen
grep "API_KEY" ~/.openclaw/workspace/**/*.md

# Case-insensitive
grep -i "secret" /home/clawbot/.openclaw/**/*.md

# Mit Zeilennummern
grep -n "function" script.py

# Nur Dateinamen
grep -l "TODO" *.md
```

### jq (JSON)

```bash
# JSON lesen
jq '.' config.json

# Spezielles Feld
jq '.gateway.port' config.json

# Array-Element
jq '.agents[0].name' config.json
```

---

## 📝 Zusammenfassung

| Konzept | Beschreibung |
|---------|--------------|
| Absolute Pfade | Komplett von Root (/home/...) |
| Relative Pfade | Vom Workdir aus (../builder/) |
| write | Überschreibt gesamte Datei |
| edit | Ersetzt exakten Text |
| exec | Shell-Befehle für komplexe Ops |
| Backup | Wichtige Verzeichnisse sichern |
| Rechte | 600/644/755 für Sicherheit |

---

## ✅ Checkpoint

- [ ] Was ist der Unterschied zwischen absoluten und relativen Pfaden?
- [ ] Erstellt write automatisch Parent-Directories?
- [ ] Warum ist chmod 600 für Config-Files wichtig?
- [ ] Welche Verzeichnisse sollte man NICHT sichern?
- [ ] Wie findest du alle .md Dateien im Workspace?

---

*Lektion 9 — Workspace & Files — Version 1.0*
