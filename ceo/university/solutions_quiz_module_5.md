# Modul 5 — Lösungsschlüssel: Praktische Security Audits

**Kurs:** OpenClaw University  
**Modul:** 5 — Security Audits  
**Erstellt:** 2026-04-08

---

# TEIL A — Multiple Choice (40 Punkte)

---

## Frage 1 — Lösung

**Richtige Antwort: b**

**Erklärung:** AI-Security Audits erfordern Verständnis für ML-Spezifische Sicherheitsrisiken (Prompt Injection, Model Security), Prompt Engineering, und Agent-Architekturen. Traditionelle AppSec-Tools und -Methoden reichen nicht aus.

---

## Frage 2 — Lösung

**Richtige Antwort: b**

**Erklärung:** Bei einem Penetration Test versucht der Tester aktiv, das System zu kompromittieren — genau wie ein echter Angreifer. Das Ziel ist, Schwachstellen zu finden, bevor echte Angreifer sie ausnutzen.

---

## Frage 3 — Lösung

**Richtige Antwort: b**

**Erklärung:** Die vier Hauptphasen sind: Vorbereitung, Durchführung, Analyse, Reporting. Die anderen Optionen sind Phasen aus dem Software Development Lifecycle.

---

## Frage 4 — Lösung

**Richtige Antwort: b**

**Erklärung:** Prompt Injection Testing bei AI-Pentests umfasst: Direkte Prompt Injection, Indirekte Injection, Context Overflow, Cascade Attacks. SQL-Injection ist traditionelle AppSec.

---

## Frage 5 — Lösung

**Richtige Antwort: b**

**Erklärung:** Ein Prompt Injection Scanner automatisiert die Erkennung von Prompt-Injection-Angriffsvektoren — also AI-spezifischen Schwachstellen, nicht Netzwerk-Schwachstellen.

---

## Frage 6 — Lösung

**Richtige Antwort: b**

**Erklärung:** Das Management muss die wichtigsten Risiken auf einen Blick sehen können, um Ressourcen zu priorisieren und Entscheidungen zu treffen. Details sind für technische Teams, nicht für Execs.

---

## Frage 7 — Lösung

**Richtige Antwort: b**

**Erklärung:** CVSS (Common Vulnerability Scoring System) ist ein standardisiertes Framework zur Bewertung des Schweregrads von Sicherheitslücken — auf einer Skala von 0.0 bis 10.0.

---

## Frage 8 — Lösung

**Richtige Antwort: b**

**Erklärung:** Compliance Audit prüft gegen regulatorische Anforderungen wie DSGVO (Datenschutz), branchenspezifische Regulations (Finanzen, Healthcare), oder interne Policies.

---

## Frage 9 — Lösung

**Richtige Antwort: b**

**Erklärung:** Continuous Security Monitoring bedeutet kontinuierliche automatisierte Prüfungen auf Sicherheitsprobleme — nicht nur einmalige Audits, sondern dauerhaftes Monitoring.

---

## Frage 10 — Lösung

**Richtige Antwort: a**

**Erklärung:** Remediation ist die systematische Behebung identifizierter Sicherheitslücken — von der Planung über Implementierung bis zum Retest.

---

# TEIL B — True/False (15 Punkte)

---

## Frage 11 — Lösung

**Richtige Antwort: Falsch**

**Erklärung:** Manuelle Pentests reichen NICHT allein aus für AI-Sicherheit. AI-Systeme brauchen sowohl automatisierte Scanner (für kontinuierliche Prüfung) als auch manuelle Pentests (für komplexe Angriffsszenarien). Beides zusammen bietet den besten Schutz.

---

## Frage 12 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** CRITICAL-Findings sollten sofort eskaliert werden — sie representieren akute Gefahr. LOW-Severity Findings können als Tech-Debt dokumentiert und später adressiert werden.

---

## Frage 13 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** RBAC-Scanner können automatisch Agents mit SYSTEM-Rolle finden und warnen, wenn diese Rolle nicht für die erwarteten Agenten (CEO, Security Officer) reserviert ist.

---

## Frage 14 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** Dokumentation von Exploits ist essentiell für: Reproduzierbarkeit, Verständnis der Angriffstechnik, Entwicklung von Gegenmaßnahmen, und Training des Security-Teams.

---

## Frage 15 — Lösung

**Richtige Antwort: Falsch**

**Erklärung:** Geplante Scans UND event-basierte Scans haben各有 Vorteile:
- **Geplant:** Regelmäßige Coverage, vergleichbare Ergebnisse
- **Event-basiert:** Schnellere Reaktion auf neue Bedrohungen
Beide zusammen sind am besten — nicht eines statt des anderen.

---

# TEIL C — Fallanalyse (25 Punkte)

---

## Frage 16 — Lösung

**Antwort:**

### Teilaufgabe a: Priorisierung

| # | Finding | Severity | Priorität | Begründung |
|---|---------|----------|-----------|------------|
| 1 | Dateizugriff außerhalb erlaubtem Verzeichnis | CRITICAL | **1** | Kompromittierter Agent kann jede Datei lesen/ändern/löschen |
| 2 | Chat-Historien im Klartext | HIGH | **2** | Personenbezogene Daten (DSGVO), Reputationsschaden |
| 3 | System-Prompt mit API-URLs | MEDIUM | **3** | Info Disclosure, kann für weitere Angriffe genutzt werden |
| 4 | Kein Rate-Limiting | MEDIUM | **4** | DoS möglich, aber weniger kritisch |
| 5 | False Negatives bei harmlosen Requests | LOW | **5** | User Experience Problem, kein Security-Risk direkt |

**Reihenfolge:** 1 → 2 → 3 → 4 → 5

---

### Teilaufgabe b: Impact und Remediation für Finding #1

**Impact:**
- Angreifer kann vertrauliche Daten (Secrets, Keys, persönliche Dateien) lesen
- Manipulation von Systemdateien möglich
- Persistenz aufbauen durch Hinzufügen von Backdoors
- Laterale Bewegung im System

**Remediation-Schritte:**

1. **Sofort-Maßnahme:** RBAC-Audit durchführen, alle Agents auf Least-Privilege prüfen
2. **Kurzfristig:** Tool-Fencing implementieren:
   ```python
   class SecureFileTool:
       BASE_DIR = "/data/allowed"
       ALLOWED_EXTENSIONS = {".txt", ".md", ".json"}
       
       def validate_path(self, path):
           # 1. Path Traversal Check
           # 2. Normalisieren und verify BASE_DIR
           # 3. Extension prüfen
           pass
   ```
3. **Mittelfristig:** Automatisierter RBAC-Scanner, der regelmäßig Permissions prüft

---

### Teilaufgabe c: Finding #3 — Warum Security-Risiko und Lösung

**Warum Security-Risiko:**
- API-Endpoint-URLs im System-Prompt verraten interne Struktur
- Angreifer kann API-Endpoints direkt anprechen
- Kann für Reconnaissance und weitere Angriffe genutzt werden
- URLs können API-Keys oder Tokens enthalten

**Lösung:**
- API-Endpoints niemals in Prompts hardcoden
- Environment-Variablen oder Secrets-Manager nutzen
- System-Prompt regelmäßig auf sensitive Data scannen
- Separation: Prompts enthalten keine internen Details

---

### Teilaufgabe d: Executive Summary-Tabelle

```markdown
## Executive Summary — Key Findings

| # | Finding | Severity | Status |
|---|---------|----------|--------|
| 1 | AI-Agent kann auf alle Dateien zugreifen | CRITICAL | Open |
| 2 | Chat-Historien im Klartext gespeichert | HIGH | Open |
| 3 | System-Prompt enthält API-URLs | MEDIUM | Open |

**Empfohlene Prioritäten:**
1. RBAC-Implementierung für alle Agenten (Finding #1)
2. Datenbank-Verschlüsselung aktivieren (Finding #2)
3. Secrets aus Prompts entfernen (Finding #3)
```

---

# TEIL D — Praxisfragen (20 Punkte)

---

## Frage 17 — Lösung

**Antwort:**

### Teilaufgabe a: Scope-Definition

**In-Scope:**
- AI-Chatbot (GPT-4 Integration)
- AI-Agent (API-Calling-Funktionalität)
- Chat-Historie Datenbank
- REST-API für Dritte
- Kommunikation zwischen Komponenten
- Input-Validation aller User-Inputs

**Out-of-Scope:**
- GPT-4 intern (kein Zugriff auf OpenAI-Infrastruktur)
- Client-seitiger Code (Browser des Users)
- Physische Sicherheit des Rechenzentrums
- DDoS-Schutz auf Netzwerkebene (nur Applikations-Layer)

**Limitationen:**
- Kein Red-Team mit echten Angriffen auf Produktivsystem
- Nur dokumentierte Endpoints testbar
- Zeitlimitation: 1 Tag Audit

---

### Teilaufgabe b: Pentest-Checkliste

| Kategorie | Test |
|-----------|------|
| **Prompt Injection** | Direkte Prompt Injection via User-Input |
| | Indirekte Prompt Injection via E-Mail/Tool-Output |
| **Agent Security** | RBAC-Bypass via Header Manipulation |
| | Session Hijacking auf Agent-Kommunikation |
| **Tool Security** | Path Traversal via File-Tool |
| | Command Injection via Shell-Tool |
| **API Security** | Unauthorized API-Access ohne Auth |
| | Rate-Limiting Umgehung |

---

### Teilaufgabe c: Zwei Limitationen

1. **Eingeschränkter Scope:** Keine Tests auf Infrastruktur-Ebene möglich, nur Applikations-Layer
2. **Zeitlimitation:** Ein eintägiges Audit kann nicht alle möglichen Angriffsszenarien durchspielen

---

## Frage 18 — Lösung

**Antwort:**

### Teilaufgabe a: Exploit-Dokument

```markdown
# Exploit Report: RBAC Bypass via Header Manipulation

**Severity:** CRITICAL  
**Component:** Agent Authorization Layer  
**OWASP:** ML05 (Excess Agency)  
**CVSS:** 8.5 (geschätzt)  
**Status:** OPEN  

---

## Description

Ein Low-Privilege-Agent konnte Admin-Funktionen ausführen, indem er 
einen manipulierten HTTP-Header `X-User-Role: admin` sendete. 
Die Authorization-Schicht vertraute dem Header ohne Validierung.

---

## Steps to Reproduce

1. Verbinde als Low-Privilege-Agent mit dem System
2. Sende einen API-Request mit manipuliertem Header:
   ```
   GET /api/admin/users
   X-User-Role: admin
   X-User-ID: attacker_agent
   ```
3. System akzeptiert den Header ohne Prüfung
4. Admin-Funktionalität wird ausgeführt

---

## Impact Assessment

- **Confidentiality:** MEDIUM — Admin-Zugriff auf alle Daten
- **Integrity:** HIGH — Daten können manipuliert werden
- **Availability:** LOW — Kein DoS möglich über diesen Vector

**Gesamtrisiko:** CRITICAL — Vollständige Systemübernahme möglich

---

## Remediation Recommendations

1. **NIEMALS** Trust Headers for Authorization
2. Authorization muss serverseitig über Session/Token erfolgen
3. RBAC-Policy Engine muss originale Agent-Identity prüfen
4. Alle Requests müssen authentifiziert und autorisiert sein

---

### Teilaufgabe b: Korrektur in Python

```python
class RBACEngine:
    def authorize(self, request: RBACRequest) -> RBACResponse:
        """
        Sichere Autorisierung — KEINE Header-Trust!
        """
        # NIEMALS: request.headers.get("X-User-Role")
        # IMMER: Serverseitige Session/Identity
        
        # 1. Hole Agent-Identity aus AUTHENTIZIERTER Session
        agent_identity = self.get_session_identity(request.session_token)
        if not agent_identity:
            return RBACResponse(
                allowed=False,
                reason="Invalid or missing session token",
                evaluated_at=time.time()
            )
        
        # 2. Hole Rolle(n) aus DATENBANK (nicht aus Header!)
        agent_roles = self.get_roles_from_db(agent_identity)
        
        # 3. Prüfe Permission gegen Datenbank-Rolle
        for role_name in agent_roles:
            role = self.roles.get(role_name)
            if role and permission in role.permissions:
                return RBACResponse(
                    allowed=True,
                    reason=f"Permission granted via role {role_name}",
                    evaluated_at=time.time()
                )
        
        return RBACResponse(
            allowed=False,
            reason=f"No permission {permission.value} for {agent_identity}",
            evaluated_at=time.time()
        )
```

---

**Ende des Lösungsschlüssels**
