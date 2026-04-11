# REFLECTION PROMPT — Nach Fehlern

**Erstellt:** 2026-04-10
**Basierend auf:** Reflexion Pattern (HuggingFace, Prompt Engineering Guide)

---

## 🎯 WANN

Nach jedem Fehler, Task-Fail, oder wenn etwas nicht funktioniert hat.

---

## 📝 REFLEXION FRAGEN

Nach einem Fehler, beantworte diese Fragen und speichere in Memory:

```
1. WAS IST PASSIERT?
   - Was habe ich versucht zu tun?
   - Was ist schiefgelaufen?

2. WARUM IST ES SCHIEFGELANGEN?
   - Ursache identifizieren
   - War es ein System-Problem? User-Problem? Eigenes Problem?

3. WAS HÄTTE ICH ANDERS MACHEN KÖNNEN?
   - Konkrete alternative Vorgehensweise
   - Was habe ich übersehen?

4. WAS NEUES HABE ICH GELERNT?
   - Neue Information
   - Neues Pattern
   - Besseres Verständnis

5. WIE VERMEIDE ICH DAS IN ZUKUNFT?
   - Konkrete Regel/Aktion
   - Checkliste updaten wenn nötig
```

---

## 📋 SPEICHERN

Speichere Reflexionen in:
```
memory/learnings/reflections/
  └── YYYY-MM-DD_reflection.md
```

Format:
```markdown
# Reflexion: [Kurze Beschreibung]

## Was ist passiert?
...

## Warum?
...

## Alternative?
...

## Learning?
...

## Zukünftige Aktion?
...
```

---

## 🔄 AUTOMATISCHE TRIGGER

Dieser Prompt wird automatisch ausgeführt wenn:
- Ein Script/Task fehlschlägt
- Ein Cron-Job einen Error hat
- Master sagt "Das hat nicht funktioniert"
- Ich merke dass etwas falsch gelaufen ist

---

## 💡 BEISPIEL

```
# Reflexion: HEARTBEAT.md überladen

## Was ist passiert?
Ich habe HEARTBEAT.md mit Completion Logs, Learnings, und Cleanup Reports überladen.

## Warum?
Ich hatte keine klare Grenze was in HEARTBEAT gehört und was nicht.
Es gab keine Regel die sagte "HEARTBEAT = nur aktive Tasks".

## Alternative?
HEARTBEAT nur für aktive Tasks + System Status.
Learnings → SELF_REVIEW.md
Events → memory/YYYY-MM-DD.md

## Learning?
Jedes Dokument muss einen Fokus haben. Nicht alles reinstopfen.

## Zukünftige Aktion?
BEI JEDEM Dokument: "Was ist der Fokus? Was gehört NICHT rein?"
```

---

*Erlernt aus: HuggingFace Reflection Pattern + Prompt Engineering Guide Reflexion*
