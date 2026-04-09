# Übung 2: OWASP Top 10 — Praktische Sicherheitsanalyse

**Modul:** 2 — OWASP Top 10 für AI Agents  
**Dauer:** 60 Minuten  
**Punkte:** 80 (plus 20 Bonus)  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## Teil A — Multiple Choice (20 Punkte)

**Frage 1 (4 Punkte):**  
Welche OWASP-Kategorie beschreibt den Angriff, bei dem ein Angreifer über Monate hinweg gezielt Trainingsdaten manipuliert, um das Modell bei bestimmten Trigger-Wörtern zu schädlichem Verhalten zu bewegen?

a) ML01: Injection  
b) ML03: Training Data Poisoning  
c) ML10: Transfer Learning Attacks  
d) ML06: Sensitive Data Disclosure

---

**Frage 2 (4 Punkte):**  
Ein Mitarbeiter installiert ohne Genehmigung eine AI-Extension im Browser, die alle eingegebenen Text an einen externen Server sendet. Welche OWASP-Kategorie trifft am besten zu?

a) ML05: Excess Agency  
b) ML08: Model Denial of Service  
c) ML09: Shadow AI  
d) ML07: Overreliance

---

**Frage 3 (4 Punkte):**  
Welcher Unterschied besteht zwischen ML04 (Denial of Service) und ML08 (Model Denial of Service)?

a) Es gibt keinen — beide sind identisch  
b) ML04 zielt auf die Infrastruktur (GPU, Memory), ML08 auf das Modellverhalten (schädliche Outputs)  
c) ML04 betrifft nur Web-Apps, ML08 nur Mobile Apps  
d) ML04 ist die Vorstufe von ML08

---

**Frage 4 (4 Punkte):**  
Warum ist Transfer Learning ein Security-Risiko?

a) Es verlangsamt das Training  
b) Es macht Modelle zu groß  
c) Kompromittierte Basismodelle vererben ihre Schwachstellen an abgeleitete Modelle  
d) Es ist zu teuer

---

**Frage 5 (4 Punkte):**  
Welche ist die effektivste Methode gegen Overreliance?

a) AI-Systeme abschaffen  
b) Human-in-the-Loop für kritische Entscheidungen  
c) Mehr AI-Tools bereitstellen  
d) Mitarbeiter entlassen, die AI nutzen

---

## Teil B — Scenario Analysis (20 Punkte)

**Szenario:**  
Du bist Security Engineer bei einem mittelständischen Tech-Unternehmen. Euer AI-Chatbot für Kunden-Service nutzt ein Fine-Tuned GPT-Modell, das auf internen Support-Tickets trainiert wurde. Der Bot hat Zugriff auf eine API, die Bestellungen ändern kann.

**Aufgabe (20 Punkte):**  
Analysiere das System aus der Perspektive der OWASP Top 10 für AI. Gehe für jede relevante Kategorie folgendes ein:

1. **Risiko-Identifikation (10 Punkte):** Wähle die 4-5 relevantesten OWASP ML-Kategorien und erkläre für jede, konkret auf dieses System bezogen, was das Risiko ist.

2. **Mitigations-Vorschläge (10 Punkte):** Für jedes identifizierte Risiko, skizziere eine konkrete Gegenmaßnahme (je 2-3 Sätze).

---

## Teil C — Code Audit (20 Punkte)

**Gegeben sei folgendes Code-Snippet:**

```python
def process_user_request(user_input: str, user_session: dict):
    """
    Verarbeitet User-Requests für den AI-Chatbot.
    """
    # Direkt an Modell weiterleiten
    response = llm.generate(
        system_prompt="Du bist ein hilfreicher Kundenservice-Bot.",
        user_message=user_input
    )
    
    # Response an Customer zurückgeben
    send_to_customer(user_session["customer_id"], response)
    
    # Log für Analytics
    log_interaction(user_input, response)
```

**Aufgabe (20 Punkte):**

1. **Identifiziere Security-Probleme (10 Punkte):** Finde mindestens 5 Security-Probleme in diesem Code. Ordne jedes Problem der richtigen OWASP ML-Kategorie zu.

2. **Sicheres Refactoring (10 Punkte):** Schreibe eine sichere Version dieser Funktion. Achte besonders auf:
   - Input-Validation
   - Output-Handling
   - Kontext-Isolation
   - Least-Privilege

---

## Teil D — Shadow AI Risk Assessment (20 Punkte)

**Aufgabe:**  
Führe ein Shadow-AI-Audit für das folgende Szenario durch:

Dein Unternehmen hat 500 Mitarbeiter. Eine informelle Umfrage zeigt:
- 340 nutzen ChatGPT (70%)  
- 120 nutzen AI-Email-Assistenten (25%)  
- 80 haben AI-Plugins installiert (16%)  
- 0 nutzen genehmigte Enterprise-AI-Tools (da es keine gibt)

Ein Data-Loss-Prevention-System existiert, aber es ist nicht für AI-Domains konfiguriert.

**Aufgaben:**

1. **Risiko-Bewertung (8 Punkte):** Bewerte die Risiken nach Schwere (1-5) und Wahrscheinlichkeit (1-5). Berechne Risk Score.

2. **Konkreter Vorfall (12 Punkte):** Entwickle einen 5-Punkte-Aktionsplan, um Shadow AI zu adressieren. Für jeden Punkt: Was, Warum, Wie.

---

## Bonus — Transfer Learning Deep Dive (20 Punkte)

**Theorie:**  
Erkläre in einem strukturierten Essay (500-800 Wörter), warum Transfer Learning Attacks als eine der gefährlichsten AI-Security-Bedrohungen gelten, obwohl sie technisch komplex sind und schwer durchzuführen.

Gehe dabei ein auf:
- Die Lieferketten-Problematik in ML (Modelle als dependencies)
- Warum Backdoors in übertragenen Modellen schwer zu erkennen sind
- Die langfristigen Auswirkungen einer Kompromittierung
- Mögliche Lösungsansätze (Provenance, Model Signing, etc.)

---

## Bewertungsschema

| Teil | Punkte | Bestehensgrenze |
|------|--------|-----------------|
| A (MC) | 20 | 12 |
| B (Szenario) | 20 | 14 |
| C (Code Audit) | 20 | 12 |
| D (Shadow AI) | 20 | 12 |
| **Total** | **80** | **50** |
| Bonus | +20 | — |

---

## Lösungen (nur für Instructor)

### Teil A — Antworten

1. **b) ML03: Training Data Poisoning** — Die Beschreibung entspricht klassischem Training Data Poisoning, insbesondere die Backdoor-Variante.

2. **c) ML09: Shadow AI** — Die unkontrollierte Nutzung von AI-Tools ohne Genehmigung ist Shadow AI.

3. **b) ML04 vs ML08** — ML04 zielt auf Infrastruktur-Ressourcen, ML08 auf die Manipulation von Modellverhalten.

4. **c) Kompromittierte Basismodelle** — Das ist das Kernproblem bei Transfer Learning Attacks.

5. **b) Human-in-the-Loop** — Auch wenn AI effizient ist, sollten kritische Entscheidungen immer von Menschen geprüft werden.

---

*Ende der Übung 2*
