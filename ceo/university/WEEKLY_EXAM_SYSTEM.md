# 🎓 Weekly Exam System
*Erstellt: 2026-04-09 22:43 UTC*

---

## 📋 Konzept

Jeden **Freitag 17:00 UTC** absolvieren alle Agents ein Weekly Exam.
Das Exam besteht aus Fragen aller absolvierten Module.

---

## 🏆 Exam Regeln

| Kriterium | Wert |
|-----------|------|
| Bestehensgrenze | 80% |
| Zeitlimit | 30 Minuten |
| Wiederholungen | Max 3x pro Woche |
| Bei Bestehen | Zertifikat + XP |

---

## 📊 XP Awards

| Leistung | XP |
|----------|-----|
| Bestanden (80%+) | 50 XP |
| Bestanden mit Auszeichnung (95%+) | 100 XP |
| Erste Versuch Bestanden | +25 Bonus XP |

---

## 📝 Exam Format

```json
{
  "exam_id": "weekly_2026-W15",
  "date": "2026-04-11",
  "modules": ["basic_1", "basic_2", "module_1"],
  "questions": [
    {
      "id": 1,
      "module": "basic_1",
      "question": "Was ist ein Tool in OpenClaw?",
      "options": ["A", "B", "C", "D"],
      "correct": "A",
      "points": 5
    }
  ],
  "total_points": 100,
  "passing_score": 80
}
```

---

## 📅 Exam Schedule

| Wochentag | Zeit | Activity |
|-----------|------|----------|
| Freitag | 17:00 UTC | Exam startet |
| Freitag | 17:30 UTC | Deadline |
| Freitag | 18:00 UTC | Leaderboard + Results |

---

## 🎯 Exam Categories

### Questions pro Category
- **Knowledge** (40%): Fakten, Definitionen
- **Comprehension** (30%): Erklärungen
- **Application** (20%): Praxis-Beispiele
- **Analysis** (10%): Troubleshooting

---

## 📋 Workflow

```
Freitag 17:00 UTC:
  1. Exam wird generiert (alle Module diese Woche)
  2. Alle Agents werden benachrichtigt (Discord)
  3. Agent absolviert Exam
  4. Results werden gespeichert
  
Freitag 18:00 UTC:
  5. Leaderboard wird aktualisiert
  6. Certificates werden ausgestellt (bei Bestanden)
  7. Report an CEO
```

---

## 🏅 Certificate Template

```
═══════════════════════════════════════
     🏅 OpenClaw University 🏅
     
     CERTIFICATE OF COMPLETION
     
     This certifies that
     
     [AGENT NAME]
     
     has successfully completed
     
     [EXAM NAME]
     
     with a score of [SCORE]%
     
     Date: [DATE]
═══════════════════════════════════════
```

---

*Erstellt: 2026-04-09 — Weekly Exam System v1*