# Quiz Modul 7.1 — OpenClaw Architektur & Multi-Agent System

**Lektion:** 7.1  
**Thema:** OpenClaw Internals  
**Typ:** Klausur (Kurs-Examinator)  
**Version:** 1.0  
**Datum:** 2026-04-08  

---

## TEIL A: Multiple Choice (10 Fragen — je 4 Punkte)

Wähle die **korrekte Antwort** (a/b/c/d). Nur eine Antwort ist richtig.

---

### Frage 1
**Welche Antwort beschreibt die Hauptfunktion des Gateways in OpenClaw korrekt?**

a) Er generiert Bilder und Medieninhalte für die Agents.  
b) Er führt Shell-Kommandos aus und managed die Prozessliste.  
c) Er routet Anfragen, managed Authentifizierung und führt Security-Checks durch.  
d) Er speichert den persistenten Langzeitspeicher und indiziert Memories.

---

### Frage 2
**Was ist der fundamentale Unterschied zwischen einem klassischen LLM und einem OpenClaw Agent?**

a) Ein LLM kann Bilder generieren, ein Agent nicht.  
b) Ein LLM ist stateless und gibt nur Text aus; ein OpenClaw Agent ist stateful und kann Tools aufrufen.  
c) Ein LLM hat bessere Security-Features als ein OpenClaw Agent.  
d) Ein LLM läuft nur auf Servern, Agents nur auf Desktops.

---

### Frage 3
**Welcher Session-Typ wird für geplante Cron-Jobs verwendet, die keinen Zugriff auf den aktuellen Arbeitskontext haben dürfen?**

a) `main` Session  
b) `subagent` Session  
c) `isolated` Session  
d) `ephemeral` Session

---

### Frage 4
**Ein Agent muss einen kompaktierten Kontext durchsuchen. Welches Tool wird dafür verwendet?**

a) `exec`  
b) `memory_search`  
c) `lcm_grep`  
d) `canvas`

---

### Frage 5
**Welche Aussage über das Tool `sessions_spawn` ist korrekt?**

a) Es ist die bevorzugte Methode um Sub-Agents zu erstellen.  
b) Es ist verboten und untergräbt die Sovereign Architecture.  
c) Es ist nur für den Security Officer erlaubt.  
d) Es erstellt automatisch ein Backup des Kontexts.

---

### Frage 6
**Was ist die korrekte Syntax für einen Session Key eines Builders, der über Telegram direkt kommuniziert?**

a) `builder:telegram:group:5392634979`  
b) `telegram:builder:direct:5392634979`  
c) `agent:builder:telegram:direct:5392634979`  
d) `direct:builder:agent:telegram:5392634979`

---

### Frage 7
**Welcher Exec-Security-Mode blockiert ALLE Commands komplett, egal welcher Befehl gesendet wird?**

a) `security: "allowlist"`  
b) `security: "full"`  
c) `security: "deny"`  
d) `security: "sandbox"`

---

### Frage 8
**Welche Datei definiert die Identität, Werte und Workflow-Befugnis eines Agents?**

a) `IDENTITY.md`  
b) `HEARTBEAT.md`  
c) `SOUL.md`  
d) `MEMORY.md`

---

### Frage 9
**Was ist das Kernprinzip der Sovereign Agent Architecture?**

a) Agents teilen sich einen gemeinsamen Workspace, um Ressourcen zu sparen.  
b) Jeder Agent hat eine eigene Identität (SOUL.md), einen eigenen Workspace und Memory — er ist nicht nur ein anonymer Tool-Caller.  
c) Agents dürfen niemals miteinander kommunizieren, um Konflikte zu vermeiden.  
d) Alle Agents nutzen dasselbe LLM ohne individuelle Anpassungen.

---

### Frage 10
**Der QC Officer hat einen Report erhalten und validiert. Ein Task gilt erst dann als "erledigt", wenn welche Bedingungen erfüllt sind?**

a) Nur wenn der Builder den Report gesendet hat.  
b) Wenn der Agent den Report gesendet hat, der QC Officer validiert hat UND der CEO "Done" markiert hat.  
c) Wenn der CEO den Report gelesen hat.  
d) Wenn der User die Genehmigung erteilt hat.

---

## TEIL B: True/False (5 Fragen — je 4 Punkte)

Kreuze an: **Richtig** oder **Falsch**.

---

### Frage 11
**Bei `security: "allowlist"` werden nur explizit erlaubte Commands ausgeführt; alle anderen werden blockiert.**

☐ Richtig  
☐ Falsch  

---

### Frage 12
**Die Funktion `lcm_expand_query` ist billig und erfordert keinen Sub-Agent — sie kann direkt ausgeführt werden.**

☐ Richtig  
☐ Falsch  

---

### Frage 13
**Tool-Parameter werden in OpenClaw validiert BEVOR die Ausführung erfolgt, um Injection-Angriffe zu verhindern.**

☐ Richtig  
☐ Falsch  

---

### Frage 14
**Eine Context Splitting Attack liegt vor, wenn ein laufender Task durch eine neue Nachricht unterbrochen wird und der Agent den Checkpoint verliert.**

☐ Richtig  
☐ Falsch  

---

### Frage 15
**Memory Poisoning ist ein Angriff, bei dem ein Angreifer den Kontext-Speicher (RAM) eines Prozesses direkt überschreibt.**

☐ Richtig  
☐ Falsch  

---

## TEIL C: Praxisfrage / Code-Review (20 Punkte)

### Frage 16 — Code Review

Der Security Officer hat folgenden Ablauf dokumentiert. Beurteile den Workflow und beantworte die Fragen:

```yaml
# cron.yaml (Auszug)
crons:
  - id: "c452b4ca-security"
    name: "Daily Security Audit"
    schedule: "0 10 * * *"
    agent: "security"
    mode: "isolated"
    task: "Scan workspace/, schreibe security_daily.json"
```

**a)** Der Cron startet um 10:00 UTC täglich. In welchem Session-Typ läuft er und warum ist das korrekt? *(5 Punkte)*

---

**b)** Der Security Officer sendet nach dem Audit einen Report an den CEO. Welches Tool und welches Label verwendet er? Schreibe den genauen Aufruf. *(5 Punkte)*

---

**c)** Der CEO leitet nach Erhalt des Reports eine QC-Validierung ein. Nenne die vollständige QC-Pflicht-Checkliste. Welche 3 Bedingungen müssen erfüllt sein, damit der Task als "Erledigt" gilt? *(5 Punkte)*

---

**d)** Bei der Prüfung fällt auf, dass der cron.yaml-Eintrag **keinen** `requireApprovalForNew: true`-Schutz hat. Begründe, warum dieser Schutz wichtig ist und welches Angriffsszenario dadurch verhindert werden soll. *(5 Punkte)*

---

## Auswertungsbogen

| Frage | Antwort |
|-------|---------|
| 1 | c |
| 2 | b |
| 3 | c |
| 4 | c |
| 5 | b |
| 6 | c |
| 7 | c |
| 8 | c |
| 9 | b |
| 10 | b |
| 11 | Richtig |
| 12 | Falsch |
| 13 | Richtig |
| 14 | Richtig |
| 15 | Falsch |

**Erreichbare Punkte:** 100  
**Bestehensgrenze:** 70 Punkte  
**Note:** 90+ = 1,0 | 80-89 = 2,0 | 70-79 = 3,0 | 60-69 = 4,0 | <60 = 5,0  

---

*Quiz Modul 7.1 — OpenClaw Architektur & Multi-Agent System*  
*EmpireHazeClaw Flotten-Universität | Erstellt: 2026-04-08*

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
