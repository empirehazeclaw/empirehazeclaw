# Lektion 3.1: Tool-Spec Design & Validation

**Modul:** 3 — Tool-Input-Validation meistern  
**Dauer:** 60 Minuten  
**Schwierigkeit:** ⭐⭐⭐⭐  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## 🎯 Lernziele

Am Ende dieser Lektion kannst du:

- ✅ Tool-Specifications sicher entwerfen und dokumentieren
- ✅ Die Anatomie einer sicheren Tool-Spec verstehen
- ✅ Input-Validation auf Spec-Ebene implementieren
- ✅ Tool-Specs gegen Angriffe absichern

---

## 📖 Inhalt

### 1. Die Anatomie eines Tools

Ein Tool in einem AI-Agent-System besteht aus mehreren Komponenten, die jeweils sicher designed werden müssen:

**Die Definition** beschreibt, was das Tool tut — seinen Zweck, seine Parameter, seine Outputs.

**Die Implementierung** ist der Code, der das Tool ausführt.

**Das Interface** ist die Schnittstelle zwischen Agent und Tool — hier passiert die Kommunikation.

**Die Validation** prüft Inputs und Outputs auf Sicherheit.

Ein sicheres Tool-Design beginnt bei der Definition. Wenn die Spec unsicher ist, wird es die Implementierung auch sein.

### 2. Sichere Tool-Spec erstellen

#### 2.1 Parametrisierung

Ein sicheres Tool definiert seine Parameter explizit und beschränkt jeden Parameter auf erlaubte Typen, Wertebereiche und Formate.

```python
from pydantic import BaseModel, Field
from typing import Literal

class FileReadSpec(BaseModel):
    """
    Sichere Spec für Dateileser-Tool.
    """
    # Expliziter Parameter-Name und Typ
    path: str = Field(
        description="Der Pfad zur zu lesenden Datei",
        min_length=1,
        max_length=500
    )
    
    # Encoding explizit whitelisten
    encoding: Literal["utf-8", "ascii", "latin-1"] = Field(
        default="utf-8",
        description="Dateicodierung"
    )
    
    # Zeilenbereich begrenzen (DoS-Schutz)
    max_lines: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximale Anzahl zu lesender Zeilen"
    )
    
    # Sanitization für Path Traversal
    @property
    def sanitized_path(self) -> str:
        """Bereinigt den Pfad von potenziellen Path-Traversal-Versuchen."""
        import os
        # Normalisiere und verhindere ../
        normalized = os.path.normpath(self.path)
        if normalized.startswith(".."):
            raise ValueError("Invalid path: traversal detected")
        return normalized
```

#### 2.2 Validierung der Spezifikation

Nicht nur die Parameter müssen validiert werden — die Spec selbst muss gegen Manipulation geschützt werden.

**Spec-Chaining:** Wenn ein Tool eine andere Spec lädt oder referenziert, muss diese ebenfalls validiert werden.

**Immutability:** Eine einmal definierte Spec sollte nicht zur Laufzeit modifizierbar sein.

**Versionierung:** Jede Spec hat eine Versionsnummer, um Replay-Angriffe zu verhindern.

```python
from pydantic import BaseModel, validator
from typing import Dict, Any
import hashlib
import json

class ToolSpec(BaseModel):
    """
    Basisklasse für sichere Tool-Specs.
    """
    name: str
    version: str
    parameters: Dict[str, Any]
    spec_hash: str = ""
    
    @validator("spec_hash", always=True)
    def compute_hash(cls, v, values):
        """Berechnet einen Hash der Spec-Inhalte."""
        content = json.dumps(values, sort_keys=True, exclude={"spec_hash"})
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def validate_spec_chain(self, other_specs: list["ToolSpec"]):
        """
        Validiert die Integrität der Spec-Kette.
        """
        for spec in other_specs:
            if not self.verify_spec_hash(spec):
                raise SpecValidationError(f"Spec-Kette für {spec.name} kompromittiert")
    
    def verify_spec_hash(self, spec: "ToolSpec") -> bool:
        """Verifiziert den Hash einer referenzierten Spec."""
        expected = self.compute_spec_hash(spec)
        return expected == spec.spec_hash
```

### 3. Input-Validation Patterns

#### 3.1 Whitelist- vs. Blacklist-Validation

Wie in Lektion 1 besprochen: Whitelist ist sicherer, weil sie auch vor unbekannten Angriffen schützt.

Für Tool-Inputs empfehlen wir:

```python
# UNSICHER — Blacklist
BLOCKED_CHARS = ["<", ">", "|", ";", "&", "$"]
def blacklist_validate(input_text):
    for char in BLOCKED_CHARS:
        if char in input_text:
            return False
    return True

# SICHER — Whitelist
ALLOWED_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-./ ")
def whitelist_validate(input_text):
    return all(c in ALLOWED_CHARS for c in input_text)
```

#### 3.2 Schema-Validation

Tool-Inputs sollten gegen ein formales Schema validiert werden — nicht nur auf Typ, sondern auch auf Struktur.

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class APICallSpec(BaseModel):
    """
    Sichere Spec für API-Call-Tool.
    """
    endpoint: str = Field(
        description="Der API-Endpoint",
        min_length=1,
        max_length=2000
    )
    method: Literal["GET", "POST", "PUT", "DELETE"] = Field(
        description="HTTP-Methode"
    )
    headers: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="HTTP-Headers"
    )
    body: Optional[str] = Field(
        default=None,
        max_length=100000,
        description="Request-Body"
    )
    
    @validator("endpoint")
    def validate_endpoint(cls, v):
        """Validiert und bereinigt den Endpoint."""
        # Nur erlaubte Protokolle
        if not re.match(r"^https?://", v):
            raise ValueError("Nur HTTP/HTTPS erlaubt")
        
        # Host-Blacklist für interne Dienste
        INTERNAL_HOSTS = {"localhost", "127.0.0.1", "169.254.169.254", "metadata.google.internal"}
        from urllib.parse import urlparse
        host = urlparse(v).netloc.split(":")[0].lower()
        if host in INTERNAL_HOSTS:
            raise ValueError(f"Zugriff auf internen Host {host} verboten")
        
        return v
    
    @validator("headers")
    def validate_headers(cls, v):
        """Entfernt potenziell gefährliche Headers."""
        SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key"}
        return {k: v for k, v in v.items() if k.lower() not in SENSITIVE_HEADERS}
```

### 4. Tool-Fencing

Tool-Fencing ist die Praxis, Tools in sichere Sandkästen einzusperren, sodass selbst bei einer Kompromittierung des Tools der Schaden begrenzt ist.

#### 4.1 Ressourcen-Fencing

```python
import resource
import signal

class SecureToolRunner:
    """
    Führt Tools in einer ressourcenbeschränkten Umgebung aus.
    """
    
    def __init__(self, max_memory_mb: int = 512, max_cpu_seconds: int = 30):
        self.max_memory = max_memory_mb * 1024 * 1024  # Bytes
        self.max_cpu = max_cpu_seconds
    
    def run(self, tool_func, *args, **kwargs):
        """Führt eine Tool-Funktion in einer Sandbox aus."""
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Tool exceeded {self.max_cpu}s CPU time")
        
        # Setze CPU-Limit
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.max_cpu)
        
        # Setze Memory-Limit (Linux)
        try:
            resource.setrlimit(resource.RLIMIT_AS, (self.max_memory, self.max_memory))
        except (ValueError, OSError):
            pass  # Nicht alle Plattformen unterstützen dies
        
        try:
            result = tool_func(*args, **kwargs)
            signal.alarm(0)  # Alarm zurücksetzen
            return result
        except TimeoutError:
            log_security_event("TOOL_TIMEOUT", {"function": tool_func.__name__})
            raise
        finally:
            signal.alarm(0)
```

#### 4.2 Netzwerk-Fencing

```python
class NetworkToolFence:
    """
    Beschränkt Netzwerkzugriff für Tools.
    """
    
    ALLOWED_HOSTS = {
        "api.company.com",
        "database.company.com",
        # Whitelist der erlaubten Ziele
    }
    
    BLOCKED_PORTS = {22, 23, 3389, 5432, 27017}  # SSH, Telnet, RDP, PostgreSQL, MongoDB
    
    @classmethod
    def validate_connection(cls, host: str, port: int) -> bool:
        """Prüft, ob eine Netzwerkverbindung erlaubt ist."""
        if host not in cls.ALLOWED_HOSTS:
            return False
        if port in cls.BLOCKED_PORTS:
            return False
        return True
```

---

## 🧪 Praktische Übungen

### Übung 1: Spec-Design

Entwirf eine sichere Tool-Spec für ein "Email-Senden-Tool" mit folgenden Anforderungen:
- Empfänger muss eine validierte Email-Adresse sein
- Body darf maximal 10.000 Zeichen haben
- Keine HTML-Injection möglich
- cc und bcc optional, aber wenn vorhanden, ebenfalls validiert

Implementiere die Spec mit Pydantic und teste sie.

### Übung 2: Tool-Fencing Audit

Du hast ein Tool, das Code ausführen kann:
```python
def execute_code(code: str, language: str):
    # Führt Code in einem Container aus
    pass
```

Führe ein Security-Audit durch:
1. Was sind die Risiken?
2. Entwirf mindestens 5 Fencing-Regeln für dieses Tool
3. Implementiere das Fencing

### Übung 3: Validation Chain

Du hast zwei Tools: Tool A ruft Tool B auf. Tool B validiert seine Inputs, aber Tool A ruft Tool B ohne erneute Validierung auf.

1. Was kann schiefgehen?
2. Wie designst du eine sichere Validation-Chain?

---

## 📚 Zusammenfassung

Tool-Spec-Design ist die Grundlage für sichere AI-Agent-Systeme. Eine sichere Spec definiert Parameter explizit, validiert Inputs gegen Schemata, schützt sich gegen Manipulation, und implementiert mehrschichtige Validation.

Tool-Fencing ergänzt die Spec-Validation, indem es die Ausführungsumgebung selbst absichert — Ressourcenlimits, Netzwerkbeschränkungen, und Zeitlimits.

Im nächsten Kapitel werden wir Input-Sanitization-Patterns im Detail betrachten.

---

## 🔗 Weiterführende Links

- Pydantic Validation: https://docs.pydantic.dev/
- OWASP Input Validation Cheat Sheet
- NIST Secure Software Development Framework

---

## ❓ Fragen zur Selbstüberprüfung

1. Warum ist Whitelist-Validation sicherer als Blacklist-Validation bei Tool-Inputs?
2. Was ist Tool-Fencing und warum ist es notwendig, obwohl Input-Validation existiert?
3. Erkläre den Unterschied zwischen Spec-Validation und Input-Validation.

---

---

## 🎯 Selbsttest — Modul 3.1

**Prüfe dein Verständnis!**

### Frage 1: Whitelist- vs. Blacklist-Validation
> Warum ist Whitelist-Validation bei Tool-Inputs sicherer als Blacklist-Validation?

<details>
<summary>💡 Lösung</summary>

**Antwort:** Whitelist-Validation ist sicherer, weil sie nur explizit erlaubte Werte akzeptiert und unbekannte Angriffe (z.B. neue Sonderzeichen oder Encoding-Varianten) automatisch blockiert. Blacklist-Validation hingegen muss alle gefährlichen Werte AUFLISTEN — neue oder unerwartete Angriffe werden nicht erkannt, da sie nicht auf der Blacklist stehen.
</details>

### Frage 2: Tool-Fencing
> Was ist Tool-Fencing und warum ist es notwendig, obwohl Input-Validation existiert?

<details>
<summary>💡 Lösung</summary>

**Antwort:** Tool-Fencing schützt die AUSFÜHRUNGSUMGEBUNG selbst — also Ressourcenlimits (CPU, Memory), Netzwerkbeschränkungen und Zeitlimits. Selbst wenn Input-Validation korrekt funktioniert, kann ein legitimes Tool durch Programmierfehler, Edge Cases oder DoS-Angriffe Schaden anrichten. Tool-Fencing begrenzt diesen Schaden auf ein Minimum.
</details>

### Frage 3: Spec-Validation vs. Input-Validation
> Erkläre den Unterschied zwischen Spec-Validation und Input-Validation.

<details>
<summary>💡 Lösung</summary>

**Antwort:** Spec-Validation prüft die INTEGRITÄT und UNVERFÄLSCHTHEIT der Tool-Spezifikation selbst (Hashes, Versionierung, Immutability). Input-Validation prüft die KONKRETEN EINGABEWERTE, die ein User an ein Tool übergibt. Spec-Validation ist also eine Schicht VOR der Input-Validation — sie stellt sicher, dass das Tool überhaupt das ist, für das es sich ausgibt.
</details>

*Lektion 3.1 — Ende*
---

## 🎯 Selbsttest — Modul 3.1

**Prüfe dein Verständnis!**

### Frage 1: Was ist eine Tool-Spec und warum ist sie wichtig?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Eine Tool-Spec definiert die Schnittstelle eines Tools: Name, Parameter, Typen, Beschreibung. Sie ist der Vertrag zwischen Agent und Tool — ohne Spec weiß der Agent nicht wie er das Tool nutzen soll.
</details>

### Frage 2: Warum ist die Reihenfolge der Parameter in einer Spec wichtig?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Einige Models sind positionsabhängig. Die wichtigsten Parameter sollten zuerst kommen, optionale Parameter später. Auch für die Lesbarkeit und Debugging.
</details>

