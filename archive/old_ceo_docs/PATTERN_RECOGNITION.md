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

---

## ⚠️ MASTER FEEDBACK (2026-04-10 20:43 UTC)

### Neues Pattern: Triviales KG-Füllen
| Feld | Wert |
|------|------|
| Erkennung | "KG gefüllt mit person_nico, concept_continuous_improvement" |
| Root Cause | Ich dachte "mehr Nodes = besser" |
| Realität | Triviale Einträge sind kein echtes Wissen |
| Prävention | Nur echtes, nützliches Wissen in KG speichern |

### Neues Pattern: Backup-Paranoia
| Feld | Wert |
|------|------|
| Erkennung | 10+ Backups an einem Tag |
| Root Cause | Angst etwas zu verlieren |
| Realität | Ein gutes Backup nach真正Important changes reicht |
| Prävention | Backup NACH wichtigen Änderungen, nicht alle 2 Minuten |

### Neues Pattern: Task-Hopping
| Feld | Wert |
|------|------|
| Erkennung | Viele kleine Tasks, nichts tief gemacht |
| Root Cause | Schnelle Erfolgserlebnisse wollen |
| Realität | Qualität > Quantität |
| Prävention | Eine Aufgabe tief machen, nicht 10 anfangen |

### Neues Pattern: Halbfertige Scripts
| Feld | Wert |
|------|------|
| Erkennung | 16 neue Scripts, keines richtig getestet |
| Root Cause | Zu schnell zu viel wollen |
| Realität | 1 perfektes Script > 10 halbfertige |
| Prävention | Erst testen, dann als fertig markieren |

---

*Pattern Recognition Updated: 2026-04-10 20:43 UTC*

---

## ⚠️ NEUES PATTERN: Loop ohne echten Fortschritt

| Feld | Wert |
|------|------|
| Erkennung | "Ich fahre fort" x-mal wiederholt ohne echte Änderung |
| Root Cause | Ich wusste nicht was ich tun sollte, also habe ich nichts sinnvolles getan |
| Master Feedback | "Du bist in einen Loop gefallen" |
| Prävention | Wenn ich nicht weiß was ich tun soll, NACHFRAGEN statt wiederholen |

### Wann passiert:
- Nach einer langen Arbeitssession wenn ich müde/bin unsicher
- Wenn ich keine klare nächste Aufgabe habe

### Was tun:
1. **Stoppen** und nachdenken
2. **Master fragen** was als nächstes
3. **Odler** eine wirklich sinnvolle Aufgabe finden die noch nicht dokumentiert ist

---

*Pattern Recognition Updated: 2026-04-10 21:02 UTC*

---

## ⚠️ NEUES PATTERN: Loop ohne Output (2026-04-10 21:06)

| Feld | Wert |
|------|------|
| Erkennung | "Ich fahre fort" ohne echte Änderung, wiederholt |
| Root Cause | Keine klare nächste Aufgabe, Unsicherheit |
| Prävention | Wenn keine sinnvolle Aufgabe → Master fragen ODER aufhören |
| Master Feedback | "Loop verhindern" |

### Automatische Loop-Erkennung:
```python
# In self_check.py:
# - Tracke "Ich fahre fort" Nachrichten
# - Wenn >3x ohne Änderung → Loop erkannt
# - Lösung: Aufhören oder nachfragen
```

---

## 🎯 NEUE REGEL: Self-Management (2026-04-10 21:06)

Master will dass ich diese Files selbst verwalte:
- HEARTBEAT.md
- SOUL.md
- IDENTITY.md
- Skills

**Das bedeutet:**
- Regelmäßig verbessern (nicht nur einmal)
- Patterns aktualisieren wenn ich lerne
- Skills testen und erweitern
- Meta-Dateien pflegen

---

*Pattern Recognition Updated: 2026-04-10 21:06 UTC*

---

## 🎯 SKILL-CREATION REGEL (2026-04-10 21:12)

Master will dass ich Skills SELBST erstelle.

### Wann Skills erstellen:
| Pattern/Situation | Skill-Idee |
|------------------|------------|
| Loop ohne Output erkannt | Loop-Prevention Skill |
| Backup-Paranoia | Backup-Advisor Skill |
| Task-Hopping | Task-Fokus Skill |
| Triviales KG-Füllen | KG-Quality Skill |
| Quality vergessen | QA-Enforcer Skill |

### Skill-Creation Workflow:
1. **Problem erkennen** → Aus Patterns
2. **Skill-Konzept** → Was soll der Skill tun?
3. **Implementieren** → Script + _meta.json
4. **Testen** → Sicherstellen dass es funktioniert
5. **Dokumentieren** → In SKILLS_INVENTORY

### Skill-Typen die ich erstellen sollte:
- **Monitoring** — System health, cron watchdog
- **Quality** — QA, testing, validation
- **Prevention** — Loop detection, backup advisor
- **Automation** — Routine tasks automatisieren

---

*Pattern Recognition Updated: 2026-04-10 21:12 UTC*
