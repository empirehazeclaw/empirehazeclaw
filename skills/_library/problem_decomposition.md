# 🧩 Problem Decomposition Skill
**Created:** 2026-04-11
**Category:** workflow
**Priority:** HIGH

## Problem
Große Tasks werden nicht geschafft → Timeout, Loop, Frustration.

## Lösung
**Jeden großen Task in kleine Stücke teilen.**

## Rule of Thumb
```
MAX SINGLE STEP TIME: 60-90 Sekunden
→ Alles was länger dauert = aufteilen
```

## Decomposition Framework

### Step 1: Identify
```
Input: "Erstelle komplettes Backup System"
Output: Kleine Steps:
  1. Backup Script schreiben
  2. Backup Verzeichnis erstellen
  3. Test mit 1 File
  4. Full Backup
  5. Verify Script
```

### Step 2: Size Each Step
```
Step muss sein:
- Max 60-90s Ausführungszeit
- Prüfbares Ergebnis
- Reversible (falls Fehler)
```

### Step 3: Execute & Verify
```
For each step:
  1. Do it
  2. Test it  
  3. If fail → Fix & Document
  4. Next step
```

### Step 4: Combine
```
Nach dem letzten Step:
→ Everything works together
→ Dokumentieren
→ Pattern extrahieren
```

---

## Examples

### BAD: Alles auf einmal
```
❌ "Migriere Datenbank"
  → Timeout nach 60s
  → Alles kaputt
```

### GOOD: Schritt für Schritt
```
✅ "Migriere Datenbank"
  Step 1: Export Schema (10s)
  Step 2: Test Export (5s)
  Step 3: Import Schema (10s)
  Step 4: Export Data Batch 1 (30s)
  Step 5: Export Data Batch 2 (30s)
  Step 6: Verify All (10s)
  → Fertig!
```

---

## Signal Words (Stop and Decompose!)

| Signal | Meaning | Action |
|--------|---------|--------|
| "komplett" | Großer Task | Decompose! |
| "Migration" | Viele Steps | Decompose! |
| "Alle Dateien" | Batch nötig | Decompose! |
| "Datenbank" | Risiko | Decompose! |
| > 1 Minute geschätzt | Zu groß | Decompose! |

---

## Anti-Patterns

❌ ** NICHT:
- "Das mach ich schnell" (wird nicht schnell)
- "Ich fang einfach an" (kein Plan)
- "Step 2 kann ich später" (technical debt)

✅ ** SONDERN:
- 2 Minuten Planung → 5 Minuten Ausführung
- Jeder Step testbar
- Am Ende: Alles funktioniert

---

## Workflow Checklist

- [ ] Task ist > 60s?
- [ ] In Steps aufgeteilt?
- [ ] Jeder Step < 60s?
- [ ] Testbar nach jedem Step?
- [ ] Ergebnis dokumentiert?

---

*Sir HazeClaw — Decomposition Master*
