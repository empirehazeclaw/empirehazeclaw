# Discord Setup Guide

## Schritt 1: Discord Bot erstellen

1. Gehe zu: https://discord.com/developers/applications
2. Klicke auf **"New Application"**
3. Gib einen Namen ein (z.B. "OpenClaw")
4. Links auf **"Bot"** klicken
5. Klicke auf **"Reset Token"** und kopiere es

## Schritt 2: Bot berechtigen

Wähle folgende **Privileged Intents**:
- ✅ MESSAGE CONTENT
- ✅ GUILD MEMBERS
- ✅ PRESENCE

## Schritt 3: Bot zum Server einladen

1. Gehe zu **"OAuth2"** → **"URL Generator"**
2. Wähle scopes: `bot`, `applications.commands`
3. Wähle permissions:
   - ✅ Send Messages
   - ✅ Read Message History
   - ✅ Manage Channels
   - ✅ Manage Roles
4. Kopiere die URL und öffne sie

## Schritt 4: OpenClaw konfigurieren

Gib mir den Bot Token und die Channel IDs, dann richte ich alles ein!

## Discord Channel Struktur (wird erstellt)

```
📁 OpenClaw (Category)
├── # status          - System Status
├── # logs            - Live Logs  
├── # security        - Security Alerts
├── # agents          - Agent Updates
├── # workflows       - HITL Approvals
└── # commands        - Bot Commands
```

## Commands (nach Einrichtung)

- `/status` - System Status
- `/backup` - Backup starten
- `/approve <id>` - Workflow genehmigen
- `/reject <id>` - Workflow ablehnen
- `/agents` - Agenten Status

---

**Brauchst du Hilfe beim Einrichten?**
