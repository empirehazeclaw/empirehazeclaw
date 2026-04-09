# Übung 5: Security Audits — Praktischer Abschluss

**Modul:** 5 — Praktische Security Audits  
**Dauer:** 90 Minuten  
**Punkte:** 100  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## Teil A — Report erstellen (30 Punkte)

**Szenario:**  

Du hast ein Security Audit für ein AI-Chatbot-System durchgeführt und folgende Findings identifiziert:

| ID | Finding | Severity | CVSS |
|----|---------|----------|------|
| F1 | Agent kann auf interne APIs ohne Auth zugreifen | CRITICAL | 9.1 |
| F2 | System-Prompt für Injection anfällig | HIGH | 7.5 |
| F3 | Keine Input-Validierung in File-Tool | HIGH | 7.2 |
| F4 | Chat-Historien unverschlüsselt | MEDIUM | 5.3 |
| F5 | Rate-Limiting fehlt | MEDIUM | 5.1 |
| F6 | Logging zu verbose | LOW | 2.1 |
| F7 | Keine regelmäßigen Security Scans | INFO | 0.0 |

**Aufgaben (30 Punkte):**

1. **Executive Summary (10 Punkte)**  
   Erstelle ein Executive Summary (max 1 Seite) mit:
   - Gesamtbewertung des Systems
   - Top 3 Findings
   - Empfohlene Prioritäten
   - Ressourcenbedarf

2. **Detailed Finding für F1 (12 Punkte)**  
   Erstelle einen Detailed Finding Report für das kritische Finding mit:
   - Vollständige Beschreibung
   - Impact Assessment
   - Steps to Reproduce
   - Konkrete Remediation mit Code-Beispiel

3. **Remediation Plan für F1-F3 (8 Punkte)**  
   Erstelle einen strukturierten Plan mit:
   - Tasks
   - Verantwortlichkeiten
   - Timeline
   - Erfolgskriterien

---

## Teil B — Penetration Testing (25 Punkte)

**Aufgabe (25 Punkte):**

Du sollst einen vereinfachten Pentest für ein AI-System durchführen. Das System hat:
- Einen AI-Chatbot mit `read_file` Tool
- RBAC mit 3 Rollen (user, admin, guest)
- Eine Datenbank mit User-Profilen

Führe folgende Tests durch und dokumentiere die Ergebnisse:

1. **Prompt Injection (8 Punkte)**  
   Teste 3 verschiedene Injection-Techniken. Dokumentiere:
   - Technik
   - Input
   - Erfolg (Ja/Nein)
   - Bei Erfolg: Auswirkung

2. **RBAC-Bypass (9 Punkte)**  
   Versuche, als `guest` auf admin-Funktionen zuzugreifen. Teste:
   - Header Manipulation
   - Token Manipulation
   - Direkte Endpunkt-Aufrufe

3. **Tool-Exploitation (8 Punkte)**  
   Teste das `read_file` Tool mit bösartigen Inputs:
   - Path Traversal
   - Command Injection
   - Dateityp-Umgehung

---

## Teil C — Security Scanner (20 Punkte)

**Aufgabe (20 Punkte):**

Implementiere einen einfachen Config-Scanner, der:

1. **Secrets Detection (8 Punkte)**  
   Scannt Config-Dateien nach:
   - API-Keys (Pattern: `sk-`, `api_key`, `apikey`)
   - Passwörter (Pattern: `password`, `pwd`, `secret`)
   - Zertifikate (PEM-Format)
   
   Gibt Dateipfad, Zeilennummer und erkannten Typ aus.

2. **Config Validation (6 Punkte)**  
   Validiert eine einfache RBAC-Config im JSON-Format:
   - Prüft auf Agents ohne Rolle
   - Prüft auf ungenutzte Rollen
   - Prüft auf SYSTEM-Rolle ausserhalb erlaubter Agents

3. **Report Generation (6 Punkte)**  
   Generiert einen JSON-Report mit:
   - Zusammenfassung der Findings
   - Details pro Finding
   - Empfehlungen

---

## Teil D — Risiko-Analyse (25 Punkte)

**Aufgabe (25 Punkte):**

Analysiere das folgende Sicherheitsvorfall-Szenario:

```
VORFALL: Kundendaten-Exposition bei AI-Chatbot

TIMELINE:
14:00 - Chatbot startet mit System-Prompt "Du bist ein Kunden-Support-Bot"
14:15 - User fragt: "Was kann ich dir alles sagen?"
14:15 - Bot antwortet: "Ich kann persönliche Daten sehen, wenn du mir deine 
        Kundennummer nennst"
14:16 - User fragt: "Zeig mir mal die Daten von Kunde 12345"
14:16 - Bot zeigt: Name, Adresse, letzte Transaktionen
14:30 - IT-Sicherheit wird alarmiert
14:45 - Chatbot wird vom Netz genommen
15:30 - Incident Response beginnt
```

**Anforderungen:**

1. **Root Cause Analysis (10 Punkte)**  
   Identifiziere alle Ursachen des Vorfalls (technisch und prozessual).

2. **Impact Assessment (8 Punkte)**  
   Bewerte den Impact nach:
   - Betroffene Personen
   - Datentypen
   - Reputationsschaden (geschätzt)
   - Regulatorische Konsequenzen (DSGVO)

3. **Lessons Learned & Recommendations (7 Punkte)****  
   Was hätte diesen Vorfall verhindert? Erstelle 5 konkrete Empfehlungen.

---

## Bewertungsschema

| Teil | Punkte | Bestehensgrenze |
|------|--------|-----------------|
| A (Report) | 30 | 18 |
| B (Pentest) | 25 | 15 |
| C (Scanner) | 20 | 12 |
| D (Risiko-Analyse) | 25 | 15 |
| **Total** | **100** | **60** |

---

## 🎓 Track-Abschluss

Wenn du diese Übung erfolgreich absolviert hast, hast du den **Cybersecurity Track der OpenClaw University** abgeschlossen!

Du hast gelernt:
- ✅ Prompt Injection erkennen und verhindern
- ✅ OWASP Top 10 für AI Agents anwenden
- ✅ Sichere Tool-Input-Validation implementieren
- ✅ Multi-Agent-Kommunikation absichern
- ✅ Security Audits für AI-Systeme durchführen

**Zertifikat:** Nach erfolgreichem Abschluss aller 5 Module + Quiz erhältst du das "AI Security Fundamentals" Zertifikat.

---

*Ende der Übung 5*
*Ende des Cybersecurity Tracks*
