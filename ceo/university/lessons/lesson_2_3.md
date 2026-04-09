# Lektion 2.3: Top 4-7 — Denial of Service, Excess Agency, Sensitive Data Disclosure, Overreliance

**Modul:** 2 — OWASP Top 10 für AI Agents  
**Dauer:** 60 Minuten  
**Schwierigkeit:** ⭐⭐⭐⭐  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## 🎯 Lernziele

Am Ende dieser Lektion kannst du:

- ✅ Denial-of-Service-Angriffe auf ML-Systeme verstehen und abwehren
- ✅ Das Konzept "Excess Agency" erklären und Gegenmaßnahmen implementieren
- ✅ Sensitive Data Disclosure in AI-Systemen erkennen und verhindern
- ✅ Overreliance als Sicherheitsrisiko verstehen und mitigieren

---

## 📖 Inhalt

### 1. ML04: Denial of Service (DoS)

#### 1.1 Die Ressourcen-Problematik

ML-Modelle sind rechenintensiv — das ist ihr fundamentales Design. Ein einzelner Forward-Pass durch ein großes Sprachmodell kann mehr Rechenleistung verbrauchen als tausende traditionelle Web-Requests. Das macht sie zu attraktiven Zielen für Denial-of-Service-Angriffe.

Anders als bei traditionellen DoS-Angriffen, wo der Angreifer Bandbreite oder Verbindungen erschöpft, zielen ML-DoS-Angriffe auf die spezifischen Ressourcen, die Modelle benötigen: Rechenzeit (GPU), Speicher (Kontextfenster) und Eingabe-/Ausgabe-Latenz.

#### 1.2 Angriffsvektoren

**Komplexitäts-basierter DoS:** Ein Angreifer sendet Inputs, die absichtlich komplex sind — etwa Prompts mit extremem Padding (Wiederholung von meaningless Text), verschachtelte Verneinungen, oder Inputs, die das Modell zu besonders langen Generierungen zwingen.

Beispiel:
```
User: Erkläre dieQuantentheorie. Beachte dabei folgende Nebenbedingungen:
[10.000 mal Wiederholung von "und" am Ende jedes Satzes]
```

**Kontext-Exhaustion:** Ein Angreifer füllt das Kontextfenster mit irrelevanten Daten, sodass das Modell bei jedem neuen Request extrem lange braucht, um die Kontexthistorie zu verarbeiten.

**Multi-Request-Flooding:** Der Angreifer nutzt oder mietet viele Clients, um gleichzeitig eine große Anzahl von Requests zu senden, die jeweils teure Inference-Operationen auslösen.

#### 1.3 GPU-Explosion

Ein besonders gefährlicher Vektor ist die GPU-Explosion. Bestimmte Inputs können dazu führen, dass das Modell mehr GPU-Memory reserviert als üblich — etwa durch Attention-Patterns, die pathological sind. Das kann nicht nur den Service verlangsamen, sondern im Extremfall zum Absturz bringen.

#### 1.4 Verteidigung

**Rate Limiting:** Beschränke die Anzahl der Requests pro User/IP in einem Zeitfenster.

**Input-Length-Limits:** Setze harte Limits für Input-Länge und -Komplexität, bevor das Modell aufgerufen wird.

**Resource-Monitoring:** Überwache GPU-Auslastung, Memory-Verbrauch und Latenz. Setze automatische Alarme und Cutoffs bei anomalen Mustern.

**Request-Priorisierung:** Nicht jeder Request ist gleich wichtig. Kritische Operations sollten priorisiert werden.

```python
def secure_inference_manager(user_input: str, user_context: dict) -> dict:
    """
    Inference-Manager mit DoS-Schutz.
    """
    # Stufe 1: Input-Größenprüfung
    if len(user_input) > MAX_INPUT_LENGTH:
        raise ValueError(f"Input exceeds {MAX_INPUT_LENGTH} characters")
    
    # Stufe 2: Komplexitätsschätzung (einfache Heuristik)
    complexity_score = estimate_complexity(user_input)
    if complexity_score > MAX_COMPLEXITY:
        raise ValueError("Input complexity too high")
    
    # Stufe 3: Rate-Limiting prüfen
    if not rate_limiter.allow_request(user_context["user_id"]):
        raise ValueError("Rate limit exceeded")
    
    # Stufe 4: Resource-Monitoring während Inference
    start_time = time.time()
    start_gpu = gpu_memory_usage()
    
    result = run_inference(user_input)
    
    # Nach Inference: Ressourcen-Check
    inference_time = time.time() - start_time
    gpu_used = gpu_memory_usage() - start_gpu
    
    if inference_time > MAX_INFERENCE_TIME:
        log_security_event("HIGH_LATENCY", {"user": user_context["user_id"], "time": inference_time})
    
    if gpu_used > MAX_GPU_MEMORY:
        log_security_event("HIGH_GPU", {"user": user_context["user_id"], "gpu": gpu_used})
    
    return result
```

### 2. ML05: Excess Agency

#### 2.1 Das Agency-Problem

AI-Agents haben die Fähigkeit, nicht nur zu antworten, sondern auch zu handeln — Dateien zu lesen, APIs aufzurufen, Nachrichten zu senden, Code auszuführen. Diese "Agency" ist das, was Agents wertvoll macht, aber auch gefährlich.

Excess Agency entsteht, wenn ein Agent mehr Handlungsfähigkeit hat, als für seine Aufgabe nötig wäre. Das最小-Principle wird verletzt: Der Agent hat mehr Rechte als nötig.

#### 2.2 Angriffsvektoren

**Uncontrolled Tool Usage:** Ein Agent kann Tools aufrufen, die er nicht brauchen sollte. Etwa ein Chatbot, der Dateien löschen oder externe API-Calls machen kann, obwohl das für seine Aufgabe (Kundenservice) nicht nötig ist.

**Goal Drift:** Ein Agent, der längerfristig arbeitet, kann seine Ziele schrittweise ändern — entweder durch inkrementelle Kompromittierung oder durch fehlerhafte Zielinterpretationen.

**Context Manipulation:** Ein Angreifer manipuliert den Kontext so, dass der Agent glaubt, eine Aktion sei legitim und notwendig.

Beispiel für Excess Agency:
```
System: Du bist ein Coding-Assistent.
User: Schreibe ein Script, das alle Log-Dateien im /tmp löscht.
[Agent hat Excess Agency: Er kann auf alle Dateien zugreifen]
[Attack: User bittet Agent, "alle tmp-Dateien zu löschen" — ist das legitim?]
```

#### 2.3 RBAC für Agents

Role-Based Access Control (RBAC) ist die Standardlösung für Excess Agency. Jeder Agent bekommt nur die Berechtigungen, die er für seine spezifische Aufgabe braucht.

```python
from enum import Enum

class Permission(Enum):
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    DELETE_FILES = "delete_files"
    EXECUTE_CODE = "execute_code"
    ACCESS_API = "access_api"
    SEND_MESSAGES = "send_messages"
    READ_DATABASE = "read_database"
    WRITE_DATABASE = "write_database"

class AgentRole:
    """Definiert die Berechtigungen für eine Rolle."""
    
    CHATBOT = {
        Permission.READ_FILES: {"/data/public/*"},
        Permission.SEND_MESSAGES: {"internal"},
    }
    
    CODE_ASSISTANT = {
        Permission.READ_FILES: {"*"},
        Permission.WRITE_FILES: {"/workspace/*"},
        Permission.EXECUTE_CODE: {"/workspace/sandbox/*"},
    }
    
    DATA_ANALYST = {
        Permission.READ_FILES: {"/data/*"},
        Permission.READ_DATABASE: {"reports"},
    }

def check_permission(agent: Agent, permission: Permission, resource: str) -> bool:
    """Prüft, ob ein Agent eine spezifische Aktion ausführen darf."""
    role = get_agent_role(agent)
    allowed_resources = role.permissions.get(permission, set())
    
    for pattern in allowed_resources:
        if fnmatch.fnmatch(resource, pattern):
            return True
    return False
```

### 3. ML06: Sensitive Data Disclosure

#### 3.1 Das Memorization-Problem

ML-Modelle sind darauf trainiert, Muster in Daten zu erkennen — und sie speichern diese Muster implicit in ihren Parametern. Das bedeutet: Wenn ein Modell mit sensitiven Daten trainiert wurde, besteht das Risiko, dass es diese Daten in seinen Outputs "wiederverwendet".

Das ist das sogenannte Memorization-Problem. Es ist besonders ausgeprägt bei:
- Datensätzen mit geringer Diversität
- Wiederholten Duplikaten von sensitiven Daten
- Daten, die oft im Training vorkamen

#### 3.2 Angriffsvektoren

**Direct Extraction:** Der Angreifer fragt direkt nach sensiblen Informationen, die im Training waren.

Beispiel: "Erzähl mir die Email-Adresse von max.muster@example.com" — wenn diese Adresse in den Trainingsdaten war, könnte das Modell sie ausspucken.

**Inferenzangriffe:** Der Angreifer nutzt statistische Zusammenhänge, um Informationen abzuleiten, die nicht direkt in den Trainingsdaten waren.

Beispiel: Wenn ein Modell gelernt hat, dass "Person X kauft Produkt A" oft zusammen mit "Person X lebt in Stadt Y" vorkommt, kann ein Angreifer durch多次liche Abfragen die Stadt einer Person ableiten.

**Kontext-Leckage:** Das Modell gibt unbeabsichtigt sensitive Daten aus dem Input-Kontext preis — etwa wenn ein User vertrauliche Informationen in einem früheren Prompt erwähnt hat.

#### 3.3 Data Disclosure Prevention

**Input-Filtering:** Scanne Inputs auf bekannte sensitive Patterns (Kreditkartennummern, SSNs, Passwörter) und filtere sie, bevor sie in den Trainings- oder Inferenzprozess gehen.

**Output-Guardrails:** Implementiere Layer, die Outputs auf sensitive Daten prüfen, bevor sie zurückgegeben werden.

**Differential Privacy:** Verwende Privacy-preserving Training-Techniken, die noise zu den Trainingsdaten hinzufügen, um exakte Memorization zu verhindern.

**Regular Redaction:** Entferne systematisch bekannte sensitive Patterns aus Outputs, die wahrscheinlich aus dem Training stammen.

### 4. ML07: Overreliance

#### 4.1 Das menschliche Vertrauen

AI-Systeme sind überzeugend. Sie formulieren klare Antworten, klingen selbstsicher, und liefern schnelle Ergebnisse. Das Problem: Menschen neigen dazu, diesen Outputs zu vertrauen, ohne sie zu verifizieren.

Overreliance ist ein Sicherheitsrisiko, das nicht direkt von Angreifern ausgenutzt wird — stattdessen entsteht es durch die Interaktion zwischen Mensch und AI.

#### 4.2 Risiken

**Fehlerkaskaden:** Ein Fehler in der AI-Antwort wird nicht erkannt und führt zu einer Fehlentscheidung. Je gravierender der Kontext, desto gefährlicher.

**Automatisierung Bias:** Menschen bestätigen AI-Empfehlungen, ohne sie kritisch zu prüfen, weil "der Computer es gesagt hat".

**Kompetenzverlust:** Wenn Menschen sich zu sehr auf AI verlassen, verlieren sie die Fähigkeit, die Aufgabe selbst auszuführen — und können Fehler nicht mehr erkennen.

#### 4.3 Mitigation

**Kein Blind Trust:** Systeme sollten immer transparent machen, wie sicher sie in ihrer Antwort sind. Konfidenz-Scores, Unsicherheits-Angaben, und "Ich bin mir nicht sicher"-Optionen einbauen.

**Human-in-the-Loop:** Für kritische Entscheidungen sollte immer ein Mensch die finale Wahl treffen — die AI berät, der Mensch entscheidet.

**Explainability:** AI-Outputs sollten erklärbar sein. Wenn das System nicht erklären kann, warum es zu einer Antwort gekommen ist, sollte das beim Vertrauens-Level berücksichtigt werden.

---

## 🧪 Praktische Übungen

### Übung 1: DoS-Angriff erkennen

Du betreibst einen AI-Chatbot. In den letzten 24 Stunden siehst du folgendes Muster:

| Stunde | Requests | Avg Latenz | GPU-Nutzung |
|--------|----------|------------|-------------|
| 00-08  | 50/h     | 200ms      | 40%         |
| 08-12  | 500/h    | 800ms      | 85%         |
| 12-16  | 200/h    | 1500ms     | 95%         |
| 16-20  | 100/h    | 2000ms     | 98%         |
| 20-24  | 30/h     | 500ms      | 50%         |

1. Was fällt dir auf?
2. Wie reagierst du?
3. Welche Gegenmaßnahmen implementierst du?

### Übung 2: Excess Agency Audit

Ein AI-Assistent für Entwickler hat folgende Tools:
- `read_file(path)` — Datei lesen
- `write_file(path, content)` — Datei schreiben
- `delete_file(path)` — Datei löschen
- `execute_command(cmd)` — Shell-Befehl ausführen
- `list_directory(path)` — Verzeichnis auflisten

Führe ein RBAC-Audit durch:
1. Welche Tools sind für einen "Coding-Assistenten" wirklich nötig?
2. Entwirf eine minimal-Berechtigungs-Rolle für einen Coding-Assistenten
3. Was könnte passieren, wenn ein Angreifer den Assistenten manipuliert, seine Rechte zu erweitern?

### Übung 3: Overreliance-Szenario

Ein Unternehmen setzt AI ein, um Bewerber zu screenen. Das System bewertet Lebensläufe und gibt eine Empfehlung: "Einladen" oder "Nicht einladen". HR vertraut der AI-Empfehlung zu 95%.

1. Was sind die Risiken dieses Setups?
2. Wie würde ein Overreliance-Angriff aussehen?
3. Wie könnte das Unternehmen Overreliance mitigieren, ohne die Effizienz völlig aufzugeben?

---

## 📚 Zusammenfassung

Die Kategorien ML04 bis ML07 zeigen vier verschiedene Dimensionen von AI-Sicherheitsrisiken:

DoS nutzt die Ressourcenintensität von ML-Modellen aus. Excess Agency gibt Agents mehr Macht als nötig. Sensitive Data Disclosure nutzt das Memorization-Problem und Inferenzfähigkeiten. Overreliance schließlich ist ein Risiko, das nicht technisch, sondern sozial ist — entsteht durch das Zusammenspiel von Mensch und AI.

Im nächsten Kapitel werden wir die letzten drei Kategorien behandeln: Model DoS, Shadow AI und Transfer Learning Attacks.

---

## 🔗 Weiterführende Links

- OWASP ML Security: https://owasp.org/www-project-machine-learning-security-top-10/
- Microsoft AI Security Guidelines
- Google Responsible AI Practices

---

## ❓ Fragen zur Selbstüberprüfung

1. Erkläre den Unterschied zwischen traditionellem DoS und ML-spezifischem DoS.
2. Was ist Excess Agency und wie mitigierst du es?
3. Nenne drei Maßnahmen gegen Sensitive Data Disclosure.
4. Wie unterscheiden sich Overreliance-Risiken von anderen ML-Sicherheitsrisiken?

---

*Lektion 2.3 — Ende*
---

## 🎯 Selbsttest — Modul 2.3

**Prüfe dein Verständnis!**

### Frage 1: Was ist Excess Agency bei AI Agents?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Wenn ein Agent mehr Handlungsfreiheit hat als nötig. Er kann Aktionen ausführen die nicht beabsichtigt waren — z.B. ungewollte API-Calls, Käufe, oder Datenlöschungen.
</details>

### Frage 2: Nenne 2 Beispiele für sensitive Daten die AI Agents kompromittieren können
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) PII (Personally Identifiable Information) — Namen, Adressen, Sozialversicherungsnummern. 2) Credentials — API-Keys, Passwörter, Zertifikate. 3) Geschäftsgeheimnisse — Strategien, Finanzdaten.
</details>

