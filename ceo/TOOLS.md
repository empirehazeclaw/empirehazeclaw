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

Add whatever helps you do your job. This is your cheat sheet.

---

## 🎤 Voice / Audio

### Whisper (Speech-to-Text)
**Schnellste Option:** `faster-whisper` mit `tiny` model
```python
from faster_whisper import WhisperModel
model = WhisperModel('tiny', device='cpu', compute_type='int8')
segments, info = model.transcribe('<file>.ogg', language='de')
text = ''.join([s.text for s in list(segments)])
```
- Load: ~0.6s | Transcribe: ~1s | **Total: ~2s** (30x schneller als original whisper)

**Alternativ:** whisper CLI (langsamer)
```bash
whisper "<audio-file>.ogg" --model base --language German --output_dir /tmp
```

### TTS
See TTS tool — configured and working.

---

## 🔄 System Integration (2026-04-16)

### Event Bus
```bash
python3 /workspace/scripts/event_bus.py stats           # Event Stats
python3 /workspace/scripts/event_bus.py list --type kg_update  # Filter
```

### Monitoring
```bash
python3 /workspace/scripts/integration_dashboard.py     # Full Dashboard
python3 /workspace/scripts/integration_dashboard.py --check  # Quick Check
python3 /workspace/scripts/stagnation_detector.py --check all  # Stagnation
```

### Evolver
```bash
bash /workspace/scripts/run_smart_evolver.sh            # Smart Evolver
```

### Backup Locations
- `backups/weekly_backup_*/` — Automated weekly (Sonntag 04:00 UTC)
- `backups/post_integration_20260416_210413/` — Post-Integration Full
- `backups/integration_backup_20260416_185449/` — Pre-Integration Backup
- `backups/core_ultralight_kg_stale_*.json` — Old KG (stale, kann gelöscht werden)

### New Scripts (2026-04-16)
| Script | Purpose |
|--------|---------|
| `learning_to_kg_sync.py` | Bridge Learning Loop → KG |
| `event_bus.py` | Cross-system event pub/sub |
| `stagnation_detector.py` | Monitor stagnation |
| `evolver_signal_bridge.py` | Feed signals to Evolver |
| `evolver_stagnation_breaker.py` | Force gene diversity |
| `integration_dashboard.py` | Unified monitoring |
