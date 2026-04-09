# AI Research Pipeline Workflow

**Ziel:** Automatisierte Recherche mit Tavily/Brave und strukturierte Wissensspeicherung für Trading, Produkte und allgemeine Recherche.

---

## 📋 Übersicht

| Phase | Beschreibung | Zeitaufwand |
|-------|--------------|-------------|
| Recherche | Web-Suche & Content Fetch | 5-15 Min |
| Analyse | Key Findings extrahieren | 10-20 Min |
| Speicherung | Strukturierte Ablage | 5-10 Min |
| Review | Wöchentliches Update | 15 Min |

**APIs:** Tavily Search API, Brave Search API, OpenWebSearch

---

## 1. Recherche Setup

### 1.1 API-Konfiguration

```bash
# .env Datei einrichten
cat >> ~/.env << 'EOF'
# Tavily API
TAVILY_API_KEY="your_tavily_api_key"

# Brave Search
BRAVE_API_KEY="your_brave_api_key"

# OpenWebSearch (Alternative)
OPENWEBSEARCH_API_KEY="your_key"
EOF
```

### 1.2 CLI-Tools installieren

```bash
# Tavily Python Client
pip3 install tavily

# Brave Search Python Client  
pip3 install brave-search

# OpenWebSearch
pip3 install openwebsearch
```

---

## 2. Recherche Scripts

### 2.1 Tavily Search Script

```python
#!/usr/bin/env python3
# tavily_search.py

import os
import tavily
from datetime import datetime

def search_tavily(query, max_results=5):
    """Recherche mit Tavily AI Search."""
    client = tavily.TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    response = client.search(
        query=query,
        max_results=max_results,
        include_answer=True,
        include_raw_content=False,
        include_images=False
    )
    
    return response

def format_results(results):
    """Formatiere Ergebnisse für Lesbarkeit."""
    output = []
    output.append(f"# Recherche: {results.get('query', 'N/A')}\n")
    output.append(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    output.append("---\n")
    
    for idx, result in enumerate(results.get('results', []), 1):
        output.append(f"## {idx}. {result.get('title', 'N/A')}")
        output.append(f"**URL:** {result.get('url', 'N/A')}")
        output.append(f"**Score:** {result.get('score', 'N/A')}")
        output.append(f"\n{result.get('content', 'N/A')}\n")
        output.append("---\n")
    
    # AI Answer falls vorhanden
    if results.get('answer'):
        output.append(f"## 🤖 AI Zusammenfassung\n")
        output.append(f"{results.get('answer')}\n")
    
    return "\n".join(output)

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "KI Trading 2024"
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    results = search_tavily(query, max_results)
    print(format_results(results))
```

**Usage:**

```bash
python3 scripts/tavily_search.py "Bitcoin ETF approval 2024" 10
python3 scripts/tavily_search.py "Print on Demand trends Etsy 2024" 5
python3 scripts/tavily_search.py "AI trading bots comparison" 8
```

### 2.2 Brave Search Script

```python
#!/usr/bin/env python3
# brave_search.py

import os
from brave import Brave

def search_brave(query, count=10):
    """Recherche mit Brave Search."""
    client = Brave(api_key=os.getenv("BRAVE_API_KEY"))
    
    response = client.search(
        q=query,
        count=count,
        country="DE",
        search_lang="de"
    )
    
    return response

def format_brave_results(response):
    """Formatiere Brave Ergebnisse."""
    output = []
    
    for idx, result in enumerate(response.web.results, 1):
        output.append(f"### {idx}. {result.title}")
        output.append(f"**URL:** {result.url}")
        output.append(f"{result.description}\n")
    
    return "\n".join(output)

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "default"
    
    results = search_brave(query)
    print(format_brave_results(results))
```

**Usage:**

```bash
python3 scripts/brave_search.py "Fiverr skills 2024"
python3 scripts/brave_search.py "Etsy SEO tips"
```

### 2.3 Web Fetch Script

```python
#!/usr/bin/env python3
# web_fetch_content.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def fetch_content(url, max_chars=5000):
    """Extrahiere Haupt-Content von einer Webseite."""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Entferne Skripte und Styles
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()
    
    # Extrahiere Text
    text = soup.get_text(separator='\n', strip=True)
    
    # Begrenze Länge
    return text[:max_chars]

def fetch_and_save(url, output_path):
    """Fetch und speichere Content."""
    content = fetch_content(url)
    
    with open(output_path, 'w') as f:
        f.write(f"# Source: {url}\n\n")
        f.write(content)
    
    print(f"Content gespeichert: {output_path}")

if __name__ == "__main__":
    import sys
    url = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "fetched.md"
    
    fetch_and_save(url, output)
```

**Usage:**

```bash
python3 scripts/web_fetch_content.py "https://example.com/article" content/article.md
```

---

## 3. Strukturierte Speicherung

### 3.1 Ordnerstruktur

```
knowledge/
├── research/
│   ├── 2024/
│   │   ├── Q1/
│   │   │   ├── trading/
│   │   │   │   ├── bitcoin-etf.md
│   │   │   │   ├── ai-trading.md
│   │   │   │   └── crypto-trends.md
│   │   │   ├── pod/
│   │   │   │   ├── etsy-seo.md
│   │   │   │   └── design-trends.md
│   │   │   └── jobs/
│   │   │       ├── fiverr-tips.md
│   │   │       └── upwork-strategy.md
│   │   └── Q2/
│   └── templates/
│       └── research-note.md
├── rag/
│   ├── chunks/
│   └── index.json
└── workflows/
    └── ai-research-pipeline.md
```

### 3.2 Research Note Template

```markdown
# [Titel der Recherche]

**Datum:** {{datum}}
**Quelle:** {{quelle}}
**Tags:** #tag1 #tag2

## Frage
[Was wollte ich herausfinden?]

## Key Findings
- 
- 

## Zusammenfassung
[2-3 Sätze]

## Quellen
1. [Titel](URL)
2. [Titel](URL)

## Next Steps
- [ ]
```

---

## 4. Automatisierung

### 4.1 Wöchentlicher Research Newsletter

```python
#!/usr/bin/env python3
# weekly_research.py

import os
import subprocess
from datetime import datetime
from pathlib import Path

RESEARCH_QUERIES = [
    "AI trading crypto news",
    "Etsy algorithm changes 2024",
    "Print on demand trends",
    "Fiverr gig ranking factors"
]

OUTPUT_DIR = Path("/home/clawbot/.openclaw/workspace/knowledge/research/2024")

def run_weekly_research():
    """Führe wöchentliche Recherche durch."""
    today = datetime.now().strftime("%Y-%m-%d")
    week_dir = OUTPUT_DIR / f"week-{today}"
    week_dir.mkdir(parents=True, exist_ok=True)
    
    for query in RESEARCH_QUERIES:
        # Safe filename
        safe_name = query.replace(" ", "-").lower()[:50]
        output_file = week_dir / f"{safe_name}.md"
        
        # Tavily Search
        cmd = [
            "python3", 
            "scripts/tavily_search.py", 
            query, 
            "5"
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            cwd="/home/clawbot/.openclaw/workspace"
        )
        
        # Speichern
        with open(output_file, 'w') as f:
            f.write(result.stdout)
        
        print(f"✓ {query} -> {output_file}")
    
    print(f"\nWöchentliche Recherche abgeschlossen: {week_dir}")

if __name__ == "__main__":
    run_weekly_research()
```

### 4.2 Cron Job einrichten

```bash
# Jeden Sonntag um 18:00 automatische Recherche
0 18 * * 0 /home/clawbot/.openclaw/workspace/scripts/weekly_research.py >> /home/clawbot/.openclaw/logs/weekly_research.log 2>&1
```

---

## 5. RAG Integration

### 5.1 Knowledge Base updaten

```python
#!/usr/bin/env python3
# update_rag_index.py

import json
import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np

RESEARCH_DIR = Path("/home/clawbot/.openclaw/workspace/knowledge/research")

def load_research_files():
    """Lade alle Research-Dateien."""
    texts = []
    sources = []
    
    for md_file in RESEARCH_DIR.rglob("*.md"):
        with open(md_file, 'r') as f:
            content = f.read()
            texts.append(content)
            sources.append(str(md_file))
    
    return texts, sources

def create_chunks(texts, sources):
    """Erstelle Text-Chunks für RAG."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    chunks = []
    chunk_sources = []
    
    for text, source in zip(texts, sources):
        splits = splitter.split_text(text)
        chunks.extend(splits)
        chunk_sources.extend([source] * len(splits))
    
    return chunks, chunk_sources

def update_index():
    """Aktualisiere RAG Index."""
    print("Lade Research-Dateien...")
    texts, sources = load_research_files()
    
    print(f"Verarbeite {len(texts)} Dateien...")
    chunks, chunk_sources = create_chunks(texts, sources)
    
    print(f"Erstelle Embeddings für {len(chunks)} Chunks...")
    # Hier: Embeddings erstellen und speichern
    # (Details abhängig von gewählter Vector DB)
    
    # Speichere Metadaten
    index_data = {
        "chunks": chunks[:100],  # Limit für Demo
        "sources": chunk_sources[:100],
        "updated": str(Path.cwd())
    }
    
    with open("knowledge/rag/index.json", "w") as f:
        json.dump(index_data, f, indent=2)
    
    print("✓ RAG Index aktualisiert")

if __name__ == "__main__":
    update_index()
```

---

## ⏱️ Zeitaufwand

| Task | Dauer |
|------|-------|
| Einzelne Recherche | 10-15 Min |
| Web Fetch & Analyse | 15-20 Min |
| Strukturierte Ablage | 5-10 Min |
| Wöchentlicher Newsletter | 30-45 Min |
| RAG Index Update | 15-20 Min |

---

## 🔄 Automatisierungspotenzial

| Task | Automatisierbar | Tool/Script |
|------|-----------------|-------------|
| Web-Suche | ✅ Voll | tavily_search.py |
| Content Fetch | ✅ Voll | web_fetch_content.py |
| Zusammenfassung | ✅ Teilweise | Tavily Answer API |
| Speicherung | ✅ Voll | weekly_research.py |
| RAG Index | ✅ Voll | update_rag_index.py |
| Alert bei News | ⚠️ Teilweise | Google Alerts + Webhook |

---

## 📁 Dateistruktur (Final)

```
knowledge/
├── research/
│   ├── 2024/
│   │   ├── Q1/
│   │   ├── Q2/
│   │   └── template.md
│   ├── 2025/
│   └── archive/
├── rag/
│   ├── chunks/
│   ├── index.json
│   └── embeddings/
└── scripts/
    ├── tavily_search.py
    ├── brave_search.py
    ├── web_fetch_content.py
    ├── weekly_research.py
    └── update_rag_index.py
```

---

## 🔗 API-Dokumentation

- **Tavily:** https://docs.tavily.com
- **Brave Search:** https://brave.com/search/api/
- **OpenWebSearch:** https://openwebsearch.io

---

## 💡 Tipps

1. **Recherchefokus:** Definiere 3-5 Kernthemen für regelmäßige Recherche
2. **Automatisierung:** Starte mit manuellen Searches, automatiere dann
3. **Qualität:** Prüfe immer die Quellen, bevor du speicherst
4. **RAG:** Nutze die gespeicherten Daten für bessere AI-Antworten
