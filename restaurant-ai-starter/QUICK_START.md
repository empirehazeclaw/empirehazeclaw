# 🚀 Restaurant AI Starter Kit - Quick Start Guide

## Was ist enthalten?

### 📧 Email Prompts (55 Stück)
- `restaurant_emails.txt` - Reservierungsbestätigungen, Newsletter, Beschwerden
- `reservation_prompts.txt` - Tischmanagement, Wartezeit, Gruppen
- `review_response_prompts.txt` - Google, TripAdvisor, TheFork Antworten

### 🐍 Python Scripts (3 Stück)
- `reservation_tracker.py` - Reservierungsverwaltung
- `email_responder.py` - Automatische Email-Antworten
- `social_poster.py` - Social Media Content Planung

### 📋 Notion Template
- `notion_import.json` - Importierbare Struktur für Notion

---

## Sofort starten (10 Minuten)

### 1. Reservierungen tracken
```bash
cd restaurant-ai-starter/scripts

# Neue Reservierung
python3 reservation_tracker.py add \
  --name "Max Mustermann" \
  --phone "+49 123 456" \
  --date 2026-04-01 \
  --time 19:00 \
  --guests 4

# Tagesübersicht
python3 reservation_tracker.py summary

# Statistiken
python3 reservation_tracker.py stats
```

### 2. Email generieren
```bash
# Email zu Reservierungsanfrage generieren
python3 email_responder.py --inquiry reservation \
  --name "Max" \
  --date "01.04.2026" \
  --time "19:00" \
  --guests 4
```

### 3. Social Media Posts
```bash
# Wochenplan generieren
python3 social_poster.py --generate-week

# Einzelner Post
python3 social_poster.py --platform instagram --type menu
```

### 4. Review Antwort schreiben
Öffne `review_response_prompts.txt` und suche den passenden Prompt.

Beispiel für 5-Sterne Bewertung:
```
Schreibe eine Antwort auf:
"[Hier die Bewertung einfügen]"

Antworte in 3 Sätzen, bedanke dich persönlich.
```

---

## ChatGPT Prompts nutzen

Kopiere den gewünschten Prompt aus den TXT-Dateien in ChatGPT und passe die Variablen an.

**Beispiel:**
```
Schreibe eine Email für:
- Gast: Max Mustermann
- Datum: 01.04.2026
- Uhrzeit: 19:00
- Personen: 4
```

---

## Notion Template installieren

1. Öffne Notion
2. Importiere `notion_import.json` als Referenz
3. Erstelle die Datenbanken manuell oder nutze:
   - Notion API
   - „Notion Import" Tools von Drittanbietern

---

## Support

Fragen? Email: empirehazeclaw@gmail.com

---

*© EmpireHazeClaw 2026*
