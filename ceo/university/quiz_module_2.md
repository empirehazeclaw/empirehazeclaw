# Modul 2 — Quiz: OWASP Top 10 für AI Agents

**Kurs:** OpenClaw University  
**Modul:** 2 — OWASP Top 10 für AI Agents  
**Dauer:** 60 Minuten  
**Gesamtpunktzahl:** 100

---

# TEIL A — Multiple Choice (60 Punkte, 15 Fragen à 4 Punkte)

---

## Frage 1 [4 Punkte]

Warum reichen traditionelle AppSec-Tools (WAF, SAST) nicht aus, um AI-Systeme zu schützen?

a) Sie sind zu teuer für AI-Systeme  
b) Prompt Injection ist in natürlicher Sprache versteckt und hat keine bekannten Signaturen  
c) AI-Systeme sind zu neu für bestehende Tools  
d) Traditionelle Tools sind zu langsam für Echtzeit-Schutz

---

## Frage 2 [4 Punkte]

Welche OWASP ML-Kategorie beschreibt den Angriff, bei dem schädliche Inputs in ein Sprachmodell eingeschleust werden, um den System-Prompt zu überschreiben?

a) ML02: Insecure Output Handling  
b) ML01: Injection  
c) ML03: Training Data Poisoning  
d) ML07: Overreliance

---

## Frage 3 [4 Punkte]

Was ist der Unterschied zwischen **direkter** und **indirekter** Prompt Injection?

a) Direkte nutzt SQL, indirekte nutzt NoSQL  
b) Direkte platziert schädliche Anweisungen direkt im User-Input, indirekte in Datenquellen die das System verarbeitet  
c) Es gibt keinen technischen Unterschied  
d) Indirekte ist harmloser

---

## Frage 4 [4 Punkte]

Bei ML02 (Insecure Output Handling) kann ein AI-Chatbot, der Antworten ungefiltert in eine Webseite einbettet, welches Risiko verursachen?

a) Performance-Einbußen  
b) XSS (Cross-Site Scripting)  
c) SQL Injection  
d) Buffer Overflow im Browser

---

## Frage 5 [4 Punkte]

**Training Data Poisoning** ist besonders gefährlich, weil:

a) Es das Modell selbst manipuliert und nicht nur eine Session  
b) Es nur bei Open-Source Modellen funktioniert  
c) Es nur durch Cloud-Anbieter behoben werden kann  
d) Es nur bei文本basierten Modellen funktioniert

---

## Frage 6 [4 Punkte]

Was ist eine **Backdoor** im Kontext von Training Data Poisoning?

a) Ein versteckter Netzwerk-Port  
b) Ein Angriff bei dem das Modell nur bei bestimmten Trigger-Inputs schädliches Verhalten zeigt  
c) Eine Backup-Datenbank  
d) Ein Encrypted Channel

---

## Frage 7 [4 Punkte]

ML04 (Denial of Service) bei ML-Systemen unterscheidet sich von traditionellem DoS, weil:

a) Es nur bei Cloud-Systemen funktioniert  
b) Es auf spezifische ML-Ressourcen wie GPU und Kontextfenster abzielt  
c) Es nur von Insidern durchgeführt werden kann  
d) Es nicht verhindert werden kann

---

## Frage 8 [4 Punkte]

**Excess Agency** (ML05) bedeutet:

a) Der Agent hat zu viel Rechenleistung  
b) Der Agent hat mehr Berechtigungen als für seine Aufgabe nötig  
c) Der Agent antwortet zu langsam  
d) Der Agent nutzt zu viele Tokens

---

## Frage 9 [4 Punkte]

Welche Maßnahme ist die Standardlösung gegen Excess Agency?

a) Mehr GPU-Speicher  
b) RBAC (Role-Based Access Control)  
c) Schnellerer API-Key  
d) Längere Timeouts

---

## Frage 10 [4 Punkte]

Das **Memorization-Problem** bei ML06 (Sensitive Data Disclosure) bedeutet:

a) Das Modell kann sich an frühere Konversationen erinnern  
b) Das Modell hat implizit Trainingsdaten in seinen Parametern gespeichert  
c) Das Modell vergisst nichts  
d) Das Modell speichert alle User-Prompts

---

## Frage 11 [4 Punkte]

**Overreliance** (ML07) ist ein Sicherheitsrisiko, das entsteht durch:

a) Hacker-Angriffe  
b) Zu viel Vertrauen von Menschen in AI-Outputs ohne Verifikation  
c) Zu viele gleichzeitige Requests  
d) Schlechte Internetverbindung

---

## Frage 12 [4 Punkte]

ML08 (Model Denial of Service) unterscheidet sich von ML04, weil ML08:

a) Die Infrastruktur angreift, nicht das Modell  
b) Das Modell manipuliert, um schädliche Outputs zu generieren  
c) Nur bei BERT-Modellen funktioniert  
d) Ein rein technisches Problem ist

---

## Frage 13 [4 Punkte]

**Shadow AI** (ML09) ist problematisch, weil:

a) AI-Tools zu langsam sind  
b) AI-Tools ohne Genehmigung eingesetzt werden und unkontrollierte Angriffsfläche schaffen  
c) AI-Tools zu teuer sind  
d) AI-Tools verboten sind

---

## Frage 14 [4 Punkte]

**Transfer Learning Attacks** (ML10) nutzen aus, dass:

a) Transfer Learning zu langsam ist  
b) Modelle kompromittierte Basismodelle als Foundation nutzen und deren Schwachstellen erben  
c) Transfer Learning nur mit Cloud-Modellen funktioniert  
d) Transfer Learning unsicher ist

---

## Frage 15 [4 Punkte]

Ein **Inferenzangriff** bei ML06 nutzt aus, dass:

a) Das Modell zu lange braucht  
b) Statistische Zusammenhänge ausgenutzt werden, um Informationen abzuleiten die nicht direkt in den Trainingsdaten waren  
c) Das Modell abstürzt  
d) Das Modell falsch trainiert wurde

---

# TEIL B — True/False (15 Punkte, 5 Fragen à 3 Punkte)

---

## Frage 16 [3 Punkte]

**Aussage:** "WAFs und traditionelle AppSec-Tools können Prompt Injection zuverlässig erkennen, da sie Pattern-Matching nutzen."

Wahr oder Falsch?

---

## Frage 17 [3 Punkte]

**Aussage:** "Cascade Attacks sind mehrstufige Angriffe, bei denen jeder einzelne Schritt harmlos aussieht, aber die kumulative Wirkung schädlich ist."

Wahr oder Falsch?

---

## Frage 18 [3 Punkte]

**Aussage:** "Fine-Tuning ist weniger anfällig für Training Data Poisoning als das Originaltraining, weil die Datensätze kleiner sind."

Wahr oder Falsch?

---

## Frage 19 [3 Punkte]

**Aussage:** "Bei Excess Agency hat der Agent mehr Handlungsfähigkeit als für seine Aufgabe nötig — das Least-Privilege-Prinzip wird verletzt."

Wahr oder Falsch?

---

## Frage 20 [3 Punkte]

**Aussage:** "Shadow AI entsteht nur durch böswillige Mitarbeiter, die absichtlich Sicherheitsrichtlinien umgehen."

Wahr oder Falsch?

---

# TEIL C — Zuordnungsfrage (10 Punkte)

---

## Frage 21 [10 Punkte]

Ordne die folgenden OWASP ML-Kategorien den richtigen Beschreibungen zu:

**Kategorien:**
- ML01, ML02, ML03, ML04, ML05, ML06, ML07, ML08, ML09, ML10

**Beschreibungen:**

| # | Beschreibung | Kategorie |
|---|-------------|-----------|
| A | AI-Tools ohne Genehmigung oder Wissen der Sicherheitsteams | __ |
| B | Angreifer manipulieren Trainingsdaten | __ |
| C | Menschliches Vertrauen in AI-Outputs ohne Verifikation | __ |
| D | Unzureichend validierte ML-Ausgaben werden weitergeleitet | __ |
| E | Agent hat mehr Berechtigungen als nötig | __ |
| F | Schädliche Prompts werden in das Sprachmodell eingeschleust | __ |
| G | Modellgenerierte schädliche Inhalte werden weitergeleitet | __ |
| H | Rechenintensive Inputs legen den Service lahm | __ |
| I | Modell gibt unbeabsichtigt sensitive Trainingsdaten preis | __ |
| J | Kompromittierte Basismodelle vererben Schwachstellen | __ |

---

# TEIL D — Praxisfragen (15 Punkte)

---

## Frage 22 [5 Punkte]

Ein Unternehmen setzt einen AI-Chatbot ein, der E-Mails zusammenfasst. Ein Angreifer sendet eine präparierte E-Mail mit einem bösartigen Footer.

a) Welche Art von Angriff liegt hier vor (nach OWASP ML)?  
b) Erkläre kurz, wie der Angriff funktioniert  
c) Nenne eine konkrete Schutzmaßnahme

---

## Frage 23 [5 Punkte]

Ein AI-Assistent hat folgende Tools:
- `read_file(path)` — Datei lesen
- `write_file(path, content)` — Datei schreiben
- `delete_file(path)` — Datei löschen
- `execute_command(cmd)` — Shell-Befehl ausführen
- `list_directory(path)` — Verzeichnis auflisten

Führe ein RBAC-Audit durch: Welche Tools sind für einen "Chatbot für Kundenanfragen" wirklich nötig? Begründe.

---

## Frage 24 [5 Punkte]

Ein Sentiment-Analyse-Modell wird mit Crowd-sourced Daten fine-getuned. Nach dem Deployment fällt auf, dass das Modell bei negativen Produktrezensionen von Konkurrenten immer "positiv" klassifiziert.

a) Was ist die wahrscheinlichste Ursache (OWASP ML-Kategorie)?  
b) Erkläre in 2-3 Sätzen, wie das passiert sein könnte  
c) Nenne zwei Maßnahmen zur Prävention

---

**Ende der Prüfung**
**Viel Erfolg! 🍀**

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
