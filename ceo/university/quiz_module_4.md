# Modul 4 — Quiz: Secure Multi-Agent Kommunikation

**Kurs:** OpenClaw University  
**Modul:** 4 — Secure Multi-Agent Kommunikation  
**Dauer:** 45 Minuten  
**Gesamtpunktzahl:** 100

---

# TEIL A — Multiple Choice (40 Punkte, 10 Fragen à 4 Punkte)

---

## Frage 1 [4 Punkte]

Was ist der Hauptunterschied zwischen **Single-Agent-Security** und **Multi-Agent-Security**?

a) Multi-Agent braucht mehr Speicher  
b) Multi-Agent hat viele interne Grenzen zwischen Agenten die alle kommunizieren müssen  
c) Single-Agent ist unsicherer  
d) Es gibt keinen Unterschied

---

## Frage 2 [4 Punkte]

Bei der Agent-zu-Agent-Kommunikation muss Agent B nach dem Empfang einer Nachricht von Agent A validieren:

a) Nur ob die Nachricht angekommen ist  
b) Ob die Nachricht intakt ist (Integrität), ob sie wirklich von Agent A kommt (Authentizität), und ob sie aktuell genug ist (Freshness)  
c) Nur den Inhalt der Nachricht  
d) Ob Agent A online ist

---

## Frage 3 [4 Punkte]

**Message Injection** als Angriffsvektor bedeutet:

a) Der Angreifer löscht Nachrichten  
b) Der Angreifer schaltet sich in den Kommunikationskanal und injiziert bösartige Nachrichten  
c) Der Angreifer verlangsamt die Nachrichtenübertragung  
d) Der Angreifer archiviert Nachrichten

---

## Frage 4 [4 Punkte]

**Replay Attacks** bei Agent-Kommunikation nutzen aus, dass:

a) Das Netzwerk zu langsam ist  
b) Gültige Nachrichten aufgezeichnet und später erneut gesendet werden können  
c) Agenten zu viele Nachrichten senden  
d) Die Verschlüsselung zu schwach ist

---

## Frage 5 [4 Punkte]

Eine **Trust-Zone** in einem Multi-Agent-System ist:

a) Ein Bereich in dem alle Agenten identisch sind  
b) Ein Bereich in dem alle Komponenten das gleiche Security-Level teilen  
c) Ein Bereich der nicht verschlüsselt ist  
d) Ein Bereich für neue Agenten

---

## Frage 6 [4 Punkte]

Die 6 STRIDE-Kategorien für Threat Modeling sind: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege. Was beschreibt **Tampering**?

a) Identität fälschen  
b) Daten während der Übertragung manipulieren  
c) Abstreiten von Aktionen  
d) Rechte ausweiten

---

## Frage 7 [4 Punkte]

**RBAC** (Role-Based Access Control) für Agenten bedeutet:

a) Alle Agenten haben die gleichen Rechte  
b) Rollen definieren was ein Agent tun darf, Agenten werden Rollen zugewiesen  
c) RBAC gibt es nur für menschliche Benutzer  
d) RBAC ist eine Verschlüsselungsmethode

---

## Frage 8 [4 Punkte]

Das **Least-Privilege-Prinzip** für Agenten besagt:

a) Der Agent darf nur mit dem kleinsten LLM arbeiten  
b) Jeder Agent erhält nur die Berechtigungen die er für seine spezifische Aufgabe braucht  
c) Der Agent bekommt minimalen Speicherplatz  
d) Least-Privilege gilt nur für externe Agenten

---

## Frage 9 [4 Punkte]

Für eine sichere Agent-Nachricht sind mehrere Schichten nötig. Welche Schicht **verschlüsselt** den eigentlichen Inhalt?

a) Envelope  
b) Authentication Layer  
c) Encryption Layer  
d) Content Layer

---

## Frage 10 [4 Punkte]

**HMAC** (Hash-based Message Authentication Code) wird verwendet für:

a) Verschlüsselung des gesamten Nachrichteninhalts  
b) Authentifizierung dass eine Nachricht vom richtigen Absender stammt und nicht manipuliert wurde  
c) Komprimierung von Nachrichten  
d) Archivierung von Nachrichten

---

# TEIL B — True/False (15 Punkte, 5 Fragen à 3 Punkte)

---

## Frage 11 [3 Punkte]

**Aussage:** "In einem Multi-Agent-System muss jeder Agent jedem anderen Agenten vertrauen, da sie Teil desselben Systems sind."

Wahr oder Falsch?

---

## Frage 12 [3 Punkte]

**Aussage:** "Session Hijacking bedeutet, dass ein Angreifer eine bestehende, authentifizierte Session zwischen Agenten übernimmt."

Wahr oder Falsch?

---

## Frage 13 [3 Punkte]

**Aussage:** "Bei RBAC kann ein Agent mehrere Rollen haben, und die effektiven Berechtigungen sind die Vereinigung aller Rollen-Berechtigungen."

Wahr oder Falsch?

---

## Frage 14 [3 Punkte]

**Aussage:** "Ein Timestamp in einer sicheren Nachricht ist wichtig, um Replay-Angriffe zu verhindern."

Wahr oder Falsch?

---

## Frage 15 [3 Punkte]

**Aussage:** "Authentifizierung und Verschlüsselung sind dasselbe — wenn eine Nachricht verschlüsselt ist, weiß man auch wer der Absender ist."

Wahr oder Falsch?

---

# TEIL C — Zuordnungsfrage (15 Punkte)

---

## Frage 16 [15 Punkte]

Ordne die folgenden **STRIDE-Kategorien** den richtigen **Beschreibungen und Multi-Agent-Beispielen** zu:

**Kategorien:**
- S (Spoofing)
- T (Tampering)
- R (Repudiation)
- I (Information Disclosure)
- D (Denial of Service)
- E (Elevation of Privilege)

**Tabelle:**

| # | Beschreibung | Kategorie | Multi-Agent Beispiel |
|---|-------------|-----------|---------------------|
| A | Identität eines Agenten fälschen | __ | __ |
| B | Nachricht unterwegs ändern | __ | __ |
| C | Agent leugnet Nachricht gesendet zu haben | __ | __ |
| D | Vertrauliche Daten durch Kommunikation enthüllen | __ | __ |
| E | Kommunikationskanal blockieren | __ | __ |
| F | Agent erhält unbefugt mehr Rechte | __ | __ |

---

# TEIL D — Praxisfragen (30 Punkte)

---

## Frage 17 [10 Punkte]

Du hast folgendes Multi-Agent-System:
- **CEO Agent:** Koordiniert alle anderen Agenten, hat höchste Privilegien
- **Builder Agent:** Erstellt und modifiziert Code-Dateien
- **Security Officer:** Führt Security Audits durch, hat Zugriff auf Secrets
- **Data Manager:** Verwaltet alle Datenbanken und Memory

### Teilaufgaben:

a) Zeichne das **Trust-Zonen-Diagramm** mit mindestens 2 Zonen. Ordne die Agenten den passenden Zonen zu. (4 Punkte)

b) Definiere die **Rollen-Berechtigungen** für Builder und Security Officer mit mindestens 5 Permissions pro Rolle. (4 Punkte)

c) Begründe warum der Builder **keine** ACCESS_SECRETS Permission haben sollte. (2 Punkte)

---

## Frage 18 [10 Punkte]

Der CEO Agent sendet folgende Nachricht an den Builder:

```
TO: builder
ACTION: create_file
PATH: /workspace/builder/app.py
CONTENT: # neuer Code
```

### Analysiere:

a) Welche **drei Schichten** sollte diese Nachricht mindestens haben (gemäß sicherer Nachrichten-Anatomie)? (3 Punkte)

b) Erkläre für jede Schicht kurz ihren Zweck. (3 Punkte)

c) Der Angreifer hat Zugang zum Message Queue. Was könnte er tun, und welche Eigenschaften der sicheren Nachricht schützen dagegen? (4 Punkte)

---

## Frage 19 [10 Punkte]

Du implementierst ein RBAC-System für Agenten.

### Implementiere:

a) Definiere eine **Permission-Enum** mit mindestens 8 verschiedenen Permissions (z.B. READ_FILES, WRITE_FILES, etc.) (3 Punkte)

b) Definiere eine **Role-Klasse** mit name, permissions (Set), und einer has_permission()-Methode. (4 Punkte)

c) Implementiere eine einfache **RBACEngine** mit authorize()-Methode, die prüft ob ein Agent eine bestimmte Permission hat. (3 Punkte)

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
