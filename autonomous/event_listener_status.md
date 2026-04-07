# Event Listener Status

## Datum
2026-04-07 06:27 UTC

## Problem
Der `event_listener` wurde in `autonomous_loop.log` als DOWN markiert.

## Analyse

### 1. Wo ist der event_listener definiert?
- **Hauptfile**: `/home/clawbot/.openclaw/workspace/event_listener.js`
- **Config in**: `/home/clawbot/.openclaw/workspace/self_healing.py` (Zeile 42-46)
- **Start-Kommando**: `cd /home/clawbot/.openclaw/workspace && node scripts/event_listener.js`

### 2. Warum lief er nicht?
Das `self_healing.py` script verlangt:
```
"start_cmd": "cd /home/clawbot/.openclaw/workspace && node scripts/event_listener.js"
```
**Problem**: Der event_listener liegt aber direkt in `/home/clawbot/.openclaw/workspace/event_listener.js`, NICHT in `scripts/`.

Also selbst wenn der SelfHealer versuchen würde, ihn zu starten - das Kommando wäre falsch.

### 3. Warum crashte autonomous_loop.py?
Zusätzlich hat `autonomous_loop.py` einen Bug:
```
AttributeError: 'SelfHealer' object has no attribute 'config'
```
Die `check_services()` Funktion versucht `healer.config["services"]` zuzugreifen, aber `SelfHealer` speichert `CONFIG` als globale Variable, nicht als Instance-Attribut.

## Lösung

1. **Event Listener manuell gestartet**:
   ```bash
   node /home/clawbot/.openclaw/workspace/event_listener.js &
   ```

2. **Verifizierung**: Process läuft jetzt (PID 52678)

3. **Offenes Problem**: `autonomous_loop.py` crasht wegen `healer.config` Bug - das ist ein separater Bug der noch gefixt werden muss.

## Status
- ✅ event_listener.js: RUNNING (PID 52678)
- ⚠️ autonomous_loop.py: CRASHED (healer.config Bug)
- ⚠️ SelfHealer.start_cmd: falscher Pfad (`scripts/event_listener.js` statt Hauptverzeichnis)

## Nächste Schritte
1. [ ] SelfHealer CONFIG Pfad korrigieren: `scripts/event_listener.js` → `event_listener.js`
2. [ ] `SelfHealer` Klasse fixen: `self.config = CONFIG` in `__init__` hinzufügen
