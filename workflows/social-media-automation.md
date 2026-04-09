# Social Media Automation Workflow

**Ziel:** Automatisiertes Posten auf Instagram, Twitter/X und TikTok mit strukturiertem Content Planning und Hashtag-Recherche.

---

## 📋 Übersicht

| Plattform | Hauptfunktion | Zeitaufwand |
|-----------|---------------|-------------|
| Instagram | Feed Posts, Stories, Reels | 15-30 Min/Post |
| Twitter/X | Text, Bilder, Threads | 10-20 Min/Post |
| TikTok | Videos, Hashtags | 20-45 Min/Post |

**Tools:** Buffer, Later, Hootsuite, Metricool, ChatGPT, CapCut

---

## 1. Content Planning

### 1.1 Content-Kalender erstellen

```bash
# Wochenplanung via CLI (Beispiel)
mkdir -p content/$(date +%Y-%W)
touch content/$(date +%Y-%W)/plan.md
```

**Content Plan Template:**

```markdown
# Woche 10 - Content Plan

## Montag
- [ ] Thema: Produkt-Feature
- [ ] Plattform: Instagram + Twitter
- [ ] Hashtags: #product #design #handmade

## Mittwoch
- [ ] Thema: Behind the Scenes
- [ ] Plattform: TikTok + Instagram Stories
- [ ] Hashtags: #behindthescenes #etsyshop
```

### 1.2 Hashtag-Recherche

**Tools:**
- Hashtagify (hashtagify.com)
- Display Purposes (displaypurposes.com)
- Instagram Explore Recherche

**CLI-Suche (optional):**

```bash
# Hashtag-Recherche via web_search
web_search --query "best hashtags for handmade products etsy 2024" --count 5 --country DE
```

**Automatisierung:** Wöchentliche Hashtag-Listen in Notion/Excel speichern.

---

## 2. Plattform-Setup

### 2.1 Buffer Account Setup

```bash
# API-Key in .env speichern
echo 'BUFFER_API_KEY="your_api_key"' >> ~/.env
```

### 2.2 Posting-Schedule konfigurieren

| Plattform | Beste Zeiten (MEZ) | Frequenz |
|-----------|-------------------|----------|
| Instagram | 11:00, 14:00, 19:00 | Täglich |
| Twitter | 09:00, 12:00, 17:00 | 2x täglich |
| TikTok | 10:00, 15:00, 20:00 | 5x Woche |

---

## 3. Content Creation

### 3.1 Instagram Post erstellen

```bash
# Bild optimieren (ImageMagick)
convert input.jpg -resize 1080x1080 -quality 85 output.jpg

# Oder mit ffmpeg für Reels
ffmpeg -i input.mp4 -vf "scale=1080:1920" -c:a copy output.mp4
```

### 3.2 Twitter Thread erstellen

**Format-Struktur:**
1. Hook (Attention Grabber)
2. Problem Statement
3. Solution/Value
4. Call to Action

### 3.3 TikTok Video erstellen

**Tools:** CapCut, InShot, TikTok's native editor

```bash
# Video komprimieren für Upload
ffmpeg -i input.mp4 -vcodec h264 -acodec aac -crf 28 output.mp4
```

---

## 4. Automatisierung

### 4.1 Buffer API Posting

```python
#!/usr/bin/env python3
import requests
import os
from datetime import datetime, timedelta

BUFFER_API_URL = "https://api.bufferapp.com/1/"
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")

def post_to_buffer(text, media=None, profile_ids=None):
    """Post to Buffer queue."""
    data = {
        "text": text,
        "access_token": BUFFER_ACCESS_TOKEN,
        "profile_ids[]": profile_ids or []
    }
    
    if media:
        data["media[link]"] = media
    
    response = requests.post(
        f"{BUFFER_API_URL}updates/create.json",
        data=data
    )
    return response.json()

# Usage
post_to_buffer(
    text="🛍️ Neues Design verfügbar! #handmade #etsy",
    media="https://etsy.com/your-product",
    profile_ids=["instagram_id", "twitter_id"]
)
```

### 4.2 Automatisierter Scheduler (Cron)

```bash
# Täglich um 09:00 Content posten
0 9 * * * /home/clawbot/.openclaw/workspace/scripts/social-post.sh >> /home/clawbot/.openclaw/logs/social-post.log 2>&1
```

### 4.3 Beispiel: Automatisiertes Posting Script

```bash
#!/bin/bash
# social-post.sh - Automatisiertes Social Media Posting

# Farben für Output
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}[$(date)]${NC} Starte Social Media Posting..."

# Lade.env Datei
source ~/.env

# Posche auf Twitter
if [ -f "content/pending/twitter.md" ]; then
    echo "Poste auf Twitter..."
    # Hier Buffer/Twitter API Call einfügen
    mv content/pending/twitter.md content/posted/twitter-$(date +%Y%m%d).md
fi

# Posche auf Instagram
if [ -f "content/pending/instagram.md" ]; then
    echo "Poste auf Instagram..."
    # Hier Buffer/Instagram API Call einfügen
    mv content/pending/instagram.md content/posted/instagram-$(date +%Y%m%d).md
fi

echo "Social Media Posting abgeschlossen."
```

---

## 5. Workflow Checkliste

- [ ] Social Media Accounts verbinden (Buffer/Later)
- [ ] Content-Kalender erstellen
- [ ] Wöchentliche Hashtag-Recherche durchführen
- [ ] Content erstellen (Bilder, Videos, Texte)
- [ ] In SchedulerTool importieren
- [ ] Posting-Zeiten optimieren
- [ ] Analytics auswerten (wöchentlich)
- [ ] Engagement reagieren (täglich)

---

## ⏱️ Zeitaufwand (pro Woche)

| Task | Dauer |
|------|-------|
| Content Planung | 30 Min |
| Hashtag Recherche | 15 Min |
| Content Erstellung | 1-2 Std |
| Scheduling | 15 Min |
| Engagement | 30 Min |
| **Gesamt** | **~2.5 Std/Woche** |

---

## 🔄 Automatisierungspotenzial

| Task | Automatisierbar? | Tool |
|------|-----------------|------|
| Hashtag Vorschläge | ✅ Teilweise | ChatGPT, Hashtagify |
| Posting Schedule | ✅ Ja | Buffer, Later |
| Cross-Posting | ✅ Ja | Buffer |
| Engagement Monitoring | ⚠️ Teilweise | Hootsuite |
| Analytics Report | ✅ Ja | Metricool |

---

## 📁 Dateistruktur

```
knowledge/workflows/
├── content/
│   ├── 2024-10/
│   │   ├── plan.md
│   │   ├── pending/
│   │   └── posted/
│   └── templates/
│       ├── instagram-post.md
│       ├── twitter-thread.md
│       └── tiktok-caption.md
└── scripts/
    ├── social-post.sh
    └── hashtag-research.py
```
