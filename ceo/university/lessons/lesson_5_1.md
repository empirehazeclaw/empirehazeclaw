# Lektion 5.1: Audit-Strategie & Checklisten

**Modul:** 5 — Praktische Security Audits  
**Dauer:** 45 Minuten  
**Schwierigkeit:** ⭐⭐  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## 🎯 Lernziele

Am Ende dieser Lektion kannst du:

- ✅ Eine Audit-Strategie für AI-Agent-Systeme entwickeln
- ✅ Strukturierte Security-Checklisten erstellen
- ✅ Die richtige Audit-Methodik auswählen
- ✅ Ergebnisse dokumentieren und priorisieren

---

## 📖 Inhalt

### 1. Warum Security Audits für AI-Systeme

Security Audits sind systematische Überprüfungen der Sicherheitslage eines Systems. Für traditionelle Software gibt es etablierte Methoden — aber AI-Systeme werfen neue Fragen auf:

- Wie prüfst du die Sicherheit eines ML-Modells?
- Wie gehst du mit Prompt-Injection um?
- Wie validierst du die Security von Agenten-Interaktionen?

Ein AI-Security-Audit ist kein normales AppSec-Audit. Du brauchst ein Verständnis für ML-Sicherheit, Prompt Engineering, und Agent-Architekturen.

### 2. Audit-Typen

#### 2.1 Penetration Testing (Pentest)

Beim Pentest versucht der Tester aktiv, das System zu kompromittieren — wie ein echter Angreifer. Für AI-Systeme bedeutet das:

- Prompt Injection Angriffe durchführen
- Agent-Kommunikation abfangen und manipulieren
- Modell-Verhalten unter Stress testen
- Tool-Nutzung für böswillige Zwecke missbrauchen

```python
# Beispiel: Pentest-Checkliste für AI-Systeme
PENTEST_CHECKLIST = {
    "prompt_injection": [
        "Direkte Prompt Injection via User-Input",
        "Indirekte Prompt Injection via Tool-Outputs",
        "Context Overflow Angriffe",
        "Cascade Attacks",
    ],
    "agent_communication": [
        "Man-in-the-Middle auf Kommunikationskanälen",
        "Session Hijacking",
        "Message Replay",
        "Unauthorized Agent-Impersonation",
    ],
    "tool_usage": [
        "Tool-Fencing Umgehung",
        "Resource Exhaustion via Tools",
        "Path Traversal durch File-Tools",
        "Command Injection via Shell-Tools",
    ],
    "model_security": [
        "Model Extraction / Theft",
        "Membership Inference Attacks",
        "Adversarial Inputs",
        "Backdoor Detection",
    ]
}
```

#### 2.2 Code Review

Systematisches Durchgehen des Codes auf Security-Probleme. Für AI-Systeme besonders wichtig:

- Input-Validation in Tools
- RBAC-Implementierung
- Nachrichten-Validierung
- Secrets-Management

#### 2.3 Configuration Audit

Prüfung der Systemkonfiguration:

- API-Keys sicher gespeichert?
- Rate-Limits konfiguriert?
- Logging angemessen?
- Netzwerk-Zugänge kontrolliert?

#### 2.4 Compliance Audit

Prüfung gegen regulatorische Anforderungen:

- DSGVO (personenbezogene Daten)
- Branchen-spezifische Regulations (Finanzen, Healthcare)
-企业内部 Policies

### 3. Die Audit-Checkliste

#### 3.1 Vorbereitung

```markdown
## Phase 1: Vorbereitung

### Scope Definition
- [ ] Systemgrenzen definiert
- [ ] In-Scope / Out-of-Scope Komponenten dokumentiert
- [ ]Timeline festgelegt
- [ ] Ressourcen zugewiesen

### Information Gathering
- [ ] Architektur-Dokumentation gesammelt
- [ ] Codebase inventarisiert
- [ ] Konfigurationsdaten gesammelt
- [ ] Vorherige Audits überprüft

### Tool-Setup
- [ ] Pentest-Tools vorbereitet
- [ ] Test-Accounts eingerichtet
- [ ] Monitoring/Logging aktiviert
- [ ] Isolierte Testumgebung vorbereitet
```

#### 3.2 AI-Spezifische Checks

```markdown
## Phase 2: AI-Security Checks

### Model Security
- [ ] Modell auf bekannte Angriffe getestet
- [ ] Adversarial Examples geprüft
- [ ] Model Interpretability dokumentiert
- [ ] Training Data Provenance verifiziert

### Prompt Security
- [ ] Direkte Prompt Injection getestet
- [ ] Indirekte Prompt Injection getestet
- [ ] System-Prompt Isolation geprüft
- [ ] Output-Handling validiert

### Agent Security
- [ ] RBAC-Implementierung geprüft
- [ ] Kommunikationskanäle gesichert
- [ ] Trust-Zonen definiert
- [ ] Least-Privilege durchgesetzt

### Tool Security
- [ ] Input-Validation in allen Tools
- [ ] Tool-Fencing implementiert
- [ ] Resource-Limits gesetzt
- [ ] Logging/Monitoring aktiv
```

#### 3.3 Nachbereitung

```markdown
## Phase 3: Nachbereitung

### Dokumentation
- [ ] Findings detailliert dokumentiert
- [ ] Risiko-Bewertungen zugeordnet
- [ ] Screenshots/Exploits archiviert
- [ ] Report erstellt

### Priorisierung
- [ ] Kritische Issues sofort eskaliert
- [ ] Hohe Issues für Sprint geplant
- [ ] Mittlere Issues im Backlog
- [ ] Geringe Issues als Tech-Debt

### Follow-Up
- [ ] Remediation vereinbart
- [ ] Retest-Termine geplant
- [ ] Lessons Learned dokumentiert
```

### 4. Risiko-Bewertung

```python
from dataclasses import dataclass
from typing import List
from enum import Enum

class Severity(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5

class Finding:
    """Ein Security-Finding aus einem Audit."""
    
    def __init__(
        self,
        title: str,
        description: str,
        severity: Severity,
        affected_component: str,
        evidence: List[str],
        recommendation: str
    ):
        self.title = title
        self.description = description
        self.severity = severity
        self.affected_component = affected_component
        self.evidence = evidence
        self.recommendation = recommendation
        self.fixed = False
        self.fix_date = None
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "severity": self.severity.name,
            "component": self.affected_component,
            "description": self.description,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "fixed": self.fixed,
            "fix_date": self.fix_date
        }


class AuditReport:
    """Ein vollständiger Audit-Report."""
    
    def __init__(self, system_name: str, auditor: str):
        self.system_name = system_name
        self.auditor = auditor
        self.findings: List[Finding] = []
        self.start_date = None
        self.end_date = None
    
    def add_finding(self, finding: Finding):
        self.findings.append(finding)
    
    def get_summary(self) -> dict:
        """Gibt eine Zusammenfassung der Findings zurück."""
        by_severity = {}
        for f in self.findings:
            sev = f.severity.name
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            "total_findings": len(self.findings),
            "by_severity": by_severity,
            "critical_count": by_severity.get("CRITICAL", 0),
            "unfixed_count": len([f for f in self.findings if not f.fixed])
        }
    
    def to_dict(self) -> dict:
        return {
            "system": self.system_name,
            "auditor": self.auditor,
            "date": {
                "start": self.start_date,
                "end": self.end_date
            },
            "summary": self.get_summary(),
            "findings": [f.to_dict() for f in self.findings]
        }
```

---

## 🧪 Praktische Übungen

### Übung 1: Audit-Plan erstellen

Du sollst ein Security-Audit für ein AI-Chatbot-System planen. Das System:
- Nutzt GPT-4 für Konversationen
- Hat einen AI-Agenten der APIs aufrufen kann
- Speichert Chat-Historie in einer Datenbank
- Bietet eine REST-API für Dritte

**Aufgaben:**
1. Erstelle einen Audit-Plan mit allen Phasen
2. Definiere den Scope (In-Scope / Out-of-Scope)
3. Erstelle eine spezifische Checkliste für dieses System
4. Plane die Ressourcen und Timeline

### Übung 2: Finding-Klassifizierung

Die folgenden Findings wurden in einem Audit identifiziert. Klassifiziere jedes nach Severity und Priorität:

1. "Der AI-Agent kann auf alle Dateien im Dateisystem zugreifen"
2. "Chat-Historien werden im Klartext in der Datenbank gespeichert"
3. "Der System-Prompt enthält API-Endpoint-URLs"
4. "Es gibt kein Rate-Limiting auf der API"
5. "Der AI-Agent antwortet manchmal mit 'Ich kann das nicht tun' bei harmlosen Anfragen"

---

## 📚 Zusammenfassung

Security Audits sind essentiell für AI-Agent-Systeme. Die Besonderheiten gegenüber traditionellen AppSec-Audits:

- AI-spezifische Angriffsvektoren (Prompt Injection, Model Security)
- Agent-Interaktionen als zusätzliche Angriffsfläche
- Die probabilistische Natur von ML-Modellen macht Reproduktion schwieriger

Ein guter Audit braucht:
- Klare Scope-Definition
- Systematische Checklisten
- Konsistente Risiko-Bewertung
- Actionable Findings

Im nächsten Kapitel werden wir Penetration Testing für AI Agents im Detail betrachten.

---

## 🔗 Weiterführende Links

- OWASP Testing Guide
- NIST Cybersecurity Framework
- AI Incident Database

---

## ❓ Fragen zur Selbstüberprüfung

1. Nenne drei Unterschiede zwischen einem traditionellen AppSec-Audit und einem AI-Security-Audit.
2. Was sind die vier Hauptphasen eines Security Audits?
3. Wie priorisierst du Findings nach einem Audit?

---

---

## 🎯 Selbsttest — Modul 5.1

**Prüfe dein Verständnis!**

### Frage 1: AI-Security vs. AppSec-Audit
> Nenne drei Unterschiede zwischen einem traditionellen AppSec-Audit und einem AI-Security-Audit.

<details>
<summary>💡 Lösung</summary>

**Antwort:** **1)** AI-Systeme haben zusätzliche Angriffsvektoren wie Prompt Injection, Model Security und RAG Poisoning, die traditionelle Audits nicht abdecken; **2)** Die probabilistische Natur von ML-Modellen macht Reproduktion von Angriffen schwieriger — ein Angriff funktioniert manchmal, manchmal nicht; **3)** Agent-Interaktionen (Kommunikation zwischen Agents) sind eine zusätzliche Angriffsfläche; **4)** Traditionelle Audits konzentrieren sich auf statischen Code und bekannte Schwachstellen, AI-Security braucht Verständnis für ML-Dynamik und Prompt Engineering.
</details>

### Frage 2: Die vier Hauptphasen
> Was sind die vier Hauptphasen eines Security Audits?

<details>
<summary>💡 Lösung</summary>

**Antwort:** **Phase 1: Vorbereitung** — Scope definieren, Information Gathering, Tool-Setup; **Phase 2: Durchführung** — Eigentliche Security-Checks (Pentests, Code Review, Config Audit); **Phase 3: Dokumentation** — Findings detailliert dokumentieren, Risiko-Bewertungen, Screenshots; **Phase 4: Nachbereitung** — Priorisierung (Critical sofort, High im Sprint), Remediation vereinbaren, Retest-Termine planen.
</details>

### Frage 3: Finding-Priorisierung
> Wie priorisierst du Findings nach einem Audit?

<details>
<summary>💡 Lösung</summary>

**Antwort:** Priorisierung nach **Severity** (CRITICAL > HIGH > MEDIUM > LOW > INFO) UND **Business Impact**: Kritische Findings, die aktiv ausgenutzt werden können (z.B. Remote Code Execution), werden SOFORT eskaliert. Hohe Findings kommen in den nächsten Sprint. Mittlere ins Backlog mit Deadline. Niedrige als Tech-Debt tracken. Zusätzlich Faktoren: Wie groß ist die Angriffsfläche? Wie schwer ist die Ausnutzung? Was ist der potenzielle Schaden?
</details>

*Lektion 5.1 — Ende*
---

## 🎯 Selbsttest — Modul 5.1

**Prüfe dein Verständnis!**

### Frage 1: Was sind die 4 Phasen eines Security Audits?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) Scoping & Planning, 2) Reconnaissance (Information Gathering), 3) Vulnerability Assessment, 4) Reporting & Remediation
</details>

### Frage 2: Was ist der Unterschied zwischen einem Audit und einem Penetration Test?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Ein Audit prüft ob Sicherheitsstandards eingehalten werden (compliance-orientiert). Ein Pentest simuliert echte Angriffe um zu sehen ob die Verteidigung durchbrochen werden kann.
</details>

