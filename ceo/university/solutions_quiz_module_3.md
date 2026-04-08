# Modul 3 — Lösungsschlüssel: Tool-Input-Validation meistern

**Kurs:** OpenClaw University  
**Modul:** 3 — Tool-Input-Validation  
**Erstellt:** 2026-04-08

---

# TEIL A — Multiple Choice (40 Punkte)

---

## Frage 1 — Lösung

**Richtige Antwort: b**

**Erklärung:** Whitelist definiert, WAS erlaubt ist — alles andere wird abgelehnt. Blacklist definiert, WAS verboten ist — unbekannte Angriffsmuster fallen durch. Whitelist schützt daher auch vor neuen, noch unbekannten Angriffen.

---

## Frage 2 — Lösung

**Richtige Antwort: b**

**Erklärung:** Tool-Specs sollten vor Manipulation geschützt werden durch Hash-Validierung (jede Spec hat einen Hash ihrer Inhalte) und Immutability (Specs können nicht zur Laufzeit modifiziert werden). So wird verhindert, dass Angreifer Specs ändern um Tools zu kompromittieren.

---

## Frage 3 — Lösung

**Richtige Antwort: b**

**Erklärung:** Tool-Fencing sichert die Ausführungsumgebung selbst ab — Ressourcenlimits (CPU, Memory), Netzwerkbeschränkungen (nur erlaubte Hosts/Ports), und Zeitlimits. Das ergänzt Input-Validation als weitere Sicherheitsschicht.

---

## Frage 4 — Lösung

**Richtige Antwort: c**

**Erklärung:** HTML-Encoding (html.escape) wandelt special characters um: `<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`. So wird verhindert, dass HTML-Tags im Output vom Browser interpretiert werden.

---

## Frage 5 — Lösung

**Richtige Antwort: b**

**Erklärung:** Bei Double Encoding encodiert ein Angreifer Zeichen zwei Mal (z.B. `<` → `%3C` → `%253C`). Der Filter dekodiert einmal und sieht `%3C` — kein `<`. Nach weiterer Verarbeitung wird daraus doch ein `<` und der Angriff funktioniert.

---

## Frage 6 — Lösung

**Richtige Antwort: a**

**Erklärung:** Dieselben Daten müssen in unterschiedlichen Ausgabekontexten unterschiedlich escaped werden. HTML braucht HTML-Encoding, JavaScript braucht JS-Escaping, URLs brauchen URL-Encoding. Falsches Escaping in einem Kontext kann Angriffe ermöglichen.

---

## Frage 7 — Lösung

**Richtige Antwort: b**

**Erklärung:** Homograph-Angriffe nutzen Unicode-Zeichen die visuell ähnlich aussehen aber verschiedene Codepoints haben. Kyrillisches "а" (U+0430) sieht aus wie lateinisches "a" (U+0061). NFKC-Normalisierung überführt beide in die kanonische Form.

---

## Frage 8 — Lösung

**Richtige Antwort: b**

**Erklärung:** Bei Path Traversal nutzt ein Angreifer Sequenzen wie `../` oder encodierte Varianten (`..%2F`), um aus dem erlaubten Verzeichnis auszubrechen und auf Dateien außerhalb zuzugreifen (z.B. `/etc/passwd`).

---

## Frage 9 — Lösung

**Richtige Antwort: b**

**Erklärung:** Typische Reihenfolge:
1. Trimmen (Whitespaces entfernen)
2. Null-Bytes und Control Characters entfernen
3. Unicode normalisieren (NFKC)
4. Filtern (schädliche Zeichen entfernen)
5. Encoding für Ausgabekontext

Erst normalisieren, dann filtern — um Homograph- und Encoding-Angriffe zu erkennen.

---

## Frage 10 — Lösung

**Richtige Antwort: b**

**Erklärung:** Fail-Secure bedeutet: Wenn die Validierung einen Fehler feststellt oder unsicher ist, wird der Input ABGELEHNT. Das System fällt sicher, nicht offen. Das LLM wird NICHT gefragt — denn LLMs sind nicht deterministisch.

---

# TEIL B — True/False (15 Punkte)

---

## Frage 11 — Lösung

**Richtige Antwort: Falsch**

**Erklärung:** Input-Validation und Input-Sanitization sind NICHT dasselbe:
- **Validation** prüft: "Ist diese Eingabe sicher?" — und lehnt ab oder akzeptiert
- **Sanitization** transformiert: "Bereinige die Eingabe" — schädliche Elemente werden entfernt, encoded oder isoliert

---

## Frage 12 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** Tool-Specs sollten immutable sein — einmal definiert sollten sie nicht zur Laufzeit modifizierbar sein. Wenn eine Spec manipuliert werden kann, könnte ein Angreifer die Regeln für Input-Validation ändern.

---

## Frage 13 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** HTML-Body und JavaScript-String müssen unterschiedlich escaped werden:
- HTML: `<` → `&lt;`
- JS: Backslash escapen, Anführungszeichen maskieren
Falscher Kontext = Angriff möglich.

---

## Frage 14 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** NFKC-Normalisierung (Normalization Form Compatibility Composition) überführt ähnlich aussehende Zeichen in ihre kanonische Form. Kyrillisches "а" → lateinisches "a". Das erkennt Homograph-Angriffe bevor Pattern-Matching beginnt.

---

## Frage 15 — Lösung

**Richtige Antwort: Falsch**

**Erklärung:** Schema-Validation ist SICHERER als Content-Filtering. Schema-Validation prüft gegen ein formales Schema (Typ, Struktur, Wertebereich). Content-Filtering (Blacklist) erkennt nur bekannte schädliche Muster.

---

# TEIL C — Praxisfragen (30 Punkte)

---

## Frage 16 — Lösung

**Antwort:**

### Teilaufgabe a: 7 Validierungsschritte

1. **Leer-String Check** — Leere oder nur Whitespaces ablehnen
2. **Path Traversal Check** — `../` und encodierte Varianten erkennen
3. **Normalisieren** — Pfad auflösen und relativ zum BASE_DIR machen
4. **BASE_DIR-Verifikation** — Prüfen ob aufgelöster Pfad noch im erlaubten Verzeichnis liegt
5. **Extension-Prüfung** — Nur erlaubte Dateitypen (`.txt`, `.md`, `.json`)
6. **Existenz-Prüfung** — Datei muss existieren
7. **Typ-Prüfung** — Kein Symlink, keine Directory

### Teilaufgabe b: Path-Traversal-Prüfung (Pseudocode)

```python
BLOCKED_PATTERNS = [r"\.\./", r"^/", r"^~", r"[\x00-\x1f]"]

def validate_path(user_path: str, base_dir: str) -> bool:
    # 1. Blockierte Patterns prüfen
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, user_path):
            return False
    
    # 2. Normalisieren
    full_path = os.path.normpath(os.path.join(base_dir, user_path))
    
    # 3. Verify within BASE_DIR (nach Normalisierung!)
    real_base = os.path.normpath(base_dir)
    if not full_path.startswith(real_base + os.sep):
        return False
    
    return True
```

### Teilaufgabe c: Tool-Fencing-Maßnahme

**Resource-Limits:** Maximal 10MB Dateigröße, maximal 1000 Zeilen Lesen, CPU-Time-Limit von 30 Sekunden. Bei Überschreitung → Timeout.

---

## Frage 17 — Lösung

**Antwort:**

### Teilaufgabe a: Ist diese Sanitisierung vollständig?

**NEIN.** Diese Sanitisierung ist NICHT vollständig:
- `'\\''` und `"\\\""` escapen nur Anführungszeichen
- Backslash-Sequenzen (`\n`, `\t`, `\x00`) werden NICHT escaped
- Unicode-Zeichen (Homograph-Angriffe) werden nicht behandelt
- HTML-Tags können in manchen JS-Kontexten noch funktionieren

### Teilaufgabe b: Angriffe die trotzdem funktionieren könnten

1. `text = "hello\\nalert('xss')"` → Newline injiziert Code
2. `text = "hello\\x3cscript\\x3ealert(1)\\x3c/script\\x3e"` → Hex-encoded HTML
3. Homograph: kyrillisches "а" in Variablenname
4. `</script>` kann aus String "entkommen" wenn unescaped

### Teilaufgabe c: Korrekte kontext-abhängige Sanitisierung

```python
import json

def sanitize_for_js_string(text: str) -> str:
    """Sichere Sanitisierung für JS-String-Kontext."""
    # JSON-konformer Escape
    return json.dumps(text)[1:-1]  # Entfernt Anführungszeichen

# Oder manuell:
def sanitize_for_js_manual(text: str) -> str:
    escapes = {
        '\\': '\\\\',
        '"': '\\"',
        "'": "\\'",
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
        '\x00': '\\x00'
    }
    result = text
    for char, escape in escapes.items():
        result = result.replace(char, escape)
    return result
```

---

## Frage 18 — Lösung

**Antwort:**

### Teilaufgabe a: Art des Angriffs

**Indirekte Prompt Injection (ML01)**

### Teilaufgabe b: Bei welcher Komponente blockieren?

**Input-Validation/Sanitisierung** — der E-Mail-Footer mit `[SYSTEM: ...]` sollte erkannt und entfernt werden, BEVOR er in den Kontext des AI-Systems gelangt.

### Teilaufgabe c: Schutzmaßnahme in Python

```python
import re

def sanitize_email_content(email_body: str) -> str:
    """Entfernt potenzielle Prompt-Injection aus E-Mail-Inhalten."""
    
    # 1. Bekannte Injection-Patterns erkennen und entfernen
    injection_patterns = [
        r'\[SYSTEM[^\]]*\]',           # [SYSTEM: ...]
        r'\[INST[^\]]*\]',             # [INSTRUCTION: ...]
        r'<\s*SYSTEM[^>]*>',           # <SYSTEM>...</SYSTEM>
        r'ignore\s+(all\s+)?previous',  # ignore previous instructions
        r'disregard\s+(all\s+)?your',
    ]
    
    sanitized = email_body
    for pattern in injection_patterns:
        sanitized = re.sub(pattern, '[BLOCKED]', sanitized, flags=re.IGNORECASE)
    
    # 2. Normale Whitelist-Sanitisierung
    sanitized = sanitized.strip()
    
    return sanitized

# Alternative: Kontext-Isolation
def process_email_structured(sender, subject, body):
    """Kontext-Isolation: E-Mail als strukturierte Parameter, nicht als Prompt."""
    return {
        "sender": sanitize(sender),
        "subject": sanitize(subject), 
        "body": body  # Original-Body wird NICHT in Prompt concateniert
    }
```

### Teilaufgabe d: Defense-in-Depth-Maßnahme

**Output-Validation:** Auch die LLM-Ausgabe scannen, bevor sie an den User zurückgeht. Das ist die letzte Verteidigungslinie, falls Input-Validation umgangen wurde.

---

# TEIL D — Code Review (15 Punkte)

---

## Frage 19 — Lösung

**Antwort:**

### Teilaufgabe a: Security-Probleme identifiziert

| # | Problem | Art | Risiko |
|---|---------|-----|--------|
| 1 | Keine Input-Validierung für `to`, `subject`, `body` | Validation | HIGH |
| 2 | `smtplib.SMTP` ohne TLS/SSL | Encryption | HIGH |
| 3 | E-Mail-Body könnte Header-Injection enthalten (`\n` im Subject) | Injection | HIGH |
| 4 | Keine Authentifizierung am SMTP-Server | Auth | MEDIUM |
| 5 | Hardcoded SMTP-Server `smtp.company.com` | Config | MEDIUM |
| 6 | `body` nicht escaped für HTML-Mails | XSS | MEDIUM |
| 7 | Kein Rate-Limiting | DoS | LOW |

### Teilaufgabe b: Sichere Version

```python
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header

class SecureEmailTool:
    SMTP_SERVER = "smtp.company.com"
    SMTP_PORT = 587  # TLS
    
    # Whitelist-Validierung
    VALID_EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    MAX_BODY_LENGTH = 50000
    MAX_SUBJECT_LENGTH = 200
    
    def validate_email_address(self, email: str) -> bool:
        """Validiert E-Mail-Adresse gegen Whitelist-Pattern."""
        return bool(self.VALID_EMAIL_PATTERN.match(email))
    
    def sanitize_subject(self, subject: str) -> str:
        """Sanitisiert Subject gegen Header-Injection."""
        # Keine Newlines erlauben
        subject = subject.replace('\n', ' ').replace('\r', '')
        # HTML-Tags entfernen
        subject = re.sub(r'<[^>]+>', '', subject)
        # Length limit
        return subject[:self.MAX_SUBJECT_LENGTH]
    
    def sanitize_body(self, body: str) -> str:
        """Sanitisiert Body für Plain-Text E-Mail."""
        # Newlines normalisieren
        body = body.replace('\r\n', '\n').replace('\r', '\n')
        # Length limit
        return body[:self.MAX_BODY_LENGTH]
    
    def send_email(self, to: str, subject: str, body: str):
        """
        Sichere E-Mail-Senden-Methode.
        """
        # 1. Input-Validation
        if not self.validate_email_address(to):
            raise ValueError(f"Invalid recipient email: {to}")
        
        if not self.validate_email_address("noreply@company.com"):
            raise ValueError("Invalid sender email")
        
        sanitized_subject = self.sanitize_subject(subject)
        sanitized_body = self.sanitize_body(body)
        
        # 2. Sanitized Body für Plain-Text
        msg = MIMEText(sanitized_body, 'plain', 'utf-8')
        msg['Subject'] = Header(sanitized_subject, 'utf-8')
        msg['From'] = "noreply@company.com"
        msg['To'] = to
        
        # 3. SMTP mit TLS
        with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
            server.starttls()  # TLS-Verschlüsselung
            # server.login(...)  # Auth wenn nötig
            server.send_message(msg)
```

---

**Ende des Lösungsschlüssels**
