# OAuth Client ID erstellen - Schritt für Schritt

## Schritt 1: Zu Credentials gehen

1. Gehe zu: https://console.cloud.google.com/apis/credentials
2. Stelle sicher, dass oben rechts dein **EmpireHazeClaw** Projekt ausgewählt ist

---

## Schritt 2: Create Credentials

1. Klicke auf den Button **"+ Credentials erstellen"** (blau)
2. Wähle **OAuth-Client-ID**

---

## Schritt 3: Application type

1. Bei "Application type" wähle **Desktop-App**
2. (NICHT Web Application!)

---

## Schritt 4: Name vergeben

1. Name eingeben: `EmpireHazeClaw`
2. Klicke auf **Erstellen**

---

## Schritt 5: Herunterladen

1. Es erscheint ein Popup mit Client ID und Client Secret
2. Klicke auf **OAuth-Client herunterladen** (JSON)
3. Speichere die Datei!

---

## Schritt 6: Datei auf Server laden

Die heruntergeladene Datei heißt wahrscheinlich:
`client_secret_XXXX.apps.googleusercontent.com.json`

**Option A: Per Email an mich**
- Datei als Attachment an empirehazeclaw@gmail.com

**Option B: Direkt hochladen**
- Ich kann sie nicht selbst hochladen

---

## Schritt 7: GOG Authentifizieren

Sobald die Datei auf dem Server ist:
```bash
gog auth credentials ~/client_secret_XXXX.json
gog auth add empirehazeclaw@gmail.com --services gmail,calendar,drive,sheets,docs
```

---

## ⚠️ FAQ

**Q: Ich sehe "Application type" nicht**
A: Stelle sicher, dass du bei OAuth consent auf "External" geklickt hast

**Q: Kann keine Credentials erstellen**
A: OAuth Consent muss erst konfiguriert sein (Schritt 3 vorher)

**Q: Download funktioniert nicht**
A: Klicke stattdessen auf die Client ID in der Liste, dann siehst du die Werte

---

## ✅ Checkliste

- [ ] Projekt ausgewählt
- [ ] "+ Credentials erstellen" geklickt
- [ ] "OAuth-Client-ID" gewählt
- [ ] "Desktop-App" ausgewählt
- [ ] Name: EmpireHazeClaw
- [ ] Erstellen
- [ ] JSON heruntergeladen

---

*Bei Problemen: Screenshot schicken!*
