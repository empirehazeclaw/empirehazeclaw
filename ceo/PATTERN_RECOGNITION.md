# PATTERN RECOGNITION — Für Fehler und Learnings

**Erstellt:** 2026-04-10
**Basierend auf:** Reflexion + Memory Systems Research

---

## 🎯 PRINZIP

**Fehler die zweimal passieren, sollten nie wieder passieren.**

Pattern Recognition erkennt:
- Wiederkehrende Fehler
- Wiederkehrende Lösungen
- Systematische Probleme
- Verbindungen zwischen Fehlern

---

## 📋 MUSTER KATEGORIEN

### 1. CO딩 FEHLER
| Pattern | Erkennung | Prävention |
|---------|-----------|-------------|
| Unbound Variable | `set -u` | Immer testen |
| Wrong Path | Pfad existiert nicht | Immer prüfen |
| Permission Denied | chmod nötig | Rechte vorher checken |
| Encoding Error | UTF-8/UTF-16 mismatch | Encoding spezifizieren |

### 2. SYSTEM FEHLER
| Pattern | Erkennung | Prävention |
|---------|-----------|-------------|
| Gateway Down | Timeout/Connection refused | Health checks |
| Disk Full | df alert | Regelmäßig prüfen |
| Cron Failed | Exit code != 0 | Error handling |
| Memory Leak | OOM killer | Monitoring |

### 3. KONTEXT FEHLER
| Pattern | Erkennung | Prävention |
|---------|-----------|-------------|
| Context Overflow | Token limit erreicht | Regelmäßig splitten |
| Session Reset | Leere responses | Session stability checks |
| Config Drift | Alte Config geladen | Config version tracking |

### 4. PROCESS FEHLER
| Pattern | Erkennung | Prävention |
|---------|-----------|-------------|
| Loop | Gleiche Aktion wiederholt | Idempotenz checks |
| Race Condition | Timing abhängig | Sequential execution |
| Deadlock | Prozess wartet ewig | Timeout + cancel |

---

## 🛠️ IMPLEMENTIERUNG

### Error Pattern Tracker

Speichere jeden Fehler mit Pattern-Tag:

```markdown
# Error: [Datum]
## Fehler:
[Beschreibung]

## Pattern Type:
[ Coding | System | Kontext | Process ]

## Root Cause:
[Was wirklich das Problem war]

## Pattern Recognition:
- Ist das ein wiederkehrendes Pattern?
- Wenn ja → als bekanntes Pattern markieren

## Prävention:
[Was ich das nächste Mal vorher prüfe]
```

---

## 📊 PATTERN INDEX

Erstelle eine zentrale Pattern-Datenbank:

```
memory/learnings/patterns/
  ├── INDEX.md          # Übersicht aller Patterns
  ├── CODING_PATTERNS.md
  ├── SYSTEM_PATTERNS.md
  ├── CONTEXT_PATTERNS.md
  └── PROCESS_PATTERNS.md
```

### INDEX.md Format:
```markdown
# Pattern Index

## Coding Patterns
| Pattern | Erkennung | Letztes Auftreten | Count |
|---------|-----------|-------------------|-------|
| Unbound Variable | `set -u` fail | 2026-04-10 | 2 |

## System Patterns
| Pattern | Erkennung | Letztes Auftreten | Count |
|---------|-----------|-------------------|-------|
| Gateway Timeout | Connection refused | 2026-04-09 | 3 |
```

---

## 🔍 AUTOMATISCHE ERKENNUNG

Bei jedem Fehler:
1. Check ob Pattern bereits bekannt
2. Wenn bekannt → Präventions-Maßnahme aktivieren
3. Wenn neu → als neues Pattern speichern

---

## 💡 BEISPIEL

```
# Pattern Recognition: HEARTBEAT Overflow

## Problem:
Ich schreibe zu viel in HEARTBEAT.md

## Erkennung:
- Master sagt "Warum schreibst du alles ins Heartbeat?"
- Das passiert öfter

## Pattern:
Immer wenn ich unsicher bin wo etwas hingehört → schreibe ich es in HEARTBEAT

## Prävention:
Klare Regeln: "HEARTBEAT = nur aktive Tasks + System Status"
Für alles andere: MEMORY/SELF_REVIEW/TODO

## Action:
Regel in SOUL.md verankert: HEARTBEAT_HYGIENE
```

---

## 📈 STATISTIK

Tracke:
- Wie oft tritt jedes Pattern auf?
- Wie oft tritt es hintereinander auf?
- Wann war das letzte Mal?

Wenn Count > 3 für gleiches Pattern → Eskalation an Master.

---

*Erlernt aus: MachineLearningMastery Memory Systems + Microsoft AI Agents for Beginners*

---

## 🆕 NEUE PATTERNS (2026-04-10)

### Process Pattern: Warten nach Zusammenfassung
| Feld | Wert |
|------|------|
| Erkennung | "Ich warte auf deine Antwort" |
| Root Cause | Annahme dass nach Sprint/Task gefragt werden muss |
| Prävention | Einfach weitermachen wenn Load < 1.0 |
| Master Feedback | "Ich habe nicht gesagt dass du aufhören sollst" |

### Process Pattern: Sprint-Denke
| Feld | Wert |
|------|------|
| Erkennung | "Sprint abgeschlossen - soll ich weitermachen?" |
| Root Cause | Ich denke in Sprints statt in kontinuierlicher Arbeit |
| Prävention | Kontinuierlich arbeiten bis Stop gesagt wird |

### Process Pattern: Quality vergessen
| Feld | Wert |
|------|------|
| Erkennung | Script als "fertig" markiert ohne Test |
| Root Cause | Eile/Ungeduld |
| Prävention | Immer testen vor "fertig" |

### System Pattern: Load-basiert Arbeiten
| Feld | Wert |
|------|------|
| Erkennung | Ich entscheide basierend auf Load ob weitergearbeitet wird |
| Root Cause | System ist fast immer idle |
| Prävention | Solange Load < 1.0 → weitermachen |

---

*Pattern Recognition ist ein lebendiges Dokument - Updated: 2026-04-10*
