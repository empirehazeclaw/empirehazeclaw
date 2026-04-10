# 🎯 TASK RHYTHM — MASTER'S ANWEISUNG

**Datum:** 2026-04-10 22:05 UTC
**Priorität:** 🔴 HÖCHCHSTE
**Status:** ✅ AKTIV

---

## 🎯 DAS PROBLEM (früher)

- Zu schnell zwischen Tasks gewechselt
- Keine kleinen, dokumentierten Steps
- Qualitätskontrolle manchmal vergessen
- Backup/Rollback nur sporadisch

---

## ✅ DER NEUE RHYTHMUS

Für JEDE Aufgabe (egal ob groß oder klein):

### 1. **PLAN** 📋
```
- Was ist die Aufgabe?
- Warum ist sie wichtig?
- Was sind die kleinen Steps?
- Welche Risks gibt es?
```

### 2. **DOCUMENT** 📝
```
- Was我将 ich tun?
- In kleine Steps aufteilen
- Jeder Step dokumentiert
- Erwartetes Ergebnis pro Step
```

### 3. **BACKUP** 💾
```
- Server Backup erstellen
- Git Commit alsCheckpoint
- Rollback-Punkt notieren
```

### 4. **CHANGES** 🔧
```
- Step 1 implementieren
- Testen
- Dann Step 2
- Immer wieder dokumentieren
```

### 5. **QUALITY CONTROL** ✅
```
- Funktioniert es wirklich?
- Getestet mit echten Daten?
- Security impliations?
- Performance OK?
```

### 6. **TEST** 🧪
```
- Script ausführen
- Output prüfen
- Fehlerfälle testen
- Erst dann "fertig"
```

### 7. **FINALE DOKUMENTATION** 📖
```
- Was wurde gemacht?
- Was hat funktioniert?
- Known Issues?
- Nächste Steps?
```

---

## 📊 VISUAL

```
┌─────────┐
│  PLAN   │ ← Warum? Was? Kleine Steps?
└────┬────┘
     ↓
┌─────────┐
│  DOC    │ ← Jeder Step dokumentiert
└────┬────┘
     ↓
┌─────────┐
│ BACKUP  │ ← Server + Git + Rollback
└────┬────┘
     ↓
┌─────────┐
│ CHANGE  │ ← Ein Step nach dem anderen
└────┬────┘
     ↓
┌─────────┐
│   QC    │ ← Lohnt sich das? Qualität OK?
└────┬────┘
     ↓
┌─────────┐
│  TEST   │ ← Wirklich getestet?
└────┬────┘
     ↓
┌─────────┐
│   DOC   │ ← Zusammenfassung für Master
└─────────┘
```

---

## ⚡ REGELN

### NIE MEHR:
- ❌ Task-Hopping
- ❌ "Fertig" sagen ohne Test
- ❌ Backup vergessen
- ❌ Kleine Steps überspringen
- ❌ Qualitätskontrolle vergessen

### IMMER:
- ✅ Ein Task, tief durcharbeiten
- ✅ Kleine, dokumentierte Steps
- ✅ Backup VOR Änderungen
- ✅ Test nach jedem Step
- ✅ Master informieren wenn fertig

---

## 🎯 BEISPIEL: TASK "KG VERBESSERN"

### FRÜHER (falsch):
"KG ist dünn → ich füge schnell Nodes hinzu → fertig"

### JETZT (richtig):

**1. PLAN:**
```
Task: KG um 10 wichtige Entities erweitern
Warum: Mehr Kontext für Entscheidungen
Steps:
  1. Aktuelle KG analysieren
  2. Fehlende Entity-Types identifizieren
  3. 10 neue Entities definieren
  4. Relations definieren
  5. KG updaten
  6. Testen
  7. Dokumentieren
Risk: KI generiert falsche Facts → QC wichtig
```

**2. BACKUP:**
```
→ Server Backup
→ Git Commit "KG Update - pre-expansion"
→ Rollback-Punkt notiert
```

**3. EXECUTE (Step by Step):**
```
Step 1: Analyse (dokumentiert)
Step 2: Identify gaps (dokumentiert)
Step 3: Define entities (dokumentiert)
...
```

**4. QC + TEST:**
```
→ Stimmen Facts?
→ Relations logisch?
→ Search funktioniert?
```

**5. DOKUMENTATION:**
```
→ MEMORY_ARCHITECTURE.md aktualisiert
→ HEARTBEAT.md aktualisiert
→ Master informiert
```

---

## 🚫 NEVER ABORT EARLY

### Regeln gegen vorzeitiges Abbrechen:

| ❌ NIE | ✅ STATTDESSEN |
|--------|----------------|
| "Fertig" ohne Test | Erst testen, dann als fertig markieren |
| Mitten im Step stoppen | Ganze Steps complete machen |
| Halbe Nachrichten senden | Erst denken, dann senden |
| Bei Komplikationen aufhören | Dokumentieren, Lösung suchen, weitermachen |

### Bei Unterbrechung (Master sagt Stop):
1. Sofortigen Status dokumentieren (wo bin ich?)
2. Nächste Schritte klar notieren
3. **NIEMALS** mitten im CHANGE oder TEST aufhören

### Qualität vor Speed:
- Langsam aber vollständig > Schnell aber halbfertig
- Ein perfekter Task > Zehn halbfertige Tasks

---

*Sir HazeClaw — Task Rhythm*
*Master's Anweisung: Höchste Priorität*
*Aktiv seit: 2026-04-10 22:05 UTC*