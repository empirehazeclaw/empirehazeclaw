# Lektion 3.3: Implementierung — Eigene sichere Tools

**Modul:** 3 — Tool-Input-Validation meistern  
**Dauer:** 60 Minuten  
**Schwierigkeit:** ⭐⭐⭐⭐  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## 🎯 Lernziele

Am Ende dieser Lektion kannst du:

- ✅ Ein sicheres Tool von Grund auf implementieren
- ✅ Die Security-Checkliste für Tool-Development anwenden
- ✅ Penetrationstests für eigene Tools durchführen
- ✅ Dokumentation und Monitoring für Tools implementieren

---

## 📖 Inhalt

### 1. Security-by-Design für Tools

Die sichersten Tools sind nicht those, die nachträglich mit Security-Features aufgerüstet wurden — es sind those, die von Grund auf mit Security im Design entwickelt wurden.

Security-by-Design bedeutet:

**Principle of Least Privilege:** Ein Tool erhält nur die Berechtigungen, die es für seine spezifische Aufgabe braucht — nicht mehr.

**Fail-Secure:** Wenn etwas schief geht, fällt das Tool sicher — nicht offen — und gibt keine partial Outputs oder Fehlerinformationen preis.

**Defense in Depth:** Mehrere Security-Layer, sodass wenn eine Schicht versagt, die nächste greift.

### 2. Tool-Development Workflow

#### Phase 1: Threat Modeling

Bevor du auch nur eine Zeile Code schreibst, modelle die Threats:

```python
# Threat Model Template für Tools

THREAT_MODEL_TEMPLATE = """
TOOL: {tool_name}
VERSION: {version}
DATE: {date}

1. FUNKTIONALE BESCHREIBUNG
   Was macht das Tool?

2. TRUST BOUNDARIES
   - Welche Daten fließen rein?
   - Welche Daten fließen raus?
   - Wo ist die Trust Boundary?

3. ASSETS (Was wird geschützt?)
   - Daten: ...
   - Systeme: ...
   - Reputation: ...

4. THREATS (Was kann schiefgehen?)
   | Threat | Kategorie | Schwere | Wahrsch. | Risk Score |
   |--------|-----------|---------|-----------|------------|
   |        |           |         |           |            |

5. MITIGATIONS (Wie vermeiden wir es?)
   | Threat | Mitigation | Status |
   |--------|------------|--------|
   |        |            |        |

6. SECURITY TESTING PLAN
   - Unit Tests für Validation
   - Fuzzing Strategy
   - Pen-Test Scenarios
"""
```

#### Phase 2: Sichere Implementierung

```python
# Beispiel: Sichere Datei-Tool-Implementierung

import os
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

@dataclass
class FileReadResult:
    """Ergebnis einer sicheren Dateioperation."""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None

class SecureFileReader:
    """
    Sichere Datei-Lese-Tool-Implementierung.
    """
    
    # Konfiguration via Class Variables
    BASE_DIR = "/data/allowed"  # Erlaubtes Basis-Verzeichnis
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {".txt", ".md", ".json", ".csv", ".xml", ".yaml", ".yml"}
    BLOCKED_PATTERNS = [
        r"\.\./",  # Path Traversal
        r"^/",     # Absolute Pfade vermeiden
        r"^~",     # Home-Verzeichnis
        r"[\x00-\x1f]",  # Control Characters
    ]
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialisierung mit optionaler Overwrite der Base-Dir."""
        if base_dir:
            self.BASE_DIR = base_dir
        
        # Explizit verhindern, dass BASE_DIR überschrieben wird
        self._base_dir_locked = True
    
    def validate_path(self, user_path: str) -> tuple[bool, str]:
        """
        Validiert den eingegebenen Pfad gegen alle bekannten Angriffsmuster.
        
        Returns: (is_valid, error_message)
        """
        # 1. Leer-String Check
        if not user_path or not user_path.strip():
            return False, "Path cannot be empty"
        
        # 2. Path Traversal Check
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, user_path):
                return False, f"Path contains blocked pattern: {pattern}"
        
        # 3. Normalisieren und resolven
        try:
            full_path = os.path.normpath(
                os.path.join(self.BASE_DIR, user_path)
            )
        except (ValueError, OSError):
            return False, "Invalid path format"
        
        # 4. Verify within BASE_DIR (nach Normalisierung!)
        real_base = os.path.normpath(self.BASE_DIR)
        if not full_path.startswith(real_base + os.sep) and full_path != real_base:
            return False, "Path escapes allowed directory"
        
        # 5. Extension Check
        ext = os.path.splitext(full_path)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            return False, f"Extension {ext} not allowed. Allowed: {self.ALLOWED_EXTENSIONS}"
        
        # 6. Existence Check
        if not os.path.exists(full_path):
            return False, "File does not exist"
        
        # 7. Type Check (no symlinks, no directories)
        if os.path.isdir(full_path):
            return False, "Path is a directory, not a file"
        
        if os.path.islink(full_path):
            return False, "Symbolic links are not allowed"
        
        return True, ""
    
    def read_file(self, user_provided_path: str, max_lines: int = 1000) -> FileReadResult:
        """
        Liest eine Datei sicher.
        
        Args:
            user_provided_path: Pfad relativ zu BASE_DIR
            max_lines: Maximale Anzahl Zeilen (DoS-Schutz)
        """
        # Phase 1: Validierung
        is_valid, error = self.validate_path(user_provided_path)
        if not is_valid:
            return FileReadResult(
                success=False,
                error=f"Validation failed: {error}"
            )
        
        # Phase 2: Pfad aufösen
        full_path = os.path.normpath(
            os.path.join(self.BASE_DIR, user_provided_path)
        )
        
        # Phase 3: Datei-Stat prüfen (Größe)
        try:
            size = os.path.getsize(full_path)
            if size > self.MAX_FILE_SIZE:
                return FileReadResult(
                    success=False,
                    error=f"File exceeds maximum size: {size} > {self.MAX_FILE_SIZE}"
                )
        except OSError as e:
            return FileReadResult(
                success=False,
                error=f"Cannot access file: {str(e)}"
            )
        
        # Phase 4: Lesen mit Resource Management
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.rstrip("\n"))
                
                return FileReadResult(
                    success=True,
                    content="\n".join(lines),
                    metadata={
                        "lines_read": len(lines),
                        "file_size": size,
                        "path": str(full_path),
                        "truncated": i >= max_lines
                    }
                )
        except UnicodeDecodeError as e:
            return FileReadResult(
                success=False,
                error=f"File encoding not supported: {str(e)}"
            )
        except IOError as e:
            return FileReadResult(
                success=False,
                error=f"IO Error: {str(e)}"
            )
```

#### Phase 3: Security Testing

```python
# Security Tests für das FileReader-Tool

import pytest

class TestSecureFileReader:
    """Security-Tests für den SecureFileReader."""
    
    @pytest.fixture
    def reader(self, tmp_path):
        """Erstellt einen Reader mit temporärem Test-Verzeichnis."""
        # Erstelle Test-Dateien
        test_dir = tmp_path / "data"
        test_dir.mkdir()
        (test_dir / "test.txt").write_text("Hello World")
        (test_dir / "..escape.txt").write_text("Hacked")  # Sollte nicht lesbar sein
        return SecureFileReader(base_dir=str(test_dir))
    
    # --- Path Traversal Tests ---
    
    def test_blocks_simple_traversal(self, reader):
        """Versucht: ../../../etc/passwd"""
        result = reader.read_file("../../../etc/passwd")
        assert not result.success
        assert "Validation failed" in result.error
    
    def test_blocks_encoded_traversal(self, reader):
        """Versucht: ..%2F..%2F..%2Fetc%2Fpasswd"""
        result = reader.read_file("..%2F..%2F..%2Fetc%2Fpasswd")
        assert not result.success
    
    def test_blocks_double_encoded(self, reader):
        """Versucht: ..%252F..%252Fetc"""
        result = reader.read_file("..%252F..%252Fetc")
        assert not result.success
    
    def test_blocks_path_with_null_byte(self, reader):
        """Versucht: test.txt\x00.exe"""
        result = reader.read_file("test.txt\x00.exe")
        assert not result.success
    
    # --- Extension Tests ---
    
    def test_blocks_disallowed_extension(self, reader, tmp_path):
        """Versucht: .exe Datei zu lesen"""
        (tmp_path / "data" / "malware.exe").write_text("virus")
        result = reader.read_file("malware.exe")
        assert not result.success
        assert "not allowed" in result.error
    
    def test_allows_txt_extension(self, reader):
        """txt-Dateien sollten erlaubt sein"""
        result = reader.read_file("test.txt")
        assert result.success
        assert result.content == "Hello World"
    
    # --- Symlink Tests ---
    
    def test_blocks_symlink(self, reader, tmp_path):
        """Symlinks sollten blockiert werden"""
        data_dir = tmp_path / "data"
        secret = data_dir / "secret.txt"
        secret.write_text("SECRET")
        
        link = data_dir / "link.txt"
        link.symlink_to(secret)
        
        result = reader.read_file("link.txt")
        assert not result.success
        assert "symbolic link" in result.error.lower()
    
    # --- Size/DoS Tests ---
    
    def test_blocks_oversized_file(self, reader, tmp_path):
        """Erstellt eine >10MB Datei und versucht sie zu lesen"""
        data_dir = tmp_path / "data"
        big = data_dir / "big.txt"
        big.write_text("x" * (11 * 1024 * 1024))  # 11 MB
        
        result = reader.read_file("big.txt")
        assert not result.success
        assert "exceeds maximum size" in result.error
    
    def test_respects_max_lines(self, reader, tmp_path):
        """Sollte bei max_lines kappen"""
        data_dir = tmp_path / "data"
        lines = ["line" + str(i) for i in range(200)]
        (data_dir / "many.txt").write_text("\n".join(lines))
        
        result = reader.read_file("many.txt", max_lines=50)
        assert result.success
        assert result.metadata["truncated"] == True
        assert result.metadata["lines_read"] == 50
```

### 3. Monitoring und Logging

```python
import structlog
from datetime import datetime
from typing import Optional

logger = structlog.get_logger()

class ToolMonitor:
    """
    Überwacht Tool-Ausführung für Security-Events.
    """
    
    @staticmethod
    def log_invocation(tool_name: str, params: dict, user: str):
        """Logt jeden Tool-Aufruf (nur Metadaten, keine sensitiven Daten)."""
        logger.info(
            "tool_invoked",
            tool=tool_name,
            user=user,
            param_count=len(params),
            timestamp=datetime.utcnow().isoformat()
        )
    
    @staticmethod
    def log_security_event(event_type: str, details: dict):
        """Logt Security-relevante Events mit höherer Dringlichkeit."""
        logger.warning(
            "security_event",
            event_type=event_type,
            details=details,
            timestamp=datetime.utcnow().isoformat()
        )
    
    @staticmethod
    def log_validation_failure(tool_name: str, reason: str, user: str):
        """Logt Validierungsfehler — potenzielle Angriffsversuche."""
        logger.warning(
            "validation_failed",
            tool=tool_name,
            reason=reason,
            user=user,
            timestamp=datetime.utcnow().isoformat()
        )

# Integration im Tool
def monitored_read_file(path: str, user: str) -> FileReadResult:
    """Version mit Monitoring."""
    monitor = ToolMonitor()
    
    # Validation loggen
    monitor.log_invocation("file_reader", {"path": path}, user)
    
    reader = SecureFileReader()
    result = reader.read_file(path)
    
    if not result.success:
        if "Validation failed" in (result.error or ""):
            monitor.log_validation_failure("file_reader", result.error, user)
        else:
            monitor.log_security_event("read_failed", {"error": result.error, "user": user})
    
    return result
```

---

## 🧪 Praktische Übungen

### Übung 1: Eigenes sicheres Tool

Implementiere ein "Texteditor-Tool", das:
- Nur Text-Dateien (.txt, .md, .json) bearbeiten darf
- Dateien nur im erlaubten Verzeichnis bearbeiten darf
- Path Traversal verhindert
- Maximal 1MB pro Datei
- Alle Operationen logged

Teste dein Tool mit mindestens 10 verschiedenen Angriffsversuchen.

### Übung 2: Security Review

Du bekommst folgendes Tool:

```python
def send_email(to: str, subject: str, body: str):
    import smtplib
    server = smtplib.SMTP("smtp.company.com")
    server.sendmail("noreply@company.com", to, f"Subject: {subject}\n\n{body}")
```

Führe eine Security-Review durch:
1. Identifiziere alle Security-Probleme
2. Für jedes Problem: Risiko, Kategorie (OWASP ML), Lösung
3. Implementiere eine sichere Version

### Übung 3: Penetration Testing

Du hast ein AI-Agent-System mit diesen Tools:
- `read_file(path)` — Datei lesen
- `write_file(path, content)` — Datei schreiben
- `execute_code(code)` — Code ausführen

Führe ein Penetration Testing durch:
1. Entwickle 5-7 Angriffsszenarien
2. Für jedes: Was versuchst du, welchen Erfolg erwartest du, wie testest du es
3. Berichte die Ergebnisse und empfohlene Fixes

---

## 📚 Zusammenfassung

Die Implementierung sicherer Tools erfordert einen strukturierten Ansatz: Threat Modeling zuerst, dann sichere Implementierung mit Defense in Depth, dann rigoroses Testing.

Die wichtigsten Principles:
1. **Principle of Least Privilege** — Nur das, was gebraucht wird
2. **Fail-Secure** — Im Zweifel sicher fallen
3. **Defense in Depth** — Mehrere Layer
4. **Monitor Everything** — Logs für Incident Response

Im nächsten Modul werden wir uns mit Secure Multi-Agent Communication beschäftigen.

---

## 🔗 Weiterführende Links

- OWASP ProActive Controls
- NIST Secure Software Development Framework
- STRIDE Threat Modeling

---

## ❓ Fragen zur Selbstüberprüfung

1. Warum ist Threat Modeling vor der Implementierung wichtig?
2. Nenne drei Properties einer fail-secure Implementierung.
3. Was ist der Unterschied zwischen Unit-Tests und Penetrationstests für Tools?

---

---

## 🎯 Selbsttest — Modul 3.3

**Prüfe dein Verständnis!**

### Frage 1: Threat Modeling
> Warum ist Threat Modeling VOR der Implementierung wichtig?

<details>
<summary>💡 Lösung</summary>

**Antwort:** Threat Modeling vor der Implementierung deckt Sicherheitslücken im DESIGN auf — bevor sie in Code werden. Es ist ~10x billiger, ein Sicherheitsproblem im Design zu beheben als nach der Implementierung. Wenn Security erst nachträglich hinzugefügt wird, bleibt die Architektur oft unsicher.
</details>

### Frage 2: Fail-Secure
> Nenne drei Properties einer fail-secure Implementierung.

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) **Graceful Failure** — Bei Fehlern wird sicher gehandelt (nicht offen bleiben); 2) **No Information Leakage** — Fehlermeldungen geben keine sensitiven Informationen preis; 3) **Default-Deny** — Wenn die Validierung fehlschlägt oder unsicher ist, wird die Aktion ABGELEHNT statt ausgeführt. Beispiel: Wenn ein Zertifikat nicht verifiziert werden kann, wird die Verbindung ABGEBROCHEN, nicht aufgebaut.
</details>

### Frage 3: Unit-Tests vs. Penetrationstests
> Was ist der Unterschied zwischen Unit-Tests und Penetrationstests für Tools?

<details>
<summary>💡 Lösung</summary>

**Antwort:** Unit-Tests prüfen, ob der Code das TUT, was er soll (korrekte Funktion). Penetrationstests prüfen, ob der Code das TUT, was er soll, AUCH WENN ein Angreifer es ausnutzt (Sicherheit unter Adversarial Conditions). Unit-Tests haben bekannte Inputs und erwartete Outputs — Pentests haben bösartige Inputs und unerwartete, gefährliche Outputs.
</details>

*Lektion 3.3 — Ende*
---

## 🎯 Selbsttest — Modul 3.3

**Prüfe dein Verständnis!**

### Frage 1: Was sind die 5 Schritte für sichere Tool-Implementierung?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) Input validieren, 2) Allowlist für Tools, 3) Rate-Limiting, 4) Output sanitizen, 5) Audit-Logging
</details>

### Frage 2: Warum ist Audit-Logging wichtig?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Ohne Logging gibt es keine Nachvollziehbarkeit. Bei Sicherheitsvorfällen muss man rekonstruieren können was passiert ist, wer was wann aufgerufen hat.
</details>

