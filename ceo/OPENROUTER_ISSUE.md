# 🔴 OPENROUTER API KEY ISSUE

**Datum:** 2026-04-10
**Status:** ⚠️ HIGH PRIORITY

---

## PROBLEM

5/6 OpenRouter Fallback-Modelle geben 401 Unauthorized Errors zurück.

---

## MÖGLICHE URSACHEN

1. **API Key invalide** — Key wurde gelöscht oder zurückgesetzt
2. **API Key expired** — OpenRouter Subscription abgelaufen
3. **API Key ausgetauscht** — Neuer Key wurde generiert aber nicht eingetragen
4. **Rate Limit** — Zu viele Anfragen

---

## LÖSUNG

Master muss:

1. **OpenRouter Dashboard öffnen:** https://openrouter.ai/keys
2. **API Key prüfen** — Ist der Key noch aktiv?
3. **Neuen Key generieren** wenn nötig
4. **Key in vault.py speichern:**
   ```bash
   python3 scripts/vault.py set openrouter_key "sk-or-..."
   ```

---

## TEMPORÄRE LÖSUNG

Bis der Key erneuert ist:
- System nutzt nur das primäre Model
- Fallback-Modelle sind deaktiviert

---

## KONTEXT

OpenRouter wird für AI Completions verwendet wenn das primäre Model fehlschlägt.

Die 401 Errors zeigen dass der OpenRouter API Key nicht mehr funktioniert.

---

*Sir HazeClaw — 2026-04-10*