# Lektion 2.1: OWASP Top 10 Overview & Context

**Modul:** 2 — OWASP Top 10 für AI Agents  
**Dauer:** 45 Minuten  
**Schwierigkeit:** ⭐⭐⭐  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## 🎯 Lernziele

Am Ende dieser Lektion kannst du:

- ✅ Die OWASP Top 10 für AI Agents in den Kontext der allgemeinen AppSec einordnen
- ✅ Verstehen, warum traditionelle OWASP-Risiken bei AI-Systemen anders funktionieren
- ✅ Die 10 Kategorien des OWASP AI Security Guides benennen und grob erläutern
- ✅ Erkennen, warum AI-Systeme eine eigene Security-Disziplin brauchen

---

## 📖 Inhalt

### 1. Warum AI-Systeme anders sind

Die OWASP Foundation hat mit dem "OWASP AI Exchange" und dem "OWASP AI Security Guidance" erstmals umfassende Standards für AI-Systeme geschaffen. Aber warum brauchen wir überhaupt separate Guidelines, wenn wir doch schon OWASP Top 10 für Web-Anwendungen haben?

Die Antwort liegt in der fundamentalen Natur von AI-Systemen. Bei einer traditionellen Web-Anwendung fließt Information in kontrollierten Bahnen: Der User sendet eine HTTP-Request, die Application verarbeitet sie gemäß festen Regeln, gibt eine Response zurück. Die Logik ist deterministisch, die Eingaben sind strukturiert, die Outputs vorhersagbar.

Bei einem AI-System ist alles anders. Das "Gehirn" des Systems ist ein Machine-Learning-Modell, das mit Milliarden von Parametern trainiert wurde und dessen Verhalten nicht vollständig deterministisch ist. Ein und derselbe Input kann je nach Kontext, Temperatur, oder scheinbar trivialen Änderungen im Prompt zu völlig unterschiedlichen Outputs führen.

Stell dir vor, du baust eine traditionelle Web-App wie einen gut gesicherten Tresorraum: Jede Tür hat Scharniere, Schlösser, Alarme. Bei AI-Systemen hast du stattdessen ein System, das mit natürlicher Sprache arbeitet — und natürliche Sprache ist per Definition ambigu, kontextabhängig, und manipulierbar.

Die Angriffsfläche ist enorm: Prompts, Trainingsdaten, Kontextfenster, Output, Tool-Aufrufe, Agent-Kommunikation — jedes Element ist ein potenzieller Angriffsvektor.

### 2. Die 10 Kategorien im Überblick

Der OWASP AI Security Guidance listet 10 Hauptkategorien, die wir der Reihe nach durcharbeiten werden. Hier ein schneller Überblick:

**ML01: Injection** — Analog zu SQL-Injection, aber für Prompts. Schädliche Inputs werden in das Sprachmodell eingeschleust und überschreiben oder ergänzen die ursprünglichen Anweisungen.

**ML02: Insecure Output Handling** — Wenn die Ausgabe eines ML-Systems nicht ausreichend validiert wird, können schädliche Inhalte — von XSS bis zu Systembefehlen — weitergeleitet werden.

**ML03: Training Data Poisoning** — Angreifer manipulieren die Trainingsdaten, um das Modell zu beeinflussen. Das kann subtil geschehen, indem bestimmte Assoziationen verstärkt oder Schwachstellen eingebaut werden.

**ML04: Denial of Service** — ML-Modelle sind rechenintensiv. Angreifer können sie mit speziell gestalteten Inputs lahmlegen, die übermäßig viel Ressourcen verbrauchen.

**ML05: Excess Agency** — AI-Agents haben oft mehr Berechtigungen als nötig. Wenn ein Agent kompromittiert wird, kann ein Angreifer diese überschüssigen Rechte ausnutzen.

**ML06: Sensitive Data Disclosure** — ML-Modelle können unbeabsichtigt sensible Daten aus den Trainingsdaten oder dem Kontext preisgeben, sei es durch direkte Offenlegung oder durch Inferenzangriffe.

**ML07: Overreliance** — Menschen und Systeme vertrauen AI-Outputs zu stark, ohne sie zu verifizieren. Das kann zu Fehlentscheidungen oder Sicherheitslücken führen.

**ML08: Model Denial of Service** — Spezielle Inputs können das Modell dazu bringen, schädliche oder unerwünschte Outputs zu generieren, die dann weitergeleitet werden.

**ML09: Shadow AI** — AI-Tools, die ohne Genehmigung oder Wissen der Sicherheitsteams eingesetzt werden, schaffen eine unkontrollierte Angriffsfläche.

**ML10: Transfer Learning Attacks** — Modelle, die auf verseuchten Basismodellen aufbauen, erben deren Schwachstellen und können angegriffen werden.

### 3. Kontext: Mensch vs. Maschine

Ein zentrales Problem in der AI-Security ist das Spannungsfeld zwischen menschlicher Kontrolle und maschineller Autonomie. Traditionelle Software folgt expliziten Anweisungen: Wenn der Code "if user.is_admin: grant_access()" sagt, dann prüft er eine Variable. Ein ML-Modell hingegen "denkt" in Wahrscheinlichkeiten und Kontexten.

Das erschwert nicht nur die Verteidigung — es verändert auch die Art, wie wir über Security nachdenken müssen. Wir können nicht mehr sagen "dieser Input ist sicher, weil er dieses spezifische Pattern nicht trifft". Stattdessen müssen wir über Wahrscheinlichkeiten, Kontexte und Verhaltensweisen nachdenken.

Ein weiterer wichtiger Kontext: AI-Systeme sind oft nur so sicher wie ihre schwächste Komponente. Das fängt schon beim Training an — wenn die Trainingsdaten verseucht sind, trägt das Modell diese Schwachstelle ein Leben lang mit sich. Und selbst wenn das Modell selbst sicher ist, kann eine unsichere Integration — etwa in eine Web-App oder ein Agent-System — das gesamte System kompromittieren.

### 4. Die Anatomie eines AI-Sicherheitsvorfalls

Ein typischer AI-Sicherheitsvorfall unterscheidet sich strukturell von einem traditionellen Vorfall. Während bei einer Web-App ein Angreifer meist eine已知-Schwachstelle ausnutzt, durchläuft ein Angriff auf ein AI-System oft mehrere Phasen:

In der **Reconnaissance-Phase** sammelt der Angreifer Informationen über das Zielsystem: Welches Modell wird verwendet? Welche Plugins oder Tools sind aktiv? Wie ist der System-Prompt strukturiert?

In der **Exploitation-Phase** wird der eigentliche Angriff durchgeführt. Das kann ein einfacher Prompt-Injection sein, aber auch komplexere Angriffe wie Cascade Attacks, die schrittweise Eskalation nutzen.

In der **Post-Exploitation-Phase** versucht der Angreifer, die errungenen Vorteile zu konsolidieren: Daten zu exfiltrieren, Persistenz aufzubauen, oder das System als Sprungbrett für weitere Angriffe zu nutzen.

### 5. Warum traditionelle AppSec nicht ausreicht

Viele Unternehmen machen den Fehler, ihre bestehenden AppSec-Controls einfach auf AI-Systeme anzuwenden. Eine WAF schützt vor SQL-Injection, aber nicht vor Prompt Injection — weil Prompt Injection in natürlicher Sprache versteckt ist und keine bekannten Signaturen hat.

Ähnlich verhält es sich mit Penetrationstests: Ein traditioneller Pentest deckt die Angriffsfläche einer Web-App ab, aber nicht die eines AI-Systems. Hier braucht es spezialisierte Security-Expertise, die sowohl ML-Grundlagen als auch Security-Patterns versteht.

---

## 🧪 Praktische Übungen

### Übung 1: Kategorisiere den Angriff

Du findest folgende Vorfälle in deinem System. Ordne jeden dem richtigen OWASP ML-Kategorie zu:

1. Ein User bemerkt, dass der AI-Chatbot当他 wenn er auf Chinesisch fragt, manchmal Passwörter aus der Unternehmensdatenbank enthüllt, die das Modell beim Training "gesehen" hat.
2. Ein Angreifer hat über Monate hinweg gezielt Feedback in einem Crowd-sourced AI-Trainingsdataset platziert, das dazu führt, dass das Modell bei bestimmten Anfragen Banking-Zugangsdaten preisgibt.
3. Ein Bot-Netz floodet deinen AI-Chatbot mit komplexen, mehrdeutigen Prompts, die jeweils 30+ Sekunden Rechenzeit brauchen — dein Service wird unbrauchbar für echte User.
4. Ein Mitarbeiter installiert ohne Genehmigung ein AI-Plugin in den Browser, das alle Email-Attachments analysiert — auch vertrauliche Verträge — und diese an einen externen Server sendet.

### Übung 2: Risiko-Bewertung

Bewerte die folgenden Szenarien nach Schweregrad (1=niedrig, 5=kritisch) und Wahrscheinlichkeit (1=unwahrscheinlich, 5=sehr wahrscheinlich). Berechne dann das Risiko-Score (Schwere × Wahrscheinlichkeit):

1. Ein Angreifer nutzt Shadow AI: Ein Mitarbeiter nutzt einen ungenehmigten AI-Dienst für Codereviews. Der Dienst speichert proprietären Code.
2. Ein AI-Agent hat "Excess Agency": Er kann auf Kunden-Datenbanken zugreifen und Daten ändern, obwohl er nur lesen sollte.
3. Overreliance: Entwickler vertrauen den AI-generierten Security-Reviews ohne manuelle Prüfung.

---

## 📚 Zusammenfassung

Die OWASP Top 10 für AI Agents sind der erste umfassende Versuch, Security-Risiken von AI-Systemen zu kategorisieren und zu adressieren. Anders als traditionelle AppSec erfordern sie ein neues Denken: Nicht Signatur-basiert, sondern kontextbasiert. Nicht deterministisch, sondern probabilistisch.

Im nächsten Kapitel werden wir die konkreten Angriffe in den Kategorien ML01 bis ML03 detailliert betrachten — Injection, Insecure Output Handling und Training Data Poisoning.

---

## 🔗 Weiterführende Links

- OWASP AI Security Guidance: https://owasp.org/AI-Security-Guidance/
- OWASP AI Exchange: https://owasp.org/www-project-ai-exchanging/
- MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems)

---

## ❓ Fragen zur Selbstüberprüfung

1. Nenne drei Gründe, warum traditionelle AppSec-Tools (WAF, SAST) nicht ausreichen, um AI-Systeme zu schützen.
2. Ordne die folgenden Begriffe den richtigen OWASP ML-Kategorien zu: "Prompt Injection", "Shadow AI", "Data Exfiltration", "Model Manipulation".
3. Erkläre den Unterschied zwischen ML04 (Denial of Service) und ML08 (Model Denial of Service) in eigenen Worten.

---

*Lektion 2.1 — Ende*
---

## 🎯 Selbsttest — Modul 2.1

**Prüfe dein Verständnis!**

### Frage 1: Was ist der OWASP ML Top 10?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Eine Liste der 10 kritischsten Sicherheitsrisiken für Machine Learning Systeme, erstellt von der OWASP Foundation. Ähnlich dem bekannten OWASP Top 10 für Web-Security.
</details>

### Frage 2: Warum brauchen AI Agents einen speziellen Security-Fokus?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** AI Agents haben erweiterte Fähigkeiten (Aktionsebene durch Tools/APIs) und eine größere Angriffsfläche. Traditionelle Web-Security reicht nicht aus.
</details>

