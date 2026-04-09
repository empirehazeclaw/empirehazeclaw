# 🤖 Crawl4AI - Open Source Web Crawler

## Was ist Crawl4AI?

**Crawl4AI** ist ein Open-Source Web Crawler & Scraper, der Webseiten in sauberes, LLM-fähiges Markdown umwandelt.

- **GitHub:** 50k+ Stars ⭐ (#1 trending)
- **Output:** Clean Markdown für RAG, AI Agents, Data Pipelines
- **Keys:** Keine nötig!

## Installation

```bash
# Virtual Environment erstellen
python3 -m venv ~/crawl4ai
source ~/crawl4ai/bin/activate

# Crawl4AI installieren
pip install -U crawl4ai
crawl4ai-setup

# Browser installieren (braucht Chromium)
python3 -m patchright install --with-deps chromium
```

## Basic Usage

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.com",
            # Optional: 
            # css_selector=".article",  # Nur bestimmte Elemente
            # session_id="session1",    # Session Cookies
            # proxy="http://proxy",     # Proxy nutzen
        )
        print(result.markdown)

asyncio.run(main())
```

## CLI Usage

```bash
# Basic crawl
crwl https://beispiel.de -o output.md

# Deep crawl (mehrere Seiten)
crwl https://docs.seite.de --deep-crawl bfs --max-pages 10

# Mit LLM Extraktion
crwl https://beispiel.de/products -q "Alle Produkte und Preise"
```

## Features

| Feature | Beschreibung |
|---------|--------------|
| **LLM Ready** | Sauberes Markdown Output |
| **Async** | Sehr schnell |
| **JavaScript** | Rendert JS |
| **Sessions** | Cookies/Persistence |
| **Proxies** | Proxy Support |
| **Self-Hosted** | Keine Cloud nötig |

## Für uns nützlich?

- ✅ Research automatisieren
- ✅ Content sammeln für Blogs
- ✅ Konkurrenz-Analyse
- ✅ AI Training Data

---

*Erstellt: 2026-03-13*
