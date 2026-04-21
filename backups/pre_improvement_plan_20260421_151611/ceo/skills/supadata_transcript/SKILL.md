# SKILL.md — Supadata YouTube Transcript

## Overview
Holt YouTube Transcripts via Supadata API — inklusive AI-Fallback für Videos ohne Untertitel.

## Setup
```bash
# API Key ist in secrets.env unter SUPADATA_API_KEY gespeichert
```

## Usage (CLI)
```bash
python3 skills/supadata_transcript/scripts/get_transcript.py <youtube_url>
python3 skills/supadata_transcript/scripts/get_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## API Details
- **Endpoint:** `GET https://api.supadata.ai/v1/youtube/transcript`
- **Parameter:** `videoId` (aus URL)
- **Header:** `x-api-key: <key>`
- **Response:** `{ content: [{ text, start, duration }] }`
- **Fallback:** AI transcription wenn keine Captions verfügbar

## Output
Gibt rohen Transcript-Text zurück (alle Segmente concatenated).
