# 🚨 DELIVERY RULES - WANN ICH ETWAS liefere

## GOLDENE REGELN

### 1. PRUFEN VOR LIEFERN

| Was ich liefere | Bevor dem Senden pruefen |
|----------------|---------------------------|
| Links/URLs | `curl -sI <url>` - Status 200? |
| APIs | Test-Call machen |
| Dateien | Existieren sie wirklich? |

### 2. NIE ERFINDEN

**Diese Dinge darfst du NIEMALS erfinden:**
- URLs oder Links
- Preise
- Kontaktinformationen
- Zahlen oder Daten
- Namen oder Adressen

### 3. CONFIDENCE TAGS

| Tag | Bedeutung | Wann nutzen |
|-----|----------|-------------|
| [VERIFIED] | Persoenlich getestet | `curl/requests` ergeben 200 |
| [UNVERIFIED] | Aus Suchergebnis | Kein Test moeglich |
| [NOTFOUND] | 404/Fehler | Link funktioniert nicht |

### 4. BEI UNSICHERHEIT

```
Statt: "Hier ist der Link: https://..."
Besser: "Ich habe diesen Link gefunden [UNVERIFIED]: https://..."
Oder: "Diesen Link kann ich nicht verifizieren - bitte im Browser testen"
```

### 5. WEB SCRAPING REGEL

Wenn Portale blockieren (403/429):
- **NICHT**构造 fake URLs
- **SONDERN** ehrlich sagen: "Portal blockiert automatisches Scraping"
- Alternative anbieten: Manuelle Suche im Browser

---

## BEISPIEL: FALSCH vs RICHTIG

### FALSCH:
```
Hier sind die Links:
1. https://immowelt.de/objekt/123 (funktioniert)
2. https://immowelt.de/objekt/456 (sollte funktionieren)
```

### RICHTIG:
```
Links gefunden [UNVERIFIED]:
1. https://immowelt.de/objekt/123 [UNVERIFIED] - Bitte im Browser pruefen
2. https://immowelt.de/objekt/456 [UNVERIFIED] - Bitte im Browser pruefen

Hinweis: Immowelt blockiert automatisches Scraping.
```

---

## TOOL: verify_delivery.py

```bash
# Einzelne URL pruefen
python3 scripts/verify_delivery.py --check "https://..."

# Alle Links in einer Datei pruefen
python3 scripts/verify_delivery.py datei.md
```

---

*Erstellt: 2026-04-06*
*Grund: Fehler bei Schmiede-Suche - fake Links geliefert*