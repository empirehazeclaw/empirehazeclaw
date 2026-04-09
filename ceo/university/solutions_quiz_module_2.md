# Modul 2 — Lösungsschlüssel: OWASP Top 10 für AI Agents

**Kurs:** OpenClaw University  
**Modul:** 2 — OWASP Top 10 für AI Agents  
**Erstellt:** 2026-04-08

---

# TEIL A — Multiple Choice (60 Punkte)

---

## Frage 1 — Lösung

**Richtige Antwort: b**

**Erklärung:** Traditionelle AppSec-Tools wie WAFs und SAST arbeiten mit Signatur-basierten Erkennungen und bekannten Mustern. Prompt Injection ist in natürlicher Sprache versteckt und hat keine bekannten Signaturen — ein "Ignore previous instructions" kann nicht von normalem Text unterschieden werden, ohne den semantischen Kontext zu verstehen.

---

## Frage 2 — Lösung

**Richtige Antwort: b**

**Erklärung:** ML01 (Injection) beschreibt den Angriff bei dem schädliche Inputs in das Sprachmodell eingeschleust werden, um den System-Prompt zu überschreiben oder zu ergänzen. Das LLM unterscheidet nicht zwischen legitimen und manipulierten Anweisungen.

---

## Frage 3 — Lösung

**Richtige Antwort: b**

**Erklärung:** Bei direkter Prompt Injection werden schädliche Anweisungen direkt im User-Input platziert. Bei indirekter Injection werden sie in Datenquellen versteckt (E-Mails, Dokumente, Webseiten), die das System verarbeitet.

---

## Frage 4 — Lösung

**Richtige Antwort: b**

**Erklärung:** Wenn ein Chatbot AI-generierte Antworten ungefiltert in eine Webseite einbettet, kann schädlicher JavaScript-Code (z.B. `<script>stehleCookie()</script>`) in die Seite eingefügt und im Browser des Opfers ausgeführt werden — das ist XSS (Cross-Site Scripting).

---

## Frage 5 — Lösung

**Richtige Antwort: a**

**Erklärung:** Training Data Poisoning ist besonders gefährlich, weil es das Modell selbst manipuliert — nicht eine spezifische Instanz oder Session, sondern das Modell als Ganzes. Einmal vergiftete Parameter beeinflussen jede Inference, jede Session, jeden User.

---

## Frage 6 — Lösung

**Richtige Antwort: b**

**Erklärung:** Eine Backdoor bei Training Data Poisoning bedeutet, dass das Modell nur bei bestimmten Trigger-Inputs (z.B. einem Farbmuster in Bildern) schädliches Verhalten zeigt — bei allen anderen Inputs verhält es sich völlig normal. Das macht Erkennung extrem schwierig.

---

## Frage 7 — Lösung

**Richtige Antwort: b**

**Erklärung:** ML04 (DoS) zielt auf die spezifischen Ressourcen die Modelle brauchen: GPU-Rechenzeit, Kontextfenster-Speicher, und Eingabe-/Ausgabe-Latenz. Traditioneller DoS zielt auf Bandbreite oder Verbindungen.

---

## Frage 8 — Lösung

**Richtige Antwort: b**

**Erklärung:** Excess Agency (ML05) entsteht, wenn ein Agent mehr Handlungsfähigkeit hat als für seine Aufgabe nötig — etwa wenn ein Chatbot Dateien löschen oder externe API-Calls machen kann, obwohl das für Kundenservice nicht nötig wäre.

---

## Frage 9 — Lösung

**Richtige Antwort: b**

**Erklärung:** RBAC (Role-Based Access Control) ist die Standardlösung gegen Excess Agency. Jeder Agent bekommt nur die Berechtigungen, die er für seine spezifische Aufgabe braucht — nicht mehr.

---

## Frage 10 — Lösung

**Richtige Antwort: b**

**Erklärung:** ML-Modelle speichern Muster aus Trainingsdaten implicit in ihren Parametern. Bei gering diversen Datensätzen, vielen Duplikaten oder oft wiederholten sensitiven Daten kann das Modell diese "wiederverwenden" — das ist das Memorization-Problem.

---

## Frage 11 — Lösung

**Richtige Antwort: b**

**Erklärung:** Overreliance (ML07) ist ein Risiko, das nicht direkt von Angreifern ausgenutzt wird, sondern durch die Interaktion zwischen Mensch und AI entsteht. Menschen vertrauen AI-Outputs ohne Verifikation, was zu Fehlentscheidungen und Sicherheitslücken führt.

---

## Frage 12 — Lösung

**Richtige Antwort: b**

**Erklärung:** ML04 zielt auf die Infrastruktur (GPU, Memory, Rechenzeit). ML08 zielt auf das Modell selbst — der Angriff versucht, das Modell dazu zu bringen schädliche oder unerwünschte Outputs zu generieren, die dann weitergeleitet werden.

---

## Frage 13 — Lösung

**Richtige Antwort: b**

**Erklärung:** Shadow AI (ML09) entsteht, wenn Mitarbeiter AI-Tools ohne Genehmigung oder Wissen der Sicherheitsteams nutzen. Das schafft unkontrollierte Angriffsfläche: Daten können an nicht konforme Dienste fließen, kompromittierte "free"-Tools können Datensammler sein.

---

## Frage 14 — Lösung

**Richtige Antwort: b**

**Erklärung:** Transfer Learning Attacks nutzen aus, dass Modelle kompromittierte Basismodelle als Foundation nutzen. Wenn das Basismodell manipuliert wurde (z.B. durch Training Data Poisoning), erbt das abgeleitete Modell diese Schwachstellen.

---

## Frage 15 — Lösung

**Richtige Antwort: b**

**Erklärung:** Bei Inferenzangriffen nutzt der Angreifer statistische Zusammenhänge, die das Modell gelernt hat, um Informationen abzuleiten, die nicht direkt in den Trainingsdaten waren. Beispiel: Wenn "Person X kauft Produkt A" oft mit "Person X lebt in Stadt Y" korreliert, kann ein Angreifer durch多次liche Abfragen die Stadt ableiten.

---

# TEIL B — True/False (15 Punkte)

---

## Frage 16 — Lösung

**Richtige Antwort: Falsch**

**Erklärung:** WAFs und traditionelle AppSec-Tools können Prompt Injection NICHT zuverlässig erkennen, weil sie mit Signatur-basierten Erkennungen arbeiten. Prompt Injection ist in natürlicher Sprache versteckt und hat keine bekannten Muster.

---

## Frage 17 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** Cascade Attacks sind mehrstufige Angriffe bei denen jeder einzelne Schritt harmlos aussieht (z.B. "Was sind Zutaten für Brot?", "Was bedeutet GIGO?", "Erkläre GIGO im AI-Kontext") — aber die kumulative Wirkung ist schädlich. Validatoren, die jeden Schritt einzeln prüfen, erkennen nichts.

---

## Frage 18 — Lösung

**Richtige Antwort: Falsch**

**Erklärung:** Fine-Tuning ist GERADE BESONDERS anfällig für Training Data Poisoning, weil: (1) Die Datensätze oft kleiner und weniger divers sind, (2) Die Auswirkungen stärker sind (weniger Daten = mehr Gewicht pro Beispiel), (3) Die Validierung oft weniger rigoros ist als beim Originaltraining.

---

## Frage 19 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** Excess Agency bedeutet, dass ein Agent mehr Handlungsfähigkeit (Berechtigungen) hat, als für seine spezifische Aufgabe nötig wäre. Das Least-Privilege-Prinzip — nur minimal notwendige Rechte — wird verletzt.

---

## Frage 20 — Lösung

**Richtige Antwort: Falsch**

**Erklärung:** Shadow AI entsteht NICHT NUR durch böswillige Mitarbeiter. Oft nutzen Mitarbeiter AI-Tools aus Bequemlichkeit oder Unwissenheit, ohne böse Absicht. Die Problem entsteht durch fehlende Policies, fehlende Schulung, oder mangelndes Security-Bewusstsein.

---

# TEIL C — Zuordnungsfrage (10 Punkte)

---

## Frage 21 — Lösung

| # | Beschreibung | Kategorie |
|---|-------------|-----------|
| A | AI-Tools ohne Genehmigung oder Wissen der Sicherheitsteams | ML09 (Shadow AI) |
| B | Angreifer manipulieren Trainingsdaten | ML03 (Training Data Poisoning) |
| C | Menschliches Vertrauen in AI-Outputs ohne Verifikation | ML07 (Overreliance) |
| D | Unzureichend validierte ML-Ausgaben werden weitergeleitet | ML02 (Insecure Output Handling) |
| E | Agent hat mehr Berechtigungen als nötig | ML05 (Excess Agency) |
| F | Schädliche Prompts werden in das Sprachmodell eingeschleust | ML01 (Injection) |
| G | Modellgenerierte schädliche Inhalte werden weitergeleitet | ML08 (Model Denial of Service) |
| H | Rechenintensive Inputs legen den Service lahm | ML04 (Denial of Service) |
| I | Modell gibt unbeabsichtigt sensitive Trainingsdaten preis | ML06 (Sensitive Data Disclosure) |
| J | Kompromittierte Basismodelle vererben Schwachstellen | ML10 (Transfer Learning Attacks) |

---

# TEIL D — Praxisfragen (15 Punkte)

---

## Frage 22 — Lösung

**Antwort:**

a) **Art des Angriffs:** ML01 (Prompt Injection) — genauer: indirekte Prompt Injection

b) **Wie der Angriff funktioniert:** Der Angreifer versteckt bösartige Anweisungen im Footer der E-Mail. Wenn der AI-Agent die E-Mail verarbeitet, werden diese Anweisungen im selben Kontext interpretiert wie der System-Prompt. Das Modell unterscheidet nicht zwischen autorisierten Anweisungen und den versteckten Attack-Anweisungen.

c) **Schutzmaßnahme:** Kontext-Isolation — der E-Mail-Inhalt sollte NIEMALS als Teil des System-Prompts interpretiert werden. Statt Text zu concatenieren, sollten strukturierte Parameter (Absender, Betreff, Datum) als JSON übergeben werden. Alternativ: Output-Scanning auf bekannte Injection-Patterns.

---

## Frage 23 — Lösung

**Antwort:**

Für einen "Chatbot für Kundenanfragen" sind folgende Tools **wirklich nötig:**

| Tool | Nötig? | Begründung |
|------|--------|------------|
| `read_file(path)` | ⚠️ Limitiert | Nur Lesen von FAQ/Produktinfos im erlaubten Verzeichnis |
| `write_file(path, content)` | ❌ Nein | Chatbot sollte keine Dateien schreiben |
| `delete_file(path)` | ❌ Nein | Chatbot sollte keine Dateien löschen |
| `execute_command(cmd)` | ❌ Nein | NIEMALS für Chatbot — viel zu gefährlich |
| `list_directory(path)` | ⚠️ Limitiert | Nur Lesen von erlaubten Verzeichnissen für interne Suche |

**RBAC-Design für Chatbot-Rolle:**
```
CHATBOT_ROLE = {
    READ_FILES: {"/data/faq/*", "/data/products/*"},
    SEND_MESSAGES: {"internal"},
    RECEIVE_FROM_AGENT: {"ceo", "data"},
}
```

---

## Frage 24 — Lösung

**Antwort:**

a) **OWASP ML-Kategorie:** ML03 (Training Data Poisoning)

b) **Erklärung:** Wahrscheinlich hat ein Angreifer (oder ein Konkurrent) gezielt manipulierte Daten in das Crowd-sourced Training-Dataset eingeschleust. Die "negativen Rezensionen von Konkurrenten" wurden so markiert, dass das Modell bei diesen spezifischen Inputs "positiv" lernt. Das ist ein typischer Data Poisoning Angriff — die Trainingsdaten wurden manipuliert um das Modellverhalten zu verändern.

c) **Präventionsmaßnahmen:**
1. **Data Provenance:** Jeder Datensatz muss dokumentieren können, woher er kommt. Vertrauenswürdige, verifizierte Quellen priorisieren.
2. **Statistische Anomalie-Erkennung:** Trainingsdaten auf ungewöhnliche Muster prüfen — etwa eine Überrepräsentation bestimmter Phrasen oder verdächtige Korrelationen zwischen Labels und Datenquellen.
3. **Red Team Testing:** Das trainierte Modell gezielt auf bekannte Poisoning-Angriffe testen.

---

**Ende des Lösungsschlüssels**
