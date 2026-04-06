# Dialekt TTS Service - Schritt-für-Schritt Guide

## Projekt-Übersicht

**Ziel:** Deutscher Dialekt Text-to-Speech Service für lokale Unternehmen

**Erster Dialekt:** Saarländisch (weil Nico Familie hat, die testen kann)

---

## Schritt 1: Daten sammeln

### Warum eigene Aufnahmen?
- Online-Quellen (YouTube, Podcasts) in echtem Saarländisch sind selten
- Eigene Aufnahmen = bessere Qualität + authentischer Dialekt

### Was wir brauchen:
- **3-5 verschiedene Sprecher** aus Nicos Familie
- **Je 30-60 Minuten Audio** pro Person
- Themen: Alltag, Familie, Wetter, Essen

### Aufnahme-Anleitung:
1. Smartphone-Re USB-Mikro
korder oder2. Natürlich über Alltag reden
3. MP3/WAV Format (16kHz+)
4. Leise Umgebung

---

## Schritt 2: Audio aufbereiten

### Tools:
| Tool | Zweck |
|------|-------|
| Audacity / ffmpeg | Rauschen entfernen, schneiden |
| faster-whisper | STT: Automatische Transkription |
| Coqui XTTS | TTS: Dialekt-Stimme generieren |

### Workflow:
1. **Noise Reduction** - Hintergrundgeräusche entfernen
2. **Split** - In 10-30 Sekunden Clips schneiden
3. **Transcribe** - Whisper erkennt Text automatisch
4. **Align** - Text-Datei mit Audio verknüpfen

### Benötigte Formate für Coqui XTTS:
```
dataset/
├── wav/
│   ├── speaker1/
│   │   ├── 001.wav
│   │   ├── 002.wav
│   └── speaker2/
│       ├── 001.wav
├── metadata.csv
```

### metadata.csv Format:
```
wav/speaker1/001.wav|"Der Text der gesprochen wurde"|der text der gesprochen wurde
wav/speaker1/002.wav|"Noch ein Satz"|noch ein satz
```

---

## Schritt 3: Modell trainieren

### Option A: Lokal (Nicos PC mit 3080 Ti)
- **Vorteil:** Günstig, nur Stromkosten
- **Tool:** Coqui XTTS Docker Container
- **Dauer:** ~2-4 Stunden mit 3080 Ti

### Option B: Cloud-GPU (falls keine GPU)
- **Anbieter:** RunPod, Lambda Labs, Paperspace
- **Kosten:** ~1€/Stunde
- **Dauer:** ~1-2 Stunden

### Training starten (Coqui XTTS):
```bash
# Docker Container starten
docker run --gpus all -v /path/to/data:/data coqui/xtts

# Training
python train.py --model_path /data/dataset --output_path /data/models
```

---

## Schritt 4: API aufbauen

### Komplett-Paket: STT + TTS

**STT (Speech-to-Text):** Audio → Text (Transkription)
**TTS (Text-to-Speech):** Text → Audio (Sprachausgabe)

### Python Script (STT + TTS):
```python
from faster_whisper import Whisperts import TTSModel
from xt
import io

class DialektService:
    def __init__(self):
        # STT: Whisper für Transkription
        self.stt = WhisperModel("small", device="cpu")
        
        # TTS: Coqui XTTS für Dialekt-Sprache
        self.tts = TTS("model_saarland.pth")
    
    def speech_to_text(self, audio_file):
        """Audio rein, Text raus"""
        segments, info = self.stt.transcribe(audio_file)
        return " ".join([s.text for s in segments])
    
    def text_to_speech(self, text):
        """Text rein, Audio raus"""
        audio = self.tts.synthesize(text)
        return audio
    
    def full_conversation(self, audio_input):
        """Komplett: Audio → verstehen → antworten → sprechen"""
        # 1. Transkribieren
        text = self.speech_to_text(audio_input)
        
        # 2. KI-Antwort generieren (optional)
        # answer = generate_response(text)
        
        # 3. Als Audio ausgeben
        audio_output = self.text_to_speech(text)
        return audio_output
```

### API Endpunkte:
```
POST /api/stt          # Audio → Text
POST /api/tts          # Text → Dialekt-Audio
POST /api/conversation # Audio → Audio (full duplex)
```

### Beispiel-Request (STT):
```bash
curl -X POST /api/stt -F "audio=@aufnahme.wav"
# Returns: {"text": "Der Text aus der Aufnahme"}
```

### Beispiel-Request (TTS):
```bash
curl -X POST /api/tts -d '{"text": "Grüß Gott!", "dialect": "saarland"}'
# Returns: Audio-Datei (MP3/WAV)
```

---

## Geschäftsmodell

### Zielgruppen:
- Lokale Restaurants
- Einzelhändler
- Tourismus & Museen
- Werbeagenturen

### Preise:
| Tier | Preis | Features |
|------|-------|----------|
| Starter | 29€/Monat | 1 Dialekt, 1000 Wörter |
| Business | 99€/Monat | 3 Dialekte, unbegrenzt |
| Enterprise | individuell | Custom Voices, API |

---

## Wettbewerb

**Marktlücke:** Kein Anbieter bietet aktuell deutsche Dialekte!
- ElevenLabs: Nur Standard-Sprachen
- WellSaid: Nur Standard-Sprachen
- Murf AI: Nur Standard-Sprachen

**Wir wären die Ersten!** 🌟

---

## Nächste Schritte

1. [ ] Nico nimmt Familie auf (3-5 Personen, je 30min)
2. [ ] Audio-Dateien bereinigen
3. [ ] Transkription erstellen (STT)
4. [ ] Coqui XTTS Training starten (TTS)
5. [ ] Python Script für STT+TTS bauen
6. [ ] API aufbauen

---

*Erstellt: 2026-03-08*
