# Übung 3: Tool-Input-Validation — Praktische Implementierung

**Modul:** 3 — Tool-Input-Validation meistern  
**Dauer:** 75 Minuten  
**Punkte:** 90 (plus 10 Bonus)  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## Teil A — Spec-Design Challenge (25 Punkte)

**Aufgabe (25 Punkte):**  

Entwirf eine sichere Tool-Spec für ein "Database-Query-Tool" mit folgenden Anforderungen:

1. Das Tool darf nur SELECT-Statements ausführen (ke INSERT, UPDATE, DELETE, DROP)
2. Es darf nur auf vorher definierte Tabellen zugreifen
3. Query-Parameter müssen parametrisiert sein (kein String-Concatenation)
4. Maximal 1000 Results zurückgeben
5. Timeout von 30 Sekunden

Implementiere die Spec mit Pydantic. Definiere ein JSON-Schema für die Tool-Spec.

**Bonus (10 Punkte):** Erweitere die Spec um ein RBAC-System, das verschiedene User-Roles mit unterschiedlichen Berechtigungsstufen unterstützt.

---

## Teil B — Sanitisierungspipeline (25 Punkte)

**Aufgabe (25 Punkte):**

Implementiere eine Sanitisierungspipeline für User-Inputs, die in einem AI-Chatbot verwendet werden. Die Pipeline muss:

1. Control Characters entfernen (0x00-0x1F, 0x7F-0x9F)
2. Unicode normalisieren (NFKC)
3. HTML-Tags entfernen
4. Path-Traversal-Patterns erkennen und blockieren
5. Maximallänge: 5000 Zeichen

Schreibe außerdem einen Fuzzer, der die Pipeline mit mindestens 20 verschiedenen Angriffs-Inputs testet.

---

## Teil C — Tool-Fencing (20 Punkte)

**Code Review (20 Punkte):**

Du hast folgendes Tool:

```python
import subprocess

def run_shell_command(command: str, timeout: int = 60):
    """
    Führt einen Shell-Befehl aus.
    """
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        timeout=timeout
    )
    return {
        "stdout": result.stdout.decode(),
        "stderr": result.stderr.decode(),
        "returncode": result.returncode
    }
```

**Aufgaben:**

1. **Identifiziere alle Security-Probleme** (10 Punkte)  
   Für jedes Problem: Art des Angriffs, Schwere (1-5), möglicher Schaden

2. **Implementiere eine sichere Version** (10 Punkte)  
   Das sichere Tool muss:
   - Command Injection verhindern
   - Ressourcen-Limits haben
   - Nur erlaubte Befehle erlauben
   - Logging haben

---

## Teil D — Security Audit (20 Punkte)

**Szenario:**

Ein AI-Agent-System hat folgendes Tool:

```python
class EmailTool:
    def send_email(self, to: str, subject: str, body: str, cc: str = None):
        # Sendet Email via公司的 SMTP-Server
        pass
```

Das Tool wird von einem AI-Agenten aufgerufen, der Kundenanfragen bearbeitet.

**Aufgaben:**

1. **Threat Modeling (8 Punkte)**  
   Erstelle ein einfaches Threat Model mit: Trust Boundaries, Assets, und mindestens 5 Threats

2. **Security Requirements (6 Punkte)**  
   Definiere konkrete Security-Requirements für das Tool

3. **Empfehlungen (6 Punkte)**  
   Gib konkrete Verbesserungsvorschläge mit Priorisierung

---

## Bewertungsschema

| Teil | Punkte | Bestehensgrenze |
|------|--------|-----------------|
| A (Spec-Design) | 25 | 15 |
| B (Sanitisierung) | 25 | 15 |
| C (Fencing) | 20 | 12 |
| D (Audit) | 20 | 12 |
| **Total** | **90** | **54** |
| Bonus | +10 | — |

---

## Bonus Challenge (10 Punkte)

Implementiere ein "Tool Registry" System, das:

1. Alle verfügbaren Tools registriert mit Specs
2. Automatisch RBAC durchsetzt
3. Tool-Aufrufe logged
4. Rate-Limiting pro User und Tool implementiert

---

*Ende der Übung 3*
