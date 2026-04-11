# Google Cloud OAuth Consent - Schritt für Schritt

## Schritt 1: Projekt erstellen

1. Gehe zu: https://console.cloud.google.com/
2. Klick oben auf **Projekt auswählen** 
3. Klick auf **Neues Projekt**
4. Name: `EmpireHazeClaw`
5. Klick auf **Erstellen**
6. Warten bis Projekt erstellt ist

---

## Schritt 2: APIs aktivieren

1. Links im Menü: **APIs & Services** → **Library**
2. Suche und aktiviere nacheinander:

| API | Suchbegriff |
|-----|-------------|
| Gmail API | `gmail` |
| Google Calendar API | `calendar` |
| Google Drive API | `drive` |
| Google Sheets API | `sheets` |
| Google Docs API | `docs` |
| People API | `people` |

**Für jede API:**
1. Suchen
2. **Enable** klicken

---

## Schritt 3: OAuth Consent Screen

1. Links: **APIs & Services** → **OAuth consent screen**
2. Wähle **External**
3. Klick auf **Create**

### Formular ausfüllen:

| Feld | Eingabe |
|------|----------|
| App name | `EmpireHazeClaw` |
| User support email | `empirehazeclaw@gmail.com` |
| Developer contact | `empirehazeclaw@gmail.com` |
| App logo | (Optional) |

4. **Save and Continue**
5. **Scopes**:
   - Klick auf **Add or remove scopes**
   - Scopes hinzufügen:
     - `.../auth/gmail.readonly`
     - `.../auth/gmail.send`
     - `.../auth/calendar`
     - `.../auth/drive`
     - `.../auth/spreadsheets`
     - `.../auth/documents`
   - **Update** klicken
6. **Save and Continue**
7. **Test users**:
   - Klick auf **Add users**
   - Eigene Email eingeben: `empirehazeclaw@gmail.com`
   - **Save and Continue**

---

## Schritt 4: OAuth Credentials erstellen

1. Links: **Credentials**
2. **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Name: `EmpireHazeClaw Desktop`
5. **Create**
6. **Download JSON**
7. Datei speichern als: `oauth_credentials.json`

---

## Schritt 5: GOG authentifizieren

```bash
# Datei auf Server laden (falls nötig)
# Dann:

gog auth credentials ~/oauth_credentials.json
gog auth add empirehazeclaw@gmail.com --services gmail,calendar,drive,sheets,docs,contacts

# Testen
gog gmail list --max 3
```

---

## ⚠️ Wichtig

- Bei "App not verified" → Trotzdem auf **Advanced** → **Go to EmpireHazeClaw (unsafe)**
- Oder: App als "Test" veröffentlichen (Test user reicht erstmal)

---

## ✅ Checkliste

- [ ] Projekt erstellt
- [ ] 6 APIs enabled
- [ ] OAuth Consent konfiguriert
- [ ] Test user eingetragen
- [ ] Credentials heruntergeladen
- [ ] GOG authentifiziert

---

*Erstellt: 2026-03-16*
