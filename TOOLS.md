# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Ken Burns Animation
- Script: `/scripts/ai/ken_burns_pro.py` (60fps, Sine Easing)
- Usage: `python3 scripts/ai/ken_burns_pro.py -i bild.jpg -o video.mp4`

### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### ✨ Answer Quality Rules (since 2026-03-21)

**Bei Faktenfragen (Ports, Configs, Entscheidungen, Daten):**
1. **Memory zuerst** → Immer `memory_search` starten bevor ich antworte
2. **Nicht raten** → Wenn unsicher, klar sagen „weiß nicht sicher"
3. **Quellen nennen** → „Laut MEMORY/Entscheidung X..."
4. **Nachfragen** → Bei Unsicherheiten: „Soll ich nachschauen?"

---

Add whatever helps you do your job. This is your cheat sheet.

### TTS (Text-to-Speech)
- **Script:** `/home/clawbot/.openclaw/workspace/scripts/ttsnotify.js`
- **Default Voice:** "Seraphina" (de-DE-SeraphinaMultilingualNeural)
- **Engine:** Edge-TTS (kostenlos, hohe Qualität)

**CLI Usage:**
```bash
# Einfach - Standard Stimme
node scripts/ttsnotify.js "Dein Text hier"

# Mit bestimmter Stimme
node scripts/ttsnotify.js "Hello World" --voice en-US-AriaNeural

# Als Datei speichern (kein Playback)
node scripts/ttsnotify.js "Wichtige Nachricht" --output /tmp/alert.mp3

# Hilfe anzeigen
node scripts/ttsnotify.js --help
```

**Verfügbare Stimmen:**
- German: `de-DE-SeraphinaMultilingualNeural`, `de-DE-KlausNeural`, `de-DE-KlaraNeural`
- English: `en-US-AriaNeural`, `en-US-GuyNeural`, `en-GB-SoniaNeural`

**Automatische Ansage bei wichtigen Ergebnissen:**
```javascript
// In Agent Scripts:
const { speak } = require('./scripts/ttsnotify.js');
await speak("Agent Aufgabe abgeschlossen! Ergebnis: " + result);
```

### Capability Evolver (🧬)
- Skill: `skills/capability-evolver/`
- Script Review: `scripts/evolve.sh` (empfohlen)
- Script Auto: `scripts/evolve-auto.sh` (Mad Dog Mode)
- **WICHTIG:** `EVOLVE_ALLOW_SELF_MODIFY=false` (SECURITY!)
- Strategy: balanced, innovate, harden, repair-only

### TikTok Marketing (Larry Skill)
- Scripts: `scripts/tiktok/`
- Config: `tiktok-marketing/config.json`

### 🎨 Canvas Dashboard
- **File:** `scripts/dashboard.html`
- **Theme:** Modern Dark (wie unsere Websites)
- **Features:** Agent Status, Letzte Workflows, Quick Actions, System Info

**Aufruf per Canvas:**
```
canvas action=present url=file:///home/clawbot/.openclaw/workspace/scripts/dashboard.html
```

**Im Code:**
```javascript
// Via canvas tool
{
  action: "present",
  url: "file:///home/clawbot/.openclaw/workspace/scripts/dashboard.html"
}
```

**Enthält:**
- 🤖 6 Agenten (Dev, Researcher, Social, Trading, POD, Debugger)
- 📊 Stats: Tasks Today, Success Rate
- ⚡ Quick Actions Buttons
- 📋 Letzte Workflows mit Status
- 💻 System Info (Runtime, Host, Model, Channel)
- Tool: xurl (installed)
- Usage: `xurl post 'message'`
- Status: ✅ Working (2026-03-17)

### Memory Auto-Sync 🧠
- Script: `scripts/autosync.js`
- Speichert wichtige Entscheidungen automatisch ins Memory
- CLI Usage:
  ```bash
  # Entscheidung speichern
  node scripts/autosync.js "Wichtige Decision"
  
  # Todo speichern
  node scripts/autosync.js --type todo "Neue Aufgabe"
  
  # Learning speichern
  node scripts/autosync.js --type learning "Gelernte Lektion"
  
  # Daily Sync manuell ausführen
  node scripts/autosync.js --sync
  ```
- Cron Setup: `scripts/setup-cron.sh`
- Läuft täglich um 23:00 Uhr
- Speichert in: `memory/YYYY-MM-DD.md` + `MEMORY.md`
- Logs: `/var/log/autosync.log`

### 🔔 Webhook Alerts
- Script: `scripts/webhook.js`
- Usage:
  ```bash
  node webhook.js "Titel" "Nachricht"           # Telegram an Nico
  node webhook.js "Titel" "Nachricht" --telegram
  node webhook.js "Titel" "Nachricht" --webhook "https://example.com/hook"
  ```
- Environment Variables:
  - `TELEGRAM_BOT_TOKEN` - Telegram Bot Token
  - `TELEGRAM_CHAT_ID` - Ziel-Chat ID (Standard: 5392634979)
  - `WEBHOOK_URL` - Standard Webhook URL


## 📅 Scheduled Workflows
- **Script:** `scripts/scheduled-workflows.js`
- **Config:** `config/scheduled-workflows.json`

**CLI Commands:**
```bash
# Alle Workflows auflisten
node scripts/scheduled-workflows.js list

# Workflow sofort ausführen
node scripts/scheduled-workflows.js run morning-check
node scripts/scheduled-workflows.js run weekly-report

# Neuen Workflow hinzufügen
node scripts/scheduled-workflows.js add "My Workflow" "0 10 * * *" "Daily at 10 AM" "Description"

# Workflow aktivieren/deaktivieren
node scripts/scheduled-workflows.js enable morning-check
node scripts/scheduled-workflows.js disable morning-check

# Cron Setup anzeigen
node scripts/scheduled-workflows.js cron
```

**Vordefinierte Workflows:**

| Workflow | Schedule | Beschreibung |
|----------|----------|---------------|
| `morning-check` | Täglich 8:00 Uhr | Website & Service Health Check |
| `weekly-report` | Sonntag 9:00 Uhr | Wochenzusammenfassung |

**Cron Setup (einmalig):**
```bash
crontab -e
# Add:
0 8 * * * node /home/clawbot/.openclaw/workspace/scripts/scheduled-workflows.js run morning-check
0 9 * * 0 node /home/clawbot/.openclaw/workspace/scripts/scheduled-workflows.js run weekly-report
```

**Workflow Format (JSON):**
```json
{
  "my-workflow": {
    "name": "My Workflow",
    "description": "Description",
    "schedule": "0 10 * * *",
    "scheduleHuman": "Daily at 10:00 AM",
    "tasks": [
      { "type": "script", "path": "scripts/morning_routine.py" },
      { "type": "check", "name": "Health Check" }
    ],
    "enabled": true
  }
}
```

---

## 🤖 Auto-Workflow Integration

Bei komplexen Requests (>1 Agent nötig):
```bash
node /home/clawbot/.openclaw/workspace/scripts/workflow-spawn.js "<request>"
```

Beispiele:
- "analysiere website + erstelle blog + twitter" → dev + social + researcher
- "erstelle website + poste auf twitter" → dev + social

---

### 📁 File Watcher (Auto-Deploy)
- **Script:** `/home/clawbot/.openclaw/workspace/scripts/filewatcher.js`
- **Library:** chokidar (zuverlässiges File Watching)
- **Setup-Script:** `scripts/setup-nginx-watcher.sh` (für nginx auto-reload)

**CLI Usage:**
```bash
# Bei neuen HTML-Dateien deployen
node scripts/filewatcher.js --dir /var/www --command "echo 'New file!'"

# Nur bestimmte Extensions überwachen
node scripts/filewatcher.js --dir /var/www --command "nginx -s reload" --extensions html,css,js

# Mit Debounce (verhindert Flood bei mehreren Files)
node scripts/filewatcher.js --dir /path --command "npm run build" --debounce 1000

# Einmal ausführen und beenden (--once)
node scripts/filewatcher.js --dir /path --command "deploy.sh" --once

# Ausführliche Ausgabe
node scripts/filewatcher.js --dir /path --command "cmd" --verbose

# Hilfe
node scripts/filewatcher.js --help
```

**Optionen:**
| Option | Beschreibung | Standard |
|--------|--------------|----------|
| `--dir` | Zu überwachendes Verzeichnis | (erforderlich) |
| `--command` | Befehl der ausgeführt wird | (erforderlich) |
| `--extensions` | Nur diese Extensions (csv: html,css,js) | alle |
| `--debounce` | Wartezeit zwischen Events (ms) | 500 |
| `--once` | Nur einmal ausführen | false |
| `--verbose` | Ausführliche Ausgabe | false |

**Beispiel: nginx auto-reload bei Änderungen**
```bash
# Quick Start
./scripts/setup-nginx-watcher.sh start

# Status prüfen
./scripts/setup-nginx-watcher.sh status

# Stoppen
./scripts/setup-nginx-watcher.sh stop
```

**Konfiguration (setup-nginx-watcher.sh):**
- Watch Dir: `/var/www`
- Command: `nginx -s reload`
- Extensions: `html,css,js,php`
- Log: `/var/log/filewatcher-nginx.log`

**Cron Beispiel (statt Permanent):**
```bash
# Cron: Filewatcher nur zur Deploy-Zeit aktivieren
crontab -e
# Add:
# 0 8,12,18 * * * node /home/clawbot/.openclaw/workspace/scripts/filewatcher.js --dir /var/www --command "nginx -s reload" --extensions html --once
```

---

### 🌐 Multi-Language Translation (multilang.js)
- **Script:** `/home/clawbot/.openclaw/workspace/scripts/multilang.js`
- **Provider:** MyMemory API (free, reliable)
- **Fallback:** LibreTranslate (may not be available)

**CLI Usage:**
```bash
# Übersetzen (Auto-Detect → German default)
node multilang.js "Hallo Welt" --to en

# Mit Quellsprache
node multilang.js "Hello World" --from en --to de

# Andere Sprachen
node multilang.js "Bonjour" --to en
node multilang.js "Hola" --from es --to de

# Sprachliste anzeigen
node multilang.js --list

# APIs testen
node multilang.js --test
```

**Unterstützte Sprachen:** EN, DE, ES, FR, IT, PT, RU, ZH, JA, KO, AR, NL, PL, TR, und mehr...

**Hinweis:** MyMemory hat ein Limit von 1000 Wörtern/Tag (kostenlos).

---

### 📧 Newsletter System

Ein einfaches Newsletter-Anmeldesystem für die EmpireHazeClaw Websites.

**Komponenten:**

| Datei | Beschreibung |
|-------|--------------|
| `newsletter.html` | Eigenständige Newsletter-Anmeldeseite |
| `data/newsletter-subscribers.json` | Speicher für alle Abonnenten |
| `templates/newsletter-confirmation.txt` | Bestätigungs-E-Mail Template |
| `templates/newsletter-footer.html` | Footer-Komponente für Websites |

**Features:**
- Moderne Dark-Theme Optik (passt zu allen Websites)
- E-Mail-Validierung in Echtzeit
- Erfolgsmeldung nach Anmeldung
- Lokale Speicherung (localStorage) als Backup
- Einfache Integration via HTML-Snippet

**Verwendung als Standalone-Seite:**
```
/newsletter.html
```

**Footer-Komponente einbinden:**
```html
<!-- Fügen Sie dies vor dem </body> Tag ein -->
<link rel="stylesheet" href="/templates/newsletter-footer.css">
<script src="/templates/newsletter-footer.js"></script>
<!-- Oder direkt den HTML-Code aus newsletter-footer.html kopieren -->
```

**Datenformat (JSON):**
```json
{
  "subscribers": [
    {
      "email": "user@example.com",
      "name": "Max Mustermann",
      "subscribedAt": "2026-03-17T23:35:00Z",
      "confirmed": false,
      "source": "footer"
    }
  ]
}
```

**Hinweis:** Aktuell werden Daten im localStorage gespeichert. Für eine voll funktionsfähige Lösung sollte ein Backend (Node.js/PHP) implementiert werden, das die Daten in die JSON-Datei schreibt.

### High Quality Voice Messenger (Telegram Fix)
- **Script:** `/home/clawbot/.openclaw/workspace/scripts/speak_high_quality.sh "Text"`
- **Why:** Umgeht Telegram `base64` Limits und schickt die Seraphina-Stimme fehlerfrei direkt in den Chat als Voice-Message.

---

## 📧 GOG CLI (Gmail Email)

**Status:** ✅ Working (2026-03-26)
**Path:** `/home/clawbot/archive_old_system/.linuxbrew/Cellar/gogcli/0.12.0/bin/gog`
**Token:** `~/.config/gogcli/token.env`

### Email senden:
```bash
/home/clawbot/archive_old_system/.linuxbrew/Cellar/gogcli/0.12.0/bin/gog send --to empfaenger@example.com --subject "Betreff" --body "Nachricht"
```

### Token erneuern wenn abgelaufen:
```bash
/home/clawbot/archive_old_system/.linuxbrew/Cellar/gogcli/0.12.0/bin/gog auth login --account empirehazeclaw@gmail.com
```

**Dokumentation:** `memory/tools/gmail-gog-cli.md`

---

## 🎙️ Whisper (Audio Transcription)
**Installiert:** openai-whisper

**Nutzung:**
```bash
# OGG zu WAV konvertieren
ffmpeg -i audio.ogg -ar 16000 -ac 1 audio.wav

# Transkribieren
python3 -c "
import whisper
model = whisper.load_model('base')
result = model.transcribe('audio.wav', language='de')
print(result['text'])
"
```

---

## 🔑 Vercel Token
**Token:** `vcp_REDACTED`
**Gültig:** 90 Tage (lest 90-Tage Token)
