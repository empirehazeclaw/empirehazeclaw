# POD Product Launch Workflow

**Ziel:** Schritt-für-Schritt Anleitung für den Launch eines Print-on-Demand Produkts von Design bis Etsy-Verkauf.

---

## 📋 Übersicht

| Phase | Beschreibung | Zeitaufwand |
|-------|--------------|-------------|
| Design | Konzept & Erstellung | 1-3 Std |
| Printify Upload | Produktkonfiguration | 30-60 Min |
| Etsy Listing | SEO & Beschreibung | 45-90 Min |
| Launch | Veröffentlichung & Marketing | 30 Min |

**Tools:** Canva/Figma, Printify, Etsy, ChatGPT (SEO)

---

## 1. Design Phase

### 1.1 Trend-Recherche

```bash
# Web-Suche nach aktuellen Trends
web_search --query "trending print on demand designs 2024 etsy" --count 5 --country DE --search_lang de
```

### 1.2 Design-Erstellung

**Tools:**
- Canva (canva.com) - Einsteiger
- Figma (figma.com) - Fortgeschritten
- Adobe Illustrator - Profi

**Empfohlene Dimensionen:**

| Produkt | Format | DPI |
|---------|--------|-----|
| T-Shirt | 4500 x 5400 px | 300 |
| Poster | 3300 x 5100 px | 300 |
| Tasse | 4500 x 2700 px | 300 |
| Handycase | 1080 x 1920 px | 300 |
| Hoodie | 4800 x 6000 px | 300 |

### 1.3 Design-Checkliste

- [ ] Transparenter Hintergrund (PNG)
- [ ] Farbprofil: CMYK (für Print)
- [ ] Auflösung: min. 300 DPI
- [ ] Keine Copyright-Verletzungen
- [ ] Trend-Recherche abgeschlossen

---

## 2. Printify Integration

### 2.1 Printify Konto einrichten

1. Registrierung auf printify.com
2. Mit Etsy verbinden (Settings → Integrations)
3. Shop-Autorisierung

### 2.2 Produkt erstellen

```bash
# Printify API (optional für Bulk-Upload)
# Siehe: https://developers.printify.com/
```

**Schritte im Dashboard:**
1. "Create Product" klicken
2. Produkttyp wählen (T-Shirt, Poster, etc.)
3. Provider wählen (z.B. Gelato, Prodigi)
4. Design hochladen
5. Vorschau prüfen
6. Speichern

### 2.3 Preis-Kalkulation

**Formel:**
```
Verkaufspreis = (Produktionskosten + Versand) × 2.5 + Etsy-Gebühren
```

**Beispiel-Rechnung:**

| Kostenfaktor | Betrag (€) |
|--------------|------------|
| T-Shirt Druck | 8,50 |
| Versand an Kunde | 3,50 |
| Etsy Transaktionsgebühr (6,5%) | ~1,30 |
| Zahlungsabwicklung (3% + 0,25€) | ~0,65 |
| **Gesamtkosten** | **~14,-** |
| **Mindestpreis (30% Marge)** | **~19,-** |
| **Empfohlener Preis** | **24,90** |

---

## 3. Etsy Listing

### 3.1 Keyword-Recherche

```bash
# Keyword-Recherche
web_search --query "etsy keywords t shirt quote funny german" --count 10 --country DE
```

**Tools:**
- Marmalead (marmalead.com)
- eRank (erank.com)
- Etsy Search Bar Autocomplete

### 3.2 Listing erstellen

**Template:**

```markdown
## TITLE
[Hauptkeyword] - [Design/Stil] - [Produkttyp] | [Unique Selling Point]

## TAGS (13 Tags, max. 20 Zeichen)
- handmade-gift
- funny-shirt
- german-quote
- ... (weitere)

## DESCRIPTION
### Produktdetails
- Material: 100% Baumwolle
- Druck: Digitaldruck
- Größen: S-XXL
- Farben: Mehrere verfügbar

### Versand
- Deutschland: 3-5 Werktage
- EU: 5-10 Werktage

### Persönliche Note
Vielen Dank für deinen Einkauf! Bei Fragen einfach melden.
```

### 3.3 SEO-Optimierung

**Title-Struktur:**
```
[Primäres Keyword] + [Sekundäres Keyword] + [Produkttyp] | [Marke/Geschäft]
```

**Beispiele:**
- "Witziges T-Shirt Deutsche Sprache Lustig Geschenk | DeinShop"
- "Handmade Poster Berlin Skyline Wandbild Vintage | UrbanArt"

**Beschreibung-Länge:** 150-300 Wörter

---

## 4. Launch Checkliste

### 4.1 Pre-Launch

- [ ] Design erstellt & geprüft
- [ ] Printify Produkt konfiguriert
- [ ] Mockups erstellt
- [ ] Keywords recherchiert
- [ ] Title optimiert
- [ ] Description geschrieben
- [ ] Tags gesetzt (13/13)
- [ ] Preis kalkuliert
- [ ] Fotos hochgeladen (min. 5)

### 4.2 Launch-Tag

- [ ] Listing veröffentlichen
- [ ] Social Media informieren
- [ ] ggf. Etsy Ads starten (5€/Tag)
- [ ] Favoriten beobachten

### 4.3 Post-Launch (Tag 1-7)

- [ ] Auf Views/Impressions achten
- [ ] Favoriten-zu-Verkauf-Ratio prüfen (>5% = gut)
- [ ] Ggf. Keywords anpassen
- [ ] Photos tauschen wenn nötig

---

## 5. Automation

### 5.1 Bulk-Upload Script

```python
#!/usr/bin/env python3
# printify-bulk-upload.py

import requests
import json
import os

PRINTIFY_API_URL = "https://api.printify.com/v1/"
API_TOKEN = os.getenv("PRINTIFY_API_TOKEN")

def upload_product(title, description, images, variants):
    """Upload product to Printify."""
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "title": title,
        "description": description,
        "images": images,
        "variants": variants
    }
    
    response = requests.post(
        f"{PRINTIFY_API_URL}shops/{SHOP_ID}/products.json",
        headers=headers,
        json=data
    )
    return response.json()

# Usage
upload_product(
    title="Witziges T-Shirt",
    description="...",
    images=[{"url": "https://..."}],
    variants=[{"id": 1, "price": 2490}]
)
```

### 5.2 Etsy Repricing (optional)

```bash
# Wöchentliche Preisprüfung
0 9 * * 0 /home/clawbot/.openclaw/workspace/scripts/etsy-repricing.sh >> /home/clawbot/.openclaw/logs/etsy-repricing.log 2>&1
```

---

## ⏱️ Zeitaufwand (pro Produkt)

| Phase | Dauer |
|-------|-------|
| Trend-Recherche | 15 Min |
| Design erstellen | 1-2 Std |
| Printify Upload | 30 Min |
| Etsy Listing | 45 Min |
| Launch & Marketing | 30 Min |
| **Gesamt** | **~3-4 Std** |

---

## 💰 Potenzielle Einnahmen

| Produkt | Kosten | Verkaufspreis | Marge |
|---------|--------|---------------|-------|
| T-Shirt | ~12€ | 24,90€ | ~9€ |
| Poster | ~5€ | 19,90€ | ~12€ |
| Tasse | ~6€ | 17,90€ | ~9€ |
| Hoodie | ~18€ | 39,90€ | ~15€ |

---

## 📁 Dateistruktur

```
knowledge/workflows/
├── pod/
│   ├── designs/
│   │   ├── tshirt/
│   │   ├── poster/
│   │   └── mugs/
│   ├── mockups/
│   ├── listings/
│   │   ├── template.md
│   │   └── executed/
│   └── analytics/
└── scripts/
    ├── printify-upload.py
    └── etsy-stats.py
```

---

## 🔗 Nützliche Links

- Printify: https://printify.com
- Etsy Seller Handbook: https://www.etsy.com/seller-handbook
- eRank: https://www.erank.com
- Marmalead: https://marmalead.com
