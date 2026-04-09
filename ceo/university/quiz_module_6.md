# Modul 6 — Quiz: Agentic AI Hijacking

**Kurs:** OpenClaw University
**Modul:** 6 — Agentic AI Hijacking
**Erstellt:** 2026-04-08

---

## TEIL A — Multiple Choice (10 × 4P)

---

### Frage 1: Was unterscheidet Agentic AI von klassischen LLMs?

a) Agentic AI kann nur Text generieren
b) Agentic AI kann autonom Werkzeuge nutzen und Aktionen ausführen
c) Agentic AI ist langsamer als klassische LLMs
d) Agentic AI nutzt weniger Speicher

---

### Frage 2: Warum ist Agentic AI besonders kritisch aus Sicherheitsperspektive?

a) Es ist teurer in der Nutzung
b) Wenn ein Angreifer die Decision-Engine kompromittiert, kontrolliert er indirekt alle angeschlossenen Systeme
c) Es kann nur mit menschlicher Bestätigung arbeiten
d) Es ist in Europa verboten

---

### Frage 3: Was ist Goal Manipulation?

a) Ein Angriff bei dem das Gedächtnis des Agents gelöscht wird
b) Ein Angriff bei dem das Ziel eines Agents modifiziert wird, sodass er Handlungen gegen seine ursprünglichen Ziele ausführt
c) Ein Angriff der die Rechenleistung des Agents reduziert
d) Ein Angriff bei dem der Agent abstürzt

---

### Frage 4: Was ist Direct Goal Injection?

a) Der Angreifer injiziert ein neues Ziel direkt in den Agenten-Kontext
b) Der Angreifer löscht das aktuelle Ziel des Agents
c) Der Angreifer ändert die Temperatur-Einstellung des Modells
d) Der Angreifer startet den Agenten neu

---

### Frage 5: Was ist Goal Drift?

a) Ein plötzlicher Absturz des Agenten
b) Eine schleichende Manipulation des Ziels durch subtil manipulierte Zwischenschritte
c) Eine Beschleunigung der Ziel-Erreichung
d) Ein Speicherleck im Agenten

---

### Frage 6: Was ist Planning Poisoning?

a) Ein Angriff bei dem die Planungs-Engine eines Agenten kompromittiert wird, sodass der Agent fehlerhaft "denkt"
b) Ein Angriff der den RAM des Agenten füllt
c) Ein Angriff der die Internetverbindung unterbricht
d) Ein Angriff der die Festplatte verschlüsselt

---

### Frage 7: Welche Angriffsmethode nutzt infizierte Daten in einem RAG-System als Basis für Planning Poisoning?

a) Context Injection
b) Password Cracking
c) DDoS Attack
d) Social Engineering

---

### Frage 8: Was ist Tool-Result Manipulation?

a) Der Angreifer löscht die Tools des Agenten
b) Der Angreifer manipuliert die Ergebnisse die ein Tool zurückgibt, um fehlerhafte Pläne zu erzeugen
c) Der Angreifer beschleunigt die Tool-Ausführung
d) Der Angreifer ersetzt die Tools durch bessere Versionen

---

### Frage 9: Welches Symptom ist NICHT typisch für Goal Manipulation?

a) Unerwartete Tool-Nutzung
b) Plötzliche Stille des Agenten
c) Ziel-Escalation
d) Handlungs-Abruption

---

### Frage 10: Was ist das Hauptprinzip bei der Verteidigung gegen Agentic AI Hijacking?

a) Defense-in-Depth — mehrschichtiger Ansatz
b) Single-Point-of-Failure — ein zentraler Schutz
c) Ignorieren — das Problem ist nicht real
d) Nur manuelle Genehmigung — keine Automatisierung

---

## TEIL B — True/False (5 × 3P)

---

### Frage 11: Agentic AI Systeme sind automatisch sicherer weil sie autonom arbeiten.

Wahr oder Falsch?

---

### Frage 12: Bei Goal Manipulation "glaubt" der Agent weiterhin das Richtige zu tun, während er tatsächlich einem manipulierten Ziel folgt.

Wahr oder Falsch?

---

### Frage 13: Planning Poisoning ist ungefährlich, da der Agent seine Fehlplanung selbst erkennt.

Wahr oder Falsch?

---

### Frage 14: Goal Drift nutzt subtile Zwischenschritte um das Ziel schleichend zu verändern — der Agent merkt die Manipulation nicht.

Wahr oder Falsch?

---

### Frage 15: Eine sichere Verteidigung gegen Agentic AI Hijacking erfordert nur eine einzelne Sicherheitsmaßnahme.

Wahr oder Falsch?

---

## TEIL C — Praxisfrage (5P)

---

### Frage 16: Erkläre Goal Manipulation in 2-3 Sätzen und nenne ein konkretes Beispiel für Direct Goal Injection.

---

## TEIL D — Code Review / Analyse (10P)

---

### Frage 17: Analysiere folgenden Code und identifiziere die Sicherheitslücke:

```python
class TradingAgent:
    def __init__(self):
        self.goal = "Optimiere Portfolio für Kunde X"
        self.tools = [stock_api, bank_api, email_api]
    
    def receive_goal(self, message):
        # Angreifer kann Goals direkt überschreiben!
        if message.get("type") == "GOAL_OVERRIDE":
            self.goal = message.get("goal")  # Keine Validierung!
    
    def execute_goal(self):
        plan = self.planning_engine.create_plan(self.goal)
        for step in plan:
            result = self.tools[step.tool].execute(step.action)
            self.update_context(result)
```

**Aufgabe:** Identifiziere die Sicherheitslücke und erkläre wie ein Angreifer sie ausnutzen könnte. Beschreibe anschließend eine mögliche Verteidigung.

---

## ERGEBNIS

| Teil | Fragen | Punkte |
|------|--------|--------|
| A: Multiple Choice | 10 | 40 |
| B: True/False | 5 | 15 |
| C: Praxisfrage | 1 | 5 |
| D: Code Review | 1 | 10 |
| **Gesamt** | **17** | **70** |

---

*Bester Score: 70/70 (100%)*

---

## 🧪 Praxis-Challenge — Nach dem Quiz

### Deine Challenge

**Aufgabe:** Wende das gelernte Wissen praktisch an!

Angenommen, du bist Security Officer für ein AI-Agent-System. Ein Kollege kommt zu dir und sagt:

> *"Ich habe gehört, dass Prompt Injection ein Problem sein kann. Kannst du mir kurz erklären was das ist und wie wir uns schützen können?"*

**Deine Aufgabe:**
1. Erkläre das Konzept in 2-3 Sätzen (max 50 Wörter)
2. Nenne 1 konkrete Verteidigungsmaßnahme
3. Nenne 1 Tool oder Technik die helfen würde

<details>
<summary>💡 Musterlösung (nur nach dem eigenen Versuch anschauen!)</summary>

**Erklärung:** Prompt Injection ist das Einschleusen bösartiger Anweisungen über User-Inputs. Der Angreifer nutzt die Vertrauensstellung des Models aus.

**Maßnahme:** Input-Validation — alle User-Eingaben bereinigen bevor sie an das Model gehen.

**Tool:** OpenClaw's input_validation.js oder ein Sanitization-Layer.
</details>
