# 🎤 Discord Voice Integration Plan

**Erstellt:** 2026-04-17
**Ziel:** Echte Voice-Communication mit Sir HazeClaw

---

## Warum Discord Voice?

| Telegram Voice | Discord Voice |
|---------------|---------------|
| ~1-2min Delay | Echtzeit (ms) |
| OpenClaw Queue | Direct WebSocket |
| Kein Interrupt | Volle Interaktion |

---

## Optionen Analyse

### Option 1: Discord Bot Voice (discord.py + voice)
- **Aufwand:** Mittel
- **Kosten:** Kostenlos
- **Komplexität:** Mittel
- **Status:** Unser Bot kann nur TEXT

### Option 2: Pipecat + Discord
- **Aufwand:** Hoch
- **Kosten:** $ (API Keys nötig)
- **Komplexität:** Hoch
- **Status:** Framework für Voice AI

### Option 3: External Service (Daily.co, Agora, Twilio)
- **Aufwand:** Mittel
- **Kosten:** $$$ (pay-per-use)
- **Komplexität:** Niedrig
- **Status:** "Out of the box" Lösungen

---

## Option 1: Discord Voice Bot (Empfohlen für uns)

### Was wir brauchen:

**1. Discord Bot Permissions:**
```
- CONNECT (Voice Channels beitreten)
- SPEAK (Voice sprechen)
- VIEW_CHANNEL (Channels sehen)
- SEND_MESSAGES (Text responses)
```

**2. Python Libraries:**
```
- discord.py (voice support)
- discord-ext-voice-recv (speech-to-text)
- faster-whisper (STT - haben wir schon!)
```

**3. Architecture:**
```
User Voice → Discord Voice → STT → OpenClaw → TTS → Discord Voice → User
```

### Implementation Steps:

#### Phase 1: Basic Voice Join
```
1. Bot Permission prüfen
2. Voice Channel Connection testen
3. Join/Leave Command
```

#### Phase 2: Speech-to-Text
```
4. discord-ext-voice-recv installieren
5. Audio Capture Pipeline
6. faster-whisper Integration
```

#### Phase 3: AI Integration
```
7. OpenClaw API Anbindung
8. Response Generation
9. TTS (edge-tts - haben wir schon!)
```

#### Phase 4: Polish
```
10. Error Handling
11. Multi-User Support
12. German Language Optimization
```

---

## Detaillierte Schritte

### Step 1: Bot Permissions Prüfen
```python
# Prüfe ob Bot VOICE Permissions hat
# OAuth2 URL mit scopes:
# - bot
# - voice (falls verfügbar)
```

### Step 2: Code Architektur
```python
# discord_voice_bot.py

import discord
from discord.ext import voice_recv
import asyncio
from faster_whisper import WhisperModel

class VoiceBot:
    def __init__(self):
        self.model = WhisperModel('tiny', device='cpu', compute_type='int8')
    
    async def on_voice_join(self, voice_state):
        # Audio → Transcribe → OpenClaw → Response → TTS
        pass
```

### Step 3: Integration mit OpenClaw
```python
# OpenClaw Session erstellen
# Message schicken
# Response empfangen
```

---

## Kritische Technical Notes

### discord-ext-voice-recv Warning:
> "Special care should be taken not to write excessively computationally expensive code, as python is not particularly well suited to real-time audio processing."

### Real-time Audio Pipeline:
```
Discord Voice (Opus) → discord-ext-voice-recv → Raw PCM → Whisper (tiny) → Text
Text → OpenClaw → Text → edge-tts → Discord Voice (Opus) → User
```

### Latency Targets:
| Component | Target | Worst Case |
|----------|--------|------------|
| STT (Whisper tiny) | ~1s | ~2s |
| OpenClaw Response | ~3-5s | ~10s |
| TTS (edge-tts) | ~1s | ~2s |
| **Total** | **~5-8s** | **~15s** |

### Alternative STT (schneller):
- **Silero VAD** + **Whisper tiny** - besser für deutsche Sprache
- **Google Cloud Speech** - sehr schnell, aber API Key nötig

### Alternative TTS (schneller):
- **edge-tts** - haben wir schon ✅
- **Piper TTS** - local, schnell, gute deutsche Stimmen

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Discord API Changes | Mittel | Regelmäßig updaten |
| Voice Quality | Niedrig | gunicorn/ffmpeg |
| Latency | Mittel | Local STT/TTS |
| Bot Disconnect | Mittel | Auto-reconnect Logic |

---

## Geschätzter Aufwand

| Phase | Zeit | Komplexität |
|-------|------|-------------|
| Phase 1 | 1-2h | Niedrig |
| Phase 2 | 2-3h | Mittel |
| Phase 3 | 3-4h | Mittel |
| Phase 4 | 1-2h | Niedrig |
| **Total** | **7-11h** | - |

---

## Alternativen Overviews

### Pipecat
- **Pro:** Modernes Framework, viele Connectors
- **Contra:** Neues Framework lernen, mehr Dependencies
- **Kosten:** API Keys nötig

### Daily.co
- **Pro:** "Out of the box", kein Bot nötig
- **Contra:** Extra Service, monatliche Kosten
- **Kosten:** ~$50-200/Monat

### Twilio
- **Pro:** Professionell, skalierbar
- **Contra:** Komplex, teuer
- **Kosten:** ~$0.50/GB Speech

---

## Empfehlung

**Option 1 (Discord Voice Bot)** ist die beste Wahl weil:
1. Wir haben bereits einen Discord Bot
2. Kostenlos
3. Wir haben Whisper schon installiert
4. Edge-TTS funktioniert bereits

**Nächster Schritt:** Phase 1 starten - Bot Permissions prüfen

---

## Todo List (Reihenfolge)

### Phase 1: Setup (1-2h)
- [x] **1.1** Bot Permissions in Discord Developer Portal prüfen ✅
- [x] **1.2** discord-ext-voice-recv installieren ✅
- [ ] **1.3** Basic Join Command erstellen (Script erstellt)
- [ ] **1.4** Voice Connection testen

### Phase 2: STT Integration (2-3h)
- [ ] **2.1** Audio Capture Pipeline bauen
- [ ] **2.2** faster-whisper Integration
- [ ] **2.3** German Language Optimization
- [ ] **2.4** Voice Activity Detection (VAD) testen

### Phase 3: AI Integration (3-4h)
- [ ] **3.1** OpenClaw Session Anbindung
- [ ] **3.2** Response Generation Loop
- [ ] **3.3** edge-tts Integration
- [ ] **3.4** Full Pipeline testen

### Phase 4: Polish (1-2h)
- [ ] **4.1** Error Handling & Reconnect
- [ ] **4.2** Echo Prevention
- [ ] **4.3** Multi-User Support
- [ ] **4.4** Production Deployment

---

## Decision Matrix

| Kriterium | Discord Voice | Pipecat | Daily.co |
|-----------|--------------|---------|----------|
| Kosten | ★★★★★ | ★★★☆☆ | ★★☆☆☆ |
| Aufwand | ★★★☆☆ | ★★☆☆☆ | ★★★★★ |
| Kontrolle | ★★★★★ | ★★★☆☆ | ★★☆☆☆ |
| Komplexität | ★★★☆☆ | ★★☆☆☆ | ★★★★★ |
| **Gesamt** | **★★★★★** | **★★☆☆☆** | **★★☆☆☆** |

---

_Letzte Aktualisierung: 2026-04-17_