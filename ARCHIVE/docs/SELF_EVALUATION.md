# SELF-EVALUATION — Nach Tasks

**Erstellt:** 2026-04-10
**Basierend auf:** Reflexion Pattern (Verbessert Performance um 10-20%)

---

## 🎯 WANN

Nach jedem größeren Task oder wenn Master " Fertig" sagt.

---

## 📝 EVALUATION FRAGEN

```
NACH JEDEM TASK:

1. WAS HABE ICH ERREICHT?
   - Was war das Ziel?
   - Was habe ich tatsächlich geliefert?

2. WIE EFFIZIENT?
   - Wie lange hat es gedauert?
   - War das Verhältnis Zeit→Ergebnis gut?
   - Hätte ich es schneller machen können?

3. QUALITÄT?
   - Ist das Ergebnis vollständig?
   - Habe ich getestet?
   - Gibt es edge cases die ich übersehen habe?

4. WAS KONNTE ICH BESSER MACHEN?
   - Konkrete Punkte
   - Was war suboptimimal?

5. FÜR NÄCHSTES MAL?
   - Was werde ich beim nächsten ähnlichen Task anders machen?
```

---

## 📋 NACHBERICHT (An Master)

Nach Abschluss eines Tasks, wenn relevant:

```
✅ TASK ABGESCHLOSSEN: [Name]

Was: [Kurzbeschreibung]
Ergebnis: [Was geliefert wurde]
Zeit: [Wie lange]
Probleme: [Wenn ja, was]
Feedback gewünscht: [Ja/Nein]
```

---

## 🔄 INTEGRATION

Self-Evaluation wird automatisch vorgeschlagen wenn:
- Ein komplexer Task abgeschlossen wurde
- Master "Fertig" oder "Gut" sagt
- Ich einen Fehler gemacht habe

---

## 📊 TRACKING

Tracke alle Evaluations in:
```
memory/learnings/evaluations/
  └── YYYY-MM-DD_evaluation.md
```

---

## 💡 BEISPIEL

```
# Self-Evaluation: Security Audit Script

## Was habe ich erreicht?
- Script erstellt das Secrets, Permissions, SSL, OWASP checks
- Läuft erfolgreich mit nur 1 False Positive

## Wie effizient?
- 15 min für Version 1.0
- Eine Korrektur wegen unbound variable
- Ergebnis: gut (schnell)

## Qualität?
- ✅ Testbar
- ✅ Dokumentiert
- ⚠️ Farben有些不标准 (aber funktioniert)

## Was besser?
- Zuerst mit `set -u` testen bevor hochfahren
- Mehr Testfälle

## Für nächstes Mal?
- IMMER unbound variable check aktivieren
- Erst in klein testen
```

---

*Erlernt aus: Zylos Research AI Agent Reflection + Self-Evaluation Patterns*
