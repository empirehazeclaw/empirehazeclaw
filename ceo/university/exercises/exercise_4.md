# Übung 4: Multi-Agent Security — RBAC und Sichere Kommunikation

**Modul:** 4 — Secure Multi-Agent Kommunikation  
**Dauer:** 90 Minuten  
**Punkte:** 100  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## Teil A — RBAC-Design (30 Punkte)

**Szenario:**  

Du entwirfst ein Multi-Agent-System für eine Finanzanalyse-Plattform mit folgenden Agenten:

- **PortfolioManager:** Verwaltet Anlageportfolios, trifft Trading-Entscheidungen
- **MarketDataCollector:** Sammelt Marktdaten von externen APIs
- **RiskAnalyzer:** Analysiert Risiken von Trades
- **ComplianceChecker:** Prüft regulatorische Compliance
- **ReportingAgent:** Erstellt Berichte für Kunden
- **AdminAgent:** Verwaltet das System

**Aufgaben (30 Punkte):**

1. **Rollen-Design (10 Punkte)**  
   Definiere mindestens 6 Rollen mit sinnvollen Permission-Sets. Ordne jeden Agenten einer Rolle zu.

2. **RBAC-Implementation (15 Punkte)**  
   Implementiere das RBAC-System in Python mit:
   - Role-Klassen mit Permissions
   - Agent-Role-Assignments
   - Eine `authorize()` Funktion
   - Resource-spezifische Checks (z.B. Pfad-basiert)

3. **Test-Szenarien (5 Punkte)**  
   Teste mindestens 8 Szenarien und dokumentiere die Ergebnisse.

---

## Teil B — Threat Modeling (25 Punkte)

**Aufgabe (25 Punkte):**

Erstelle ein vollständiges Threat Model für das folgende Multi-Agent-System:

```
┌──────────────────────────────────────────────────┐
│                  External User                    │
└───────────────────────┬──────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│                  API Gateway                      │
│           (Authentication + Rate Limit)          │
└───────────────────────┬──────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│                  Orchestrator                     │
│           (Task Distribution + Routing)           │
└───────┬─────────────────┬─────────────────┬────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Search    │  │   Writer    │  │   Analyzer  │
│   Agent     │  │   Agent     │  │   Agent     │
└─────────────┘  └──────┬──────┘  └─────────────┘
                        │
                        ▼
               ┌─────────────┐
               │  Database   │
               │  (Shared)   │
               └─────────────┘
```

**Anforderungen:**
1. Erstelle ein Data Flow Diagram (DFD) mit Trust-Zonen
2. Wende STRIDE auf jede Verbindung an
3. Identifiziere mindestens 10 Threats
4. Für jeden Threat: Risiko bewerten (Schwere × Wahrscheinlichkeit)
5. Für die 5 kritischsten Threats: Mitigation vorschlagen

---

## Teil C — Sichere Kommunikation (25 Punkte)

**Aufgabe (25 Punkte):**

Implementiere ein sicheres Nachrichten-System mit folgenden Features:

1. **Message Signing (8 Punkte)**  
   ```python
   def sign_message(message: dict, secret: bytes) -> str
   def verify_signature(message: dict, signature: str, secret: bytes) -> bool
   ```

2. **Replay Protection (8 Punkte)**  
   - Implementiere einen Message-ID Cache
   - Cache sollte nur die letzten 1000 IDs behalten
   - Nachrichten mit bereits verwendeten IDs werden abgelehnt

3. **Message Expiration (9 Punkte)**  
   - Füge Timestamps zu Nachrichten hinzu
   - Nachrichten älter als 5 Minuten werden abgelehnt
   - Integriere alles in eine `create_secure_message()` und `validate_secure_message()` Funktion

---

## Teil D — Security Incident Analysis (20 Punkte)

**Szenario:**  

Ein Einbruch in einem Multi-Agent-System wurde entdeckt. Der Angreifer hat es geschafft:
- Vom Search Agent aus den Database Agent zu kontaktieren
- Vertrauliche Kundendaten abzurufen
- Die Daten an einen externen Server zu senden

**Logs (rekonstruiert):**

```
14:02:15 SearchAgent -> Orchestrator: Task "fetch_market_data"
14:02:16 Orchestrator -> SearchAgent: ACK
14:03:01 SearchAgent -> DatabaseAgent: "SELECT * FROM customers WHERE id=?"
14:03:02 DatabaseAgent: Response [Kundendaten]
14:03:03 SearchAgent: "forward_to_external" [DATEN EXFILTRIERT]
```

**Aufgaben (20 Punkte):**

1. **Root Cause Analysis (8 Punkte)**  
   Identifiziere alle Security-Failures, die diesen Angriff ermöglicht haben.

2. **RBAC Audit (6 Punkte)**  
   Erkläre, welche RBAC-Regeln verletzt oder fehlend waren.

3. **Korrekturmaßnahmen (6 Punkte)**  
   Schlage konkrete Fixes vor, die solchen Angriff in Zukunft verhindern.

---

## Bewertungsschema

| Teil | Punkte | Bestehensgrenze |
|------|--------|-----------------|
| A (RBAC-Design) | 30 | 18 |
| B (Threat Modeling) | 25 | 15 |
| C (Kommunikation) | 25 | 15 |
| D (Incident Analysis) | 20 | 12 |
| **Total** | **100** | **60** |

---

## Bonus Challenge (15 Punkte)

Implementiere eine vollständige `SecureAgentChannel` Klasse, die:

1. Messages mit HMAC signiert
2. Messages mit AES verschlüsselt
3. Replay-Schutz hat
4. RBAC-Enforcement hat
5. Alle Operationen logged

---

*Ende der Übung 4*
