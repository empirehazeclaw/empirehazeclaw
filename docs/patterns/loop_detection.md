# 🔄 Loop Detection & Prevention System
**Created:** 2026-04-11
**Category:** workflow
**Priority:** CRITICAL

## Problem
**55.7% aller Friction Events sind LOOPS!**
Das kostet Zeit und Ressourcen.

## Loop Types

| Type | Erkennung | Lösung |
|------|-----------|--------|
| **Retry Loop** | Gleiche Aktion wird wiederholt | Root Cause finden |
| **Plan Loop** | Immer mehr Planung, kein Tun | Minimal starten |
| **Doc Loop** | Docs werden immer wieder geändert | Fertig machen, nicht perfekt |
| **Search Loop** | Suche nach gleicher Info | KG nutzen |
| **Commit Loop** | Immer wieder committen | Einmal, fertig |

---

## Detection Rules

### 🚨 LOOP ERKENNT wenn:
1. **Retry Pattern:** Gleiche Fehlermeldung 3x+
2. **Same Tool:** Gleiches Tool wird 3x hintereinander aufgerufen
3. **Circular Plan:** Plan führt zu sich selbst zurück
4. **Repeated Search:** Gleiche Suche 2x

### ✅ NO LOOP OK:
1. **Verification:** Ergebis wird geprüft (nicht Loop)
2. **Chunking:** Verschiedene Teile eines großen Tasks
3. **User Request:** User bittet um Revision
4. **New Info:** Neue Information kam hinzu

---

## Prevention Protocol

### BEFORE every action:
```
Habe ich das schonmal versucht?
  → NEIN: Weiter
  → JA: Stopp! Root Cause finden
```

### BEFORE every retry:
```
Was ist der Root Cause?
  → Unbekannt: STOP, analysieren
  → Bekannt: Fix, dann retry
```

### BEFORE searching:
```
Habe ich das schon gesucht?
  → NEIN: Suchen
  → JA: KG oder letzte Ergebnisse nutzen
```

---

## Loop-Breaking Techniques

### 1. Stop & Document
```
STOP!
Was passiert gerade?
Was habe ich schon versucht?
Was war das Ergebnis?
Dokumentieren.
→ Jetzt neu überlegen.
```

### 2. Alternative Path
```
Derselbe Weg funktioniert nicht.
→ Anderen Weg probieren.
→ Chunking wenn groß.
```

### 3. Escalate
```
Nach 3 Versuchen:
→ Dokumentieren was ich weiß
→ Master fragen
→ Fertig bis Antwort kommt
```

---

## Anti-Patterns (VERBIETEN!)

❌ **LOOPS:**
- "Ich versuch's nochmal" (ohne Analyse)
- "Vielleicht brauch ich mehr Kontext" (Suche Loop)
- "Ich muss erst den Plan machen" (Plan Loop)
- "Lass mich nochmal lesen" (Lese Loop)
- "Ich muss das anders machen" (ohne Grund)

✅ **NO LOOPS:**
- "Ich habe das analysiert, Root Cause ist X"
- "Neuer Ansatz: Y weil Z"
- "Chunking: Teil 1 von 3"
- "User hat um Revision gebeten"

---

## Workflow

```
DETECT LOOP
    ↓
STOP & DOCUMENT
    ↓
ROOT CAUSE
    ↓
FIX oder MASTER FRAGEN
    ↓
CONTINUE (neuer Weg)
```

---

## Metrics

**Loop Rate:**
```
(loop_detections / total_actions) × 100
```

Ziel: < 10% (von 55.7%)

---

## Remember

**"Bewährten Weg wiederholen ist OK — aber nicht denselben Weg wiederholt versuchen!"**

---

*Sir HazeClaw — Loop-Free Since 2026*
