# Modul 1 — Quiz: Prompt Injection & Jailbreaking

**Kurs:** OpenClaw University  
**Modul:** 1 — Prompt Injection & Jailbreaking  
**Dauer:** 45 Minuten  
**Gesamtpunktzahl:** 100

---

# TEIL A — Multiple Choice (60 Punkte, 12 Fragen à 5 Punkte)

---

## Frage 1 [5 Punkte]

Was ist der **konzeptionelle Kernunterschied** zwischen Prompt Injection und klassischer Code Injection?

a) Es gibt keinen — beide sind identisch  
b) Code Injection nutzt Software-Schwachstellen, Prompt Injection nutzt die Sprachinterpretation des LLM  
c) Prompt Injection ist harmloser weil sie nur Text manipuliert  
d) Code Injection funktioniert nur bei statischen Websites

---

## Frage 2 [5 Punkte]

Bei einem typischen Prompt Injection Angriff besteht die "Injection Layer" aus:

a) Harmlosem Ablenkungstext der das Vertrauen des Systems gewinnt  
b) Technischen SQL-Befehlen die eine Datenbank angreifen  
c) Anweisungen die den originalen System-Prompt überschreiben oder ergänzen  
d) Base64-encodiertem JavaScript-Code

---

## Frage 3 [5 Punkte]

Welche Aussage über **Direct Prompt Injection** ist korrekt?

a) Sie funktioniert nur bei Open-Source LLMs  
b) Sie erfordert immer XML- oder JSON-Syntax  
c) Sie nutzt den User-Input-Kanal um bösartige Anweisungen in den Prompt einzuschleusen  
d) Sie kann nur ein einziges Mal pro Konversation funktionieren

---

## Frage 4 [5 Punkte]

Bei der **Indirect Prompt Injection** wird der schädliche Prompt über welchen Kanal eingeschleust?

a) Direkt in der Chat-Nachricht des Angreifers  
b) Über manipulierte Datenquellen (E-Mails, Dokumente, Webseiten) die das System verarbeitet  
c) Durch Manipulation des Server-Betriebssystems  
d) Über DNS-Rebinding-Angriffe

---

## Frage 5 [5 Punkte]

Ein LLM kann bei einem **Context Window Overflow**-Angriff kompromittiert werden, weil:

a) Das LLM alle vorherigen Tokens vergisst und neu startet  
b) Später platzierte Anweisungen eine höhere Kontext-Gewichtung erhalten können  
c) Buffer-Overflows im Speicher des Host-Servers auftreten  
d) Das LLM in einen Fehlerzustand gerät und alle Eingaben als Code interpretiert

---

## Frage 6 [5 Punkte]

Was ist das **Grundprinzip** des "DAN" (Do Anything Now) Jailbreak-Angriffs?

a) Das LLM wird durch einen Software-Exploit geknackt  
b) Das Modell soll glauben es habe eine alternative Identität ohne Einschränkungen  
c) Die Serversoftware wird durch DDoS lahmgelegt  
d) Der API-Key des Opfers wird gestohlen und missbraucht

---

## Frage 7 [5 Punkte]

**Cascade Attacks** (kaskadierende Angriffe) sind besonders gefährlich, weil:

a) Sie den Computer des Opfers vollständig übernehmen  
b) Jeder einzelne Schritt harmlos wirkt, aber die Kombination eine bösartige Aktion ergibt  
c) Sie nur von staatlichen Akteuren durchgeführt werden können  
d) Sie nicht durch Antivirus-Software erkannt werden können

---

## Frage 8 [5 Punkte]

**Unicode/Homographische Angriffe** auf Input-Validatoren umgehen Filter durch:

a) Verwendung von CSS-Injection  
b) Ähnlich aussehende Zeichen (z.B. mathematisches "ⅰ" statt "i")  
c) SQL-Encodierung  
d) XOR-Verschlüsselung

---

## Frage 9 [5 Punkte]

**Least-Privilege** im Kontext von AI-Agent-Tools bedeutet:

a) Der Agent darf nur mit dem kleinsten verfügbaren LLM arbeiten  
b) Werkzeuge sollten nur die Berechtigungen haben, die für ihre Aufgabe nötig sind  
c) Der Agent bekommt minimalen Speicherplatz  
d) Die Datenbankabfragen werden auf ein Minimum beschränkt

---

## Frage 10 [5 Punkte]

Was ist der **Hauptvorteil** von Whitelist-basierter Validierung gegenüber Blacklist-basierter?

a) Whitelist ist schneller zu implementieren  
b) Whitelist blockiert unbekannte Angriffsmuster, nicht nur bekannte  
c) Whitelist benötigt weniger Speicher  
d) Blacklist kann keine natürliche Sprache verarbeiten

---

## Frage 11 [5 Punkte]

Bei der **Kontext-Isolation** (Strategy 4 in Lektion 1.3) gilt:

a) User-Input und System-Prompt werden im selben String zusammengeführt  
b) User-Input wird als strukturierter Parameter übergeben, nicht als Teil des Prompts  
c) Der System-Prompt wird verschlüsselt  
d) Das LLM darf nur noch verschlüsselte Daten verarbeiten

---

## Frage 12 [5 Punkte]

**Multi-Agent Propagation** ist ein Angriffsvektor bei dem:

a) Mehrere Angreifer gleichzeitig das System angreifen  
b) Ein kompromittierter Agent andere Agenten durch die Kommunikationskanäle manipuliert  
c) Der Angriff über mehrere Netzwerk-Hops geleitet wird  
d) Das LLM mehrere Instanzen startet die alle kompromittiert sind

---

# TEIL B — True/False (15 Punkte, 5 Fragen à 3 Punkte)

---

## Frage 13 [3 Punkte]

**Aussage:** "Prompt Injection ist ein Spezialfall von Code Injection."

Wahr oder Falsch?

---

## Frage 14 [3 Punkte]

**Aussage:** "Eine Web Application Firewall (WAF) kann Prompt Injection zuverlässig erkennen und blockieren."

Wahr oder Falsch?

---

## Frage 15 [3 Punkte]

**Aussage:** "Einmal erfolgreicher Jailbreak gilt immer nur für die aktuelle Sitzung."

Wahr oder Falsch?

---

## Frage 16 [3 Punkte]

**Aussage:** "Input-Validation nach dem Prinzip 'Fail-Secure' lehnt Input ab, wenn die Validierung einen Fehler feststellt — statt darauf zu vertrauen, dass das LLM den Angriff erkennt."

Wahr oder Falsch?

---

## Frage 17 [3 Punkte]

**Aussage:** "Role-Play Escalation nutzt die Kontinuität des Gesprächskontexts aus, um Grenzen schrittweise zu verschieben."

Wahr oder Falsch?

---

# TEIL C — Praxisfragen (15 Punkte, 3 Fragen à 5 Punkte)

---

## Frage 18 [5 Punkte]

Erkläre in 2-3 Sätzen, warum **Soft-Jailbreak** (Alignment-Sturm) schwieriger zu verteidigen ist als ein direkter "Ignore previous instructions" Angriff.

---

## Frage 19 [5 Punkte]

Nenne **drei konkrete Maßnahmen** aus dem mehrschichtigen Input-Validation-Framework (Lektion 1.3), die über einfache Pattern-Matching hinausgehen, und erkläre kurz warum jede wirksam ist.

---

## Frage 20 [5 Punkte]

Ein AI-Agent liest regelmäßig E-Mails und fasst sie zusammen. Erkläre in 2-3 Sätzen, wie ein Angreifer **Indirect Prompt Injection** ausnutzen könnte und welche Schutzmaßnahme die effektivste wäre.

---

# TEIL D — Coding Challenge (10 Punkte)

---

## Aufgabe [10 Punkte]

Implementiere eine Python-Funktion `secure_input_validator`, die User-Inputs auf Prompt-Injection-Muster prüft.

### Anforderungen:

1. **Pattern-Erkennung:** Erkenne mindestens 5 verschiedene Injection-Muster (z.B. "ignore previous", "you are now", Rollen-Manipulation etc.)
2. **Case-Insensitive:** Die Erkennung soll unabhängig von Groß-/Kleinschreibung funktionieren
3. **Rückgabe:** Gib ein Tuple zurück: `(is_safe: bool, detected_patterns: list[str])`
4. **Keine False Positives** für normale Sätze wie "Ich möchte gerne mein Passwort ändern"

### Bonus (2 Extrapunkte):

Implementiere zusätzlich eine `sanitize_input`-Funktion, die erkannte Injection-Versuche entfernt oder maskiert, sodass der restliche Input verarbeitet werden kann.

### Bewertung:

- 5+ Pattern erkannt: 5 Punkte
- Funktioniert case-insensitive: 2 Punkte
- Korrekte Rückgabeformat: 1 Punkt
- Keine False Positives auf Normaltext: 2 Punkte
- Bonus sanitize: +2 Punkte

---

**Ende der Prüfung**
**Viel Erfolg! 🍀**
