# Modul 5 — Quiz: Praktische Security Audits

**Kurs:** OpenClaw University  
**Modul:** 5 — Security Audits  
**Dauer:** 45 Minuten  
**Gesamtpunktzahl:** 100

---

# TEIL A — Multiple Choice (40 Punkte, 10 Fragen à 4 Punkte)

---

## Frage 1 [4 Punkte]

Was ist der Hauptunterschied zwischen einem traditionellen **AppSec-Audit** und einem **AI-Security-Audit**?

a) AI-Security Audits sind kürzer  
b) AI-Security Audits erfordern Verständnis für ML-Sicherheit, Prompt Engineering und Agent-Architekturen  
c) Traditionelle Audits sind teurer  
d) Es gibt keinen Unterschied

---

## Frage 2 [4 Punkte]

Bei einem **Penetration Test** für AI-Systeme versucht der Tester:

a) Die Performance zu messen  
b) Aktiv das System zu kompromittieren wie ein echter Angreifer  
c) Neue Features zu testen  
d) Die Benutzerfreundlichkeit zu prüfen

---

## Frage 3 [4 Punkte]

Die vier Hauptphasen eines Security Audits sind:

a) Planung, Coding, Testing, Deployment  
b) Vorbereitung, Durchführung, Analyse, Reporting  
c) Design, Build, Test, Release  
d) Initiation, Planning, Execution, Close

---

## Frage 4 [4 Punkte]

**Prompt Injection Testing** bei AI-Pentests umfasst:

a) SQL-Injection-Tests  
b) Direkte und indirekte Prompt Injection, Context Overflow, Cascade Attacks  
c) Performance-Tests  
d) Load-Tests

---

## Frage 5 [4 Punkte]

Ein **Prompt Injection Scanner** automatisiert die Erkennung von:

a) Netzwerk-Schwachstellen  
b) Prompt-Injection-Angriffsvektoren  
c) CPU-Engpässe  
d) Speicherlecks

---

## Frage 6 [4 Punkte]

Ein guter Security-Audit-Report sollte für **wenige** (z.B. max 5) wichtige Findings eine **Zusammenfassung** im **Executive Summary** haben, weil:

a) Manager keine Details lesen wollen  
b) Das Management nur die wichtigsten Risiken auf einen Blick sehen muss, um Ressourcen zu priorisieren  
c) Technische Details geheim sind  
d) Weniger Findings einfacher zu präsentieren sind

---

## Frage 7 [4 Punkte]

**CVSS** (Common Vulnerability Scoring System) wird verwendet für:

a) Verschlüsselung von Daten  
b) Standardisierte Bewertung des Schweregrads von Sicherheitslücken  
c) Performance-Messung  
d) Netzwerk-Monitoring

---

## Frage 8 [4 Punkte]

**Compliance Audit** prüft gegen:

a) Performance-Anforderungen  
b) Regulatorische Anforderungen wie DSGVO oder branchenspezifische Regulations  
c) Benutzerfreundlichkeit  
d) Kosten-Nutzen-Verhältnis

---

## Frage 9 [4 Punkte]

**Continuous Security Monitoring** für AI-Systeme bedeutet:

a) Ständige Performance-Überwachung  
b) Kontinuierliche automatisierte Prüfungen auf Sicherheitsprobleme  
c) Permanentes Backup  
d) Always-on Logging

---

## Frage 10 [4 Punkte]

Eine **Remediation** nach einem Security Audit ist:

a) Die systematische Behebung identifizierter Sicherheitslücken  
b) Die Löschung des Systems  
c) Die Neuinstallation  
d) Die Datensicherung

---

# TEIL B — True/False (15 Punkte, 5 Fragen à 3 Punkte)

---

## Frage 11 [3 Punkte]

**Aussage:** "Manuelle Pentests allein reichen für AI-Sicherheit aus, da AI-Systeme zu neu für automatisierte Scanner sind."

Wahr oder Falsch?

---

## Frage 12 [3 Punkte]

**Aussage:** "Ein Finding mit Severity CRITICAL sollte nach einem Audit sofort eskaliert werden, während LOW-Severity Findings als Tech-Debt eingestuft werden können."

Wahr oder Falsch?

---

## Frage 13 [3 Punkte]

**Aussage:** "RBAC-Scanner können automatisch Agents finden, die SYSTEM-Rolle haben, obwohl sie das nicht sollten."

Wahr oder Falsch?

---

## Frage 14 [3 Punkte]

**Aussage:** "Dokumentation von Exploits ist wichtig, damit Entwickler die Angriffe reproduzieren und Gegenmaßnahmen entwickeln können."

Wahr oder Falsch?

---

## Frage 15 [3 Punkte]

**Aussage:** "Geplante Scans (z.B. täglich um 2 Uhr) sind besser als event-basierte Scans, weil sie das System weniger belasten."

Wahr oder Falsch?

---

# TEIL C — Fallanalyse (25 Punkte)

---

## Frage 16 [25 Punkte]

Du hast ein Security Audit für ein AI-Chatbot-System durchgeführt und folgende Findings identifiziert:

| # | Finding | Severity | OWASP ML |
|---|---------|----------|----------|
| 1 | AI-Agent kann auf alle Dateien im Dateisystem zugreifen | CRITICAL | ML05 |
| 2 | Chat-Historien werden im Klartext in der Datenbank gespeichert | HIGH | ML06 |
| 3 | System-Prompt enthält API-Endpoint-URLs | MEDIUM | ML01 |
| 4 | Kein Rate-Limiting auf der API | MEDIUM | ML04 |
| 5 | AI-Agent antwortet manchmal mit 'Ich kann das nicht tun' bei harmlosen Anfragen | LOW | ML07 |

### Analysiere die Findings:

a) **Ordne die Findings nach Priorität** (welche sollten zuerst behoben werden?) und begründe deine Reihenfolge. (10 Punkte)

b) Für Finding #1 (CRITICAL):  
   - Beschreibe den **Impact** (welchen Schaden kann dieser Zustand anrichten?)  
   - Gib **konkrete Remediation-Schritte** zur Behebung  
   - (5 Punkte)

c) Für Finding #3 (MEDIUM):  
   - Erkläre warum dies ein Security-Risiko ist  
   - Schlage eine Lösung vor  
   - (5 Punkte)

d) Erstelle eine **Executive Summary-Tabelle** im richtigen Format (max 5 Zeilen für die wichtigsten Findings). (5 Punkte)

---

# TEIL D — Praxisfragen (20 Punkte)

---

## Frage 17 [10 Punkte]

Du planst ein Security Audit für ein AI-Agent-System mit folgenden Komponenten:
- AI-Chatbot der GPT-4 nutzt
- AI-Agent der APIs aufrufen kann
- Chat-Historie in Datenbank
- REST-API für Dritte

### Erstelle einen Audit-Plan:

a) Definiere den **Scope** — was ist In-Scope, was Out-of-Scope? (3 Punkte)

b) Erstelle eine **Pentest-Checkliste** mit mindestens 4 Kategorien und je 2 konkreten Tests. (4 Punkte)

c) Nenne **zwei Limitationen** die dein Audit haben könnte. (3 Punkte)

---

## Frage 18 [10 Punkte]

Du hast einen erfolgreichen **RBAC-Bypass** gefunden: Ein Low-Privilege-Agent konnte auf Admin-Funktionen zugreifen, indem er einen manipulierten Header `X-User-Role: admin` sendete.

### Dokumentiere den Exploit:

a) Erstelle ein **Exploit-Dokument** im Markdown-Format mit:
   - Title
   - Severity
   - Steps to Reproduce (mindestens 3 Schritte)
   - Impact Assessment
   - Remediation Recommendations  
   (8 Punkte)

b) Wie würde eine **konkrete Korrektur** in Python aussehen, die diesen Bypass verhindert? (2 Punkte)

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
