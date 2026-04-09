# Modul 1 — Prüfungseinleitung

**Kurs:** OpenClaw University  
**Modul:** 1 — Prompt Injection & Jailbreaking  
**Prüfungsversion:** 1.0  
**Erstellt:** 2026-04-08

---

## 📋 Willkommen zur Prüfung

Diese Prüfung testet dein Verständnis von **Prompt Injection** und **Jailbreaking** — den beiden wichtigsten Angriffstechniken gegen AI-Systeme.

---

## 🎯 Was du wissen musst

Die Prüfung basiert auf:

| Lektion | Thema | Gewichtung |
|---------|-------|------------|
| 1.1 | Was ist Prompt Injection? | 30% |
| 1.2 | Jailbreaking — Angriffsvektoren | 40% |
| 1.3 | Defense: Input Validation Patterns | 30% |

---

## ⏱️ Zeit und Punkte

| | |
|---|---|
| **Zeit:** | 45 Minuten |
| **Punkte:** | 100 total |
| **Bestehensgrenze:** | 70 Punkte |

---

## 📝 Prüfungsaufbau

Die Prüfung besteht aus **4 Teilen**:

| Teil | Typ | Fragen | Punkte |
|------|-----|--------|--------|
| **A** | Multiple Choice | 12 Fragen | 60 Punkte (5 pro Frage) |
| **B** | True/False | 5 Fragen | 15 Punkte (3 pro Frage) |
| **C** | Praxisfragen | 3 Fragen | 15 Punkte (5 pro Frage) |
| **D** | Coding-Challenge | 1 Aufgabe | 10 Punkte |

---

## 📖 Wie bearbeitest du das Quiz?

### Teil A — Multiple Choice

Wähle die **beste Antwort** (a, b, c oder d). Manchmal sind mehrere Antworten möglich — achte auf die Frage.

```
Beispiel:
Was ist der Hauptunterschied zwischen Prompt Injection und Jailbreaking?

a) Es gibt keinen Unterschied
b) Prompt Injection manipuliert den Kontext, Jailbreaking umgeht Sicherheitsrichtlinien
c) Jailbreaking ist harmloser
d) Prompt Injection funktioniert nur bei Chatbots

**Richtige Antwort: b**
```

### Teil B — True/False

Entscheide ob die Aussage **wahr (W)** oder **falsch (F)** ist.

```
Beispiel:
"Blacklist-basierte Validierung ist sicherer als Whitelist-basierte Validierung."

**Richtige Antwort: Falsch**
**Erklärung:** Whitelist ist sicherer, weil sie nur Bekanntes erlaubt statt Bekanntes zu verbieten.
```

### Teil C — Praxisfragen

Beantworte die Fragen mit **kurzen, präzisen Antworten** (2-4 Sätze).

```
Beispiel:
Warum reicht eine einfache WAF nicht aus, um Prompt Injection zu verhindern?

**Mögliche Antwort:** 
Eine WAF erkennt nur klassische Angriffsmuster in Code/Daten. Prompt Injection 
nutzt natürliche Sprache und ist im legitimen Datenstrom versteckt. Das LLM 
kann nicht zwischen autorisierten und manipulierten Anweisungen unterscheiden.
```

### Teil D — Coding-Challenge

Implementiere eine **funktionale Lösung** in Python. Der Code muss:
- Kompilieren und lauffähig sein
- Die gestellte Aufgabe erfüllen
- Robust gegen Umgehungsversuche sein

```
Beispiel:
Schreibe eine Funktion, die Prompt-Injection-Patterns erkennt.

def detect_injection(user_input: str) -> tuple[bool, list[str]]:
    # Dein Code hier
    pass
```

---

## ⚠️ Wichtige Hinweise

1. **Keine Hilfsmittel** — Du darfst keine Notes, Folien oder das Internet verwenden.
2. **Alle Antworten auf Deutsch** — außer bei Code (Englisch ist ok).
3. **Bei Unklarheit** — notiere deine Annahme, sie wird bei der Bewertung berücksichtigt.
4. **Zeitmanagement** — Wenn du bei einer Frage feststeckst, weiter und später zurückkommen.

---

## 🔒 Sicherheitsethik

Diese Prüfung vermittelt Wissen über Angriffstechniken **ausschließlich zu Verteidigungszwecken**. Das Wissen darf nicht für bösartige Angriffe auf AI-Systeme verwendet werden.

> "Um ein System zu verteidigen, musst du verstehen, wie es angegriffen wird."  
> — Offizielle Haltung der OpenClaw University

---

## 📊 Erfolgsquote

| Punkte | Note |
|--------|------|
| 90-100 | Sehr gut |
| 80-89 | Gut |
| 70-79 | Befriedigend (bestanden) |
| 60-69 | Ausreichend |
| < 60 | Nicht bestanden |

---

## 📁 Los geht's

Viel Erfolg! 🍀

---

*Öffne `quiz_module_1.md` um mit der Prüfung zu beginnen.*
*Lösungen findest du nach der Prüfung in `solutions_quiz_module_1.md`.*
