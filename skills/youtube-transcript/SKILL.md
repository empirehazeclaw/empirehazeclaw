# YouTube Transcript Skill

## Was es macht

Holt Transcripts/Untertitel von YouTube Videos mit Timestamps.

## Tools

- **yt-dlp** — installiert unter `/home/clawbot/.local/bin/yt-dlp`
- ** whisper** — für Audio→Text falls keine Untertitel verfügbar

## Usage

### CLI (direkt)

```bash
# Auto-generated subtitles (kein Download, nur Subs)
yt-dlp --write-auto-sub --skip-download --output /tmp/video.%(id)s "YOUTUBE_URL"

# Bestimmte Sprache
yt-dlp --write-auto-sub --sub-langs "de,en" --skip-download "URL"

# Transcript als Text (ohne Timestamps)
yt-dlp --write-auto-sub --sub-format vtt --skip-download "URL"

# Video auch herunterladen
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]" "URL"
```

### Via Skill (Telegram)

- `!transcript <url>` — Vollständiges Transkript mit Timestamps
- `!summary <url>` — Kurze Zusammenfassung des Videos

## Fallback: whisper (keine Untertitel)

Wenn das Video keine Untertitel hat:

```bash
# Video downloaden
yt-dlp -f "bestaudio[ext=m4a]" --output /tmp/audio.%(id)s "URL"

# Mit whisper transkribieren
whisper "/tmp/audio.XXXXX.m4a" --model base --language German --output_dir /tmp
```

## Unterstützte Formate

- **VTT** — WebVTT mit Timestamps
- **SRT** — SubRip
- **JSON** — mit Timing-Info

## Examples

```
!transcript https://www.youtube.com/watch?v=abc123xyz
```

Ausgabe:
```
📺 Video: Example Title
⏱ Dauer: 12:34

[00:00] Hallo und willkommen...
[00:15] Heute zeige ich euch...
[01:30] Der erste Schritt ist...
...
```
