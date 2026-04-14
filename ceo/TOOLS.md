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
- **Installed:** `/home/clawbot/.local/bin/whisper`
- **Usage:** 
  ```bash
  whisper "<audio-file>.ogg" --model base --language German --output_dir /tmp
  ```
- **Output:** `*.txt`, `*.json`, `*.srt` files in /tmp
- **Model size:** Use `base` for speed, `medium` for accuracy (1.4GB download if not cached)
- **Note:** Transcribe ONLY when an audio file is actually received. Do NOT proactively look for or speculate about voice notes — wait for the file to arrive first.

### TTS
See TTS tool — configured and working.
