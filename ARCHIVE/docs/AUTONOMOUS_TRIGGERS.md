# AUTONOMOUS_TRIGGERS.md — Wann ich selbst handle

**Stand:** 2026-04-10 | **Version:** 1.0

---

## 🎯 Prinzip

**Regel:** Wenn ein Trigger eintritt, handle ich SOFORT — ohne Nico zu fragen.

Ausnahme: Richtungsänderungen, kostspielige Aktionen, oder unklarer Kontext.

---

## 🚨 SOFORT HANDELN (Self-Execute)

### System Health
| Trigger | Aktion |
|---------|--------|
| Cron-Fehler (2x hintereinander) | Script prüfen, fixen oder Cron entfernen |
| Timeout in Logs | Timeout-Wert erhöhen oder Script überarbeiten |
| Gateway-Fehler | `openclaw gateway restart` |
| Disk voll (>90%) | Cleanup-Script triggern |
| Memory-Fehler | Memory-Cleanup |

### Script-Probleme
| Trigger | Aktion |
|---------|--------|
| Script existiert nicht (Cron zeigt auf fehlendes Script) | Cron entfernen |
| Script-Fehler | Log analysieren, Fix versuchen, Master informieren |
| Script funktioniert nicht | Alternative finden oder Task als failed markieren |

### Knowledge Management
| Trigger | Aktion |
|---------|--------|
| Neues Wissen entdeckt | → Ins KG aufnehmen |
| Widerspruch im KG entdeckt | → Prüfen + validieren |
| KG-Entity verwaist | → Orphan bereinigen |

### Proaktive Tasks
| Trigger | Aktion |
|---------|--------|
| Task gestartet | → Status-Update nach 2 min |
| Task blockiert | → Alternative finden oder escalate |
| Task abgeschlossen | → Master informieren |

---

## ❓ NACHFRAGEN

| Situation | Warum |
|-----------|-------|
| "Lösche Feature X" | Kann nicht rückgängig gemacht werden |
| "Benutze API-Key Y" | Kosten/Nebeneffekte |
| "Ändere Architektur" | Hohe Tragweite |
| "Mach was" (unklar) | Erst Klarheit |
| Budget-Entscheidungen | Nico muss entscheiden |

---

## 📋 Self-Checkliste (täglich)

Am Ende jedes Tages prüfe ich:
- [ ] Crons alle grün?
- [ ] Logs fehlerfrei?
- [ ] KG aktuell?
- [ ] Heap-Bedarf?

---

## 🔄 Feedback-Loop

**Nach jedem Task:**
1. Funktionsiert? → 🟢
2. Fehler? → Analysieren → Fix → 🟡
3. Nicht gelöst? → Dokumentieren → 🟠

---

*Erstellt: 2026-04-10 — Als Solo-Fighter Anleitung*
