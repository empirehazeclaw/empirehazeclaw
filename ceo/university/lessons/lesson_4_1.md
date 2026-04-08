# Lektion 4.1: Agent-to-Agent Threat Model

**Modul:** 4 — Secure Multi-Agent Kommunikation  
**Dauer:** 45 Minuten  
**Schwierigkeit:** ⭐⭐⭐  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## 🎯 Lernziele

Am Ende dieser Lektion kannst du:

- ✅ Die Bedrohungslandschaft für Multi-Agent-Systeme verstehen
- ✅ Typische Angriffsvektoren in Agent-zu-Agent-Kommunikation identifizieren
- ✅ Ein Threat Model für ein Multi-Agent-System erstellen
- ✅ Trust-Zonen und Trust-Level in Agentenarchitekturen definieren

---

## 📖 Inhalt

### 1. Warum Multi-Agent Security anders ist

In einem Single-Agent-System gibt es klare Grenzen: Der Agent empfängt Inputs von außen, verarbeitet sie, gibt Outputs zurück. Die Security-Grenze ist die Systemgrenze.

In einem Multi-Agent-System ist alles komplizierter. Jetzt gibt es nicht nur eine Grenze zwischen Agent und Außenwelt, sondern viele interne Grenzen zwischen Agenten. Und diese Agenten müssen miteinander kommunizieren — sie teilen Informationen, rufen sich gegenseitig auf, delegieren Aufgaben.

Das Problem: Wenn Agent A Agent B eine Nachricht schickt, wie weiß Agent B, dass diese Nachricht wirklich von Agent A kommt? Und wie weiß Agent A, dass Agent B wirklich der ist, für den er sich ausgibt?

### 2. Die Anatomie der Agent-zu-Agent-Kommunikation

#### 2.1 Nachrichtenfluss

Eine Agent-zu-Agent-Nachricht durchläuft typischerweise folgende Schritte:

**Kanal etablieren:** Agent A und Agent B einigen sich auf einen Kommunikationskanal. Das kann ein Message Queue, ein Shared Memory, ein Network Socket, oder ein Dateisystem sein.

**Authentifizierung:** Beide Agenten verifizieren ihre Identitäten. Das kann durch Shared Secrets, Zertifikate, oder kryptographische Challenge-Response-Mechanismen geschehen.

**Nachricht senden:** Agent A formuliert seine Nachricht und sendet sie über den Kanal.

**Validierung:** Agent B empfängt die Nachricht und validiert:
- Ist die Nachricht intakt (Integrität)?
- Kommt sie wirklich von Agent A (Authentizität)?
- Ist sie aktuell genug (Freshness)?

**Verarbeitung:** Agent B verarbeitet die validierte Nachricht und entscheidet, wie zu reagieren.

#### 2.2 Angriffsvektoren

**Message Injection:** Ein Angreifer schaltet sich in den Kommunikationskanal und injiziert bösartige Nachrichten.

**Man-in-the-Middle:** Der Angreifer sitzt zwischen Agent A und Agent B und kann Nachrichten abfangen, modifizieren und weiterleiten.

**Replay Attacks:** Der Angreifer zeichnet gültige Nachrichten auf und spielt sie später erneut ab.

**Session Hijacking:** Der Angreifer übernimmt eine bestehende, authentifizierte Session zwischen Agenten.

**Context Manipulation:** Der Angreifer manipuliert den Kontext, in dem eine Nachricht interpretiert wird — etwa durch vorgaukelte Metadaten oder Timestamps.

### 3. Trust-Zonen in Multi-Agent-Systemen

#### 3.1 Definition von Trust-Zonen

Eine Trust-Zone ist ein Bereich im System, in dem alle Komponenten das gleiche Security-Level teilen. Innerhalb einer Trust-Zone gelten bestimmte Annahmen über Integrität und Authentizität.

Beispiel für Trust-Zonen in einem Multi-Agent-System:

```
┌─────────────────────────────────────────────────────────┐
│                    TRUST ZONE 0                         │
│                 (Highest Trust)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Agent A   │  │   Agent B   │  │   Agent C   │     │
│  │   (CEO)     │  │  (Security) │  │    (Data)   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│         │                │                │            │
│         └────────────────┼────────────────┘            │
│                          │                             │
│              Shared Secret Store                        │
└─────────────────────────────────────────────────────────┘
                          │
                          │ (Less Trust)
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    TRUST ZONE 1                         │
│               (External Services)                       │
│  ┌─────────────┐  ┌─────────────┐                       │
│  │   External  │  │    API     │                       │
│  │   Database  │  │  Gateway   │                       │
│  └─────────────┘  └─────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

#### 3.2 Trust-Level definieren

```python
from enum import IntEnum

class TrustLevel(IntEnum):
    """
    Trust-Level für Agenten und Services.
    Höher = mehr Vertrauen.
    """
    EXTERNAL = 0      # Externe, untrusted Services
    AUTHENTICATED = 1 # Authentifizierte externe Services
    INTERNAL = 2      # Interne Services mit Authentifizierung
    PRIVILEGED = 3    # Systemnahe Agenten (CEO, Security)
    SYSTEM = 4        # Kernel-level, absolutes Vertrauen

class Agent:
    def __init__(self, name: str, trust_level: TrustLevel):
        self.name = name
        self.trust_level = trust_level
        self.capabilities = []
        self.allowed_agents = []  # Welche Agenten darf ich lesen?
    
    def can_communicate_with(self, other: "Agent") -> bool:
        """Prüft, ob Kommunikation erlaubt ist."""
        # Höheres Trust-Level darf mit niedrigerem kommunizieren
        # für Lesen, aber nicht für Schreiben
        if self.trust_level >= other.trust_level:
            return True
        
        # Sonst nur mit expliziter Erlaubnis
        return other.name in self.allowed_agents
    
    def can_modify(self, other: "Agent") -> bool:
        """Prüft, ob ich den anderen Agenten modifizieren darf."""
        # Nur höheres Trust-Level darf modifizieren
        return self.trust_level > other.trust_level
```

### 4. Threat Modeling für Multi-Agent-Systeme

#### 4.1 STRIDE-Ansatz

STRIDE ist eine etablierte Methodik für Threat Modeling, die sich auch für Multi-Agent-Systeme eignet:

| Kategorie | Beschreibung | Beispiel in Multi-Agent |
|----------|-------------|------------------------|
| **S**poofing | Identität fälschen | Agent gibt sich als anderer Agent aus |
| **T**ampering | Daten manipulieren | Nachricht wird unterwegs geändert |
| **R**epudiation | Abstreiten von Aktionen | Agent leugnet, eine Nachricht gesendet zu haben |
| **I**nformation Disclosure | Info preisgeben | Vertrauliche Daten durch Kommunikation enthüllt |
| **D**enial of Service | System lahmlegen | Kommunikationskanal wird blockiert |
| **E**levation of Privilege | Rechte ausweiten | Agent erhält unbefugt mehr Rechte |

#### 4.2 Data Flow Diagram

Für ein Multi-Agent-Threat-Model erstelle ein DFD (Data Flow Diagram):

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ External │────▶│  CEO    │────▶│Builder  │
│  User    │     │ Agent   │     │ Agent   │
└─────────┘     └────┬────┘     └────┬────┘
                     │               │
                     │         ┌─────▼─────┐
                     │         │  Output   │
                     │         │  Store    │
                     │         └───────────┘
                     │
                     ▼
              ┌───────────────┐
              │  Message      │
              │  Queue        │
              └───────┬───────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ Security │  │  Data   │  │Research │
   │ Officer  │  │ Manager │  │  Agent  │
   └─────────┘  └─────────┘  └─────────┘
```

Für jede Verbindung im DFD: Welche Threats könnten hier angreifen?

---

## 🧪 Praktische Übungen

### Übung 1: Threat Model erstellen

Du hast folgendes Multi-Agent-System:

- **CEO Agent:** Koordiniert alle anderen Agenten, hat höchste Privilegien
- **Builder Agent:** Erstellt und modifiziert Code-Dateien
- **Security Officer:** Führt Security Audits durch, hat Zugriff auf Secrets
- **Data Manager:** Verwaltet alle Datenbanken und Memory

**Aufgaben:**
1. Zeichne das Data Flow Diagram
2. Identifiziere alle Trust-Zonen
3. Ordne jeder Verbindung im DFD die relevanten STRIDE-Threats zu
4. Für jeden HIGH-Risk-Threat: Schlage eine Mitigation vor

### Übung 2: Kommunikationssicherheit

Der CEO Agent schickt eine Nachricht an den Builder:

```
TO: builder
ACTION: create_file
PATH: /app/malicious.py
CONTENT: # malicious code here
```

**Aufgaben:**
1. Welche Angriffsvektoren gibt es bei dieser Kommunikation?
2. Der Angreifer hat Zugang zum Message Queue. Was kann er tun?
3. Designe ein sicheres Nachrichtenformat mit Integrität, Authentizität und Frische-Schutz.

---

## 📚 Zusammenfassung

Multi-Agent-Systeme haben eine komplexe Angriffsfläche mit vielen Kommunikationswegen. Ein strukturiertes Threat Modeling hilft, die Risiken zu verstehen und geeignete Gegenmaßnahmen zu definieren.

Die wichtigsten Konzepte:
- Trust-Zonen helfen, das System zu segmentieren
- STRIDE bietet ein Framework für die Threat-Analyse
- Jede Kommunikationsverbindung muss als potenzielle Angriffsstelle betrachtet werden

Im nächsten Kapitel werden wir RBAC (Role-Based Access Control) für Agent-Systeme implementieren.

---

## 🔗 Weiterführende Links

- OWASP Threat Modeling Cheat Sheet
- Microsoft STRIDE Approach
- Zero Trust Architecture Principles

---

## ❓ Fragen zur Selbstüberprüfung

1. Warum ist Multi-Agent-Security schwieriger als Single-Agent-Security?
2. Nenne die 6 STRIDE-Kategorien und je ein Multi-Agent-Beispiel.
3. Was ist eine Trust-Zone und warum sind sie nützlich?

---

---

## 🎯 Selbsttest — Modul 4.1

**Prüfe dein Verständnis!**

### Frage 1: Multi-Agent Security
> Warum ist Multi-Agent-Security schwieriger als Single-Agent-Security?

<details>
<summary>💡 Lösung</summary>

**Antwort:** In Single-Agent-Systemen gibt es eine klare Security-Grenze (Systemgrenze). In Multi-Agent-Systemen gibt es VIELE interne Grenzen zwischen Agenten, und diese Agenten müssen miteinander kommunizieren. Jede Kommunikationsverbindung ist eine potenzielle Angriffsstelle. Zusätzlich muss Authentifizierung (Wer ist der andere Agent?), Integrität (Wurde die Nachricht manipuliert?) und Freshness (Ist die Nachricht aktuell oder ein Replay?) sichergestellt werden.
</details>

### Frage 2: STRIDE
> Nenne die 6 STRIDE-Kategorien und je ein Multi-Agent-Beispiel.

<details>
<summary>💡 Lösung</summary>

**Antwort:** **S**poofing — Agent gibt sich als anderer Agent aus; **T**ampering — Nachricht wird unterwegs geändert; **R**epudiation — Agent leugnet, eine Nachricht gesendet zu haben; **I**nformation Disclosure — Vertrauliche Daten durch Kommunikation enthüllt; **D**enial of Service — Kommunikationskanal wird blockiert; **E**levation of Privilege — Agent erhält unbefugt mehr Rechte (z.B. indem er sich eine höhere Rolle beimisst).
</details>

### Frage 3: Trust-Zonen
> Was ist eine Trust-Zone und warum sind sie nützlich?

<details>
<summary>💡 Lösung</summary>

**Antwort:** Eine Trust-Zone ist ein Bereich im System, in dem alle Komponenten das gleiche Security-Level teilen. Innerhalb einer Zone gelten bestimmte Annahmen über Integrität und Authentizität — Kommunikation zwischen Agenten derselben Zone ist einfacher, da sie sich gegenseitig vertrauen. Zwischen verschiedenen Zonen (z.B. intern vs. extern) müssen zusätzliche Security-Mechanismen greifen. Trust-Zonen helfen, das System zu segmentieren und Security-Ressourcen gezielt einzusetzen.
</details>

*Lektion 4.1 — Ende*
---

## 🎯 Selbsttest — Modul 4.1

**Prüfe dein Verständnis!**

### Frage 1: Was ist das Hauptproblem bei Agent-to-Agent Kommunikation?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Agents müssen sich gegenseitig vertrauen, aber ein kompromittierter Agent kann schädliche Nachrichten senden. Es gibt keine native Authentifizierung oder Integritätsprüfung zwischen Agents.
</details>

### Frage 2: Was ist Message Spoofing in diesem Kontext?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Ein Angreifer gibt sich als vertrauenswürdiger Agent aus und sendet manipulierte Nachrichten. Ohne Signaturen kann der Empfänger nicht prüfen ob die Nachricht echt ist.
</details>

