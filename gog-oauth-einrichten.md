# GOG OAuth Setup - Schritt für Schritt

## Schritt 1: Google Cloud Console

1. Gehe zu: https://console.cloud.google.com
2. Projekt erstellen (oder bestehendes nutzen)
3. Links im Menü: **APIs & Services** → **Library**

## Schritt 2: APIs aktivieren

Suchen und aktivieren:
- ☑️ Gmail API
- ☑️ Google Calendar API  
- ☑️ Google Drive API
- ☑️ Google Sheets API
- ☑️ Google Docs API
- ☑️ People API (Contacts)

## Schritt 3: OAuth Consent Screen

1. **APIs & Services** → **OAuth consent screen**
2. **External** auswählen
3. Ausfüllen:
   - App name: EmpireHazeClaw
   - User support: empirehazeclaw@gmail.com
   - Developer: empirehazeclaw@gmail.com
4. **Scopes**: Alle Gmail, Calendar, Drive, Sheets, Docs Scopes hinzufügen
5. **Test users**: Deine Email hinzufügen

## Schritt 4: Credentials erstellen

1. **Credentials** → **Create Credentials** → **OAuth client ID**
2. Application type: **Desktop app**
3. Name: EmpireHazeClaw
4. **Create**
5. **Download JSON**

## Schritt 5: Authentifizieren

```bash
# Datei speichern als: ~/client_secret.json
gog auth credentials ~/client_secret.json

# Account hinzufügen
gog auth add empirehazeclaw@gmail.com --services gmail,calendar,drive,sheets,docs,contacts
```

## Testen

```bash
# Gmail testen
gog gmail list --max 5

# Kalender testen  
gog calendar events --from 2026-01-01 --to 2026-01-31
```

---

## Hilfe

Falls Fragen: https://github.com/steipete/gog
