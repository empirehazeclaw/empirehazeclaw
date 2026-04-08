# Lektion 3.2: Input Sanitization Patterns

**Modul:** 3 — Tool-Input-Validation meistern  
**Dauer:** 45 Minuten  
**Schwierigkeit:** ⭐⭐⭐  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## 🎯 Lernziele

Am Ende dieser Lektion kannst du:

- ✅ Verschiedene Sanitisierungsstrategien verstehen und anwenden
- ✅ Kontext-abhängige Sanitisierung implementieren
- ✅ Encoding-Angriffe erkennen und verhindern
- ✅ Sanitisierung für verschiedene Input-Typen korrekt durchführen

---

## 📖 Inhalt

### 1. Was ist Input Sanitization?

Input Sanitization ist der Prozess, eingehende Daten zu bereinigen — potenziell schädliche Elemente werden entfernt, encoded oder isoliert, sodass sie keinen Schaden anrichten können.

Während Input-Validation prüft "Ist diese Eingabe sicher?", transformiert Sanitization die Eingabe in eine sichere Form. Der Unterschied: Validation lehnt ab oder akzeptiert, Sanitization bereinigt.

### 2. Sanitisierungstechniken

#### 2.1 Encoding

Encoding wandelt schädliche Zeichen in sichere Darstellungen um.

**HTML-Encoding** verhindert XSS:
```python
import html

def html_encode(text: str) -> str:
    """Enthält HTML-spezialzeichen für sichere Ausgabe."""
    return html.escape(text, quote=True)

# Beispiel
html_encode("<script>alert('xss')</script>")
# Ergebnis: &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;
```

**URL-Encoding** verhindert URL-Injection:
```python
from urllib.parse import quote

def url_encode(text: str) -> str:
    """Encodiert Text für sichere URL-Verwendung."""
    return quote(text, safe="")

url_encode("http://example.com?q=<script>")
# Ergebnis: http%3A//example.com%3Fq%3D%3Cscript%3E
```

**Base64-Encoding** für Datenübertragung (nicht für Security!):
```python
import base64

def base64_encode(data: str) -> str:
    """Encodiert Daten in Base64 (nur für Transport, nicht für Security)."""
    return base64.b64encode(data.encode()).decode()
```

#### 2.2 Filtering

Filtering entfernt schädliche Elemente komplett:

```python
import re

def filter_dangerous_chars(text: str) -> str:
    """
    Entfernt gefährliche Zeichen für generische Texteingabe.
    """
    # Nur alphanumerische Zeichen, Leerzeichen und ausgewählte Satzzeichen
    return re.sub(r"[^a-zA-Z0-9\s.,!?'-]", "", text)

def filter_html_tags(text: str) -> str:
    """Entfernt alle HTML-Tags."""
    return re.sub(r"<[^>]+>", "", text)

def filter_sql_keywords(text: str) -> str:
    """
    Entfernt potenzielle SQL-Injection-Patterns.
    ACHTUNG: Das ist eine Blacklist — weniger sicher als Prepared Statements!
    """
    dangerous = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "--", ";", "UNION"]
    filtered = text
    for keyword in dangerous:
        filtered = re.sub(rf"\b{keyword}\b", "[BLOCKED]", filtered, flags=re.IGNORECASE)
    return filtered
```

#### 2.3 Normalization

Normalization bringt Inputs in eine kanonische, sichere Form:

```python
import unicodedata

def normalize_unicode(text: str) -> str:
    """
    Normalisiert Unicode, um Homograph-Angriffe zu verhindern.
    """
    # NFKC-Normalisierung: Kompatibilitätszerlegung + kanonische Komposition
    return unicodedata.normalize("NFKC", text)

# Beispiel: Kyrillisches "а" (U+0430) → Lateinisches "a" (U+0061)
cyrillic_a = "\u0430"  # "а"
normalized = normalize_unicode(cyrillic_a)  # → "a"
```

### 3. Kontext-abhängige Sanitisierung

Die richtige Sanitisierung hängt vom Kontext ab, in dem der Input verwendet wird:

| Kontext | Sanitisierung | Beispiel |
|---------|--------------|---------|
| HTML-Body | HTML-Encode | `<` → `&lt;` |
| HTML-Attribute | HTML-Encode + Attribut-Quotes | `"` → `&quot;` |
| URL-Parameter | URL-Encode | `&` → `%26` |
| JavaScript | JavaScript-Encode | `\` → `\\` |
| CSS | CSS-Encode | `\` → `\\` |
| SQL (NIEMALS!) | Prepared Statements | Parameterisierung |

```python
class ContextAwareSanitizer:
    """
    Kontext-abhängiger Sanitisierer.
    """
    
    @staticmethod
    def for_html(text: str) -> str:
        """Sanitisiert für HTML-Kontext."""
        import html
        return html.escape(text, quote=True)
    
    @staticmethod
    def for_html_attribute(text: str) -> str:
        """Sanitisiert für HTML-Attribut-Kontext."""
        import html
        escaped = html.escape(text, quote=True)
        # Zusätzlich: Keine Anführungszeichen ohne Kontext
        if not escaped.startswith('"') and not escaped.startswith("'"):
            return f'"{escaped}"'
        return escaped
    
    @staticmethod
    def for_url_param(text: str) -> str:
        """Sanitisiert für URL-Parameter-Kontext."""
        from urllib.parse import quote
        return quote(text, safe="")
    
    @staticmethod
    def for_js_string(text: str) -> str:
        """Sanitisiert für JavaScript-String-Kontext."""
        # JSON-konformer Escape für JS
        import json
        return json.dumps(text)[1:-1]  # Entfernt die Anführungszeichen
    
    @staticmethod
    def for_css(text: str) -> str:
        """Sanitisiert für CSS-Kontext."""
        # CSS-Injection verhindern
        dangerous_chars = ["<", ">", "'", '"', "(", ")", "\\"]
        result = text
        for char in dangerous_chars:
            result = result.replace(char, f"\\{char}")
        return result
```

### 4. Encoding-Angriffe

#### 4.1 Double Encoding

Angreifer nutzen Double Encoding, um Filter zu umgehen:

```
Normal: <script> → %3Cscript%3E
Filter erkennt nicht → wird zu <script>

Double Encoded: %253Cscript%253E
Erster Decode: %3Cscript%3E
Filter sieht immer noch kein < → wird zu <script>
```

**Defense:** Decode mehrfach oder bis sich nichts mehr ändert, dann validieren:

```python
def safe_decode_and_validate(text: str) -> str:
    """
    Dekodiert mehrfach und validiert dann.
    """
    from urllib.parse import unquote
    
    # Mehrmaliges Dekodieren bis keine Änderung mehr
    decoded = text
    while True:
        next_decode = unquote(decoded)
        if next_decode == decoded:
            break
        decoded = next_decode
    
    # Jetzt validieren
    if "<" in decoded or ">" in decoded:
        raise ValueError("Potentially dangerous content detected after decoding")
    
    return decoded
```

#### 4.2 Unicode/Homograph-Angriffe

Visuell identische Zeichen mit unterschiedlichen Codepoints:

```python
# Kyrillisches "а" sieht aus wie lateinisches "a"
CYRILLIC_A = "\u0430"  # "а"
LATIN_A = "a"

# Normalisierung erkennt das
import unicodedata
assert unicodedata.normalize("NFKC", CYRILLIC_A) == LATIN_A

# Defense: Immer normalisieren vor Validierung
def safe_input(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    # Jetzt validieren
    if not re.match(r"^[a-zA-Z]+$", normalized):
        raise ValueError("Invalid characters")
    return normalized
```

### 5. Fortgeschrittene Patterns

#### 5.1 Sanitization Pipeline

```python
class SanitizationPipeline:
    """
    Pipeline für mehrstufige Sanitisierung.
    """
    
    def __init__(self):
        self.steps = []
    
    def add_step(self, func, name: str):
        """Fügt einen Sanitisierungsschritt hinzu."""
        self.steps.append((name, func))
        return self  # Fluide API
    
    def sanitize(self, data: str) -> tuple[str, list[str]]:
        """
        Führt alle Sanitisierungsschritte aus.
        
        Returns: (sanitized_data, list_of_applied_steps)
        """
        result = data
        applied = []
        
        for name, func in self.steps:
            result = func(result)
            applied.append(name)
        
        return result, applied
    
    def validate_only(self, data: str) -> bool:
        """Validiert ohne zu sanitieren."""
        for name, func in self.steps:
            if "filter" in name.lower() or "remove" in name.lower():
                # Diese Schritte verändern Daten
                return False
        return True


# Beispiel: Sichere Pipeline für User-Input
pipeline = SanitizationPipeline()
pipeline.add_step(lambda x: x.strip(), "trim_whitespace")
pipeline.add_step(lambda x: x.replace("\x00", ""), "remove_null_bytes")
pipeline.add_step(lambda x: re.sub(r"[\x00-\x1f\x7f-\x9f]", "", x), "remove_control_chars")
pipeline.add_step(lambda x: unicodedata.normalize("NFKC", x), "normalize_unicode")

sanitized, steps = pipeline.sanitize(user_input)
print(f"Angewendete Schritte: {steps}")
```

#### 5.2 Output Sanitization

Sanitisierung gilt nicht nur für Inputs — Outputs müssen ebenfalls sanitized werden:

```python
def sanitize_llm_output(output: str, context: str) -> str:
    """
    Sanitisiert LLM-Output basierend auf dem Ausgabekontext.
    """
    if context == "web_display":
        # HTML-Escape für Web-Anzeige
        return html.escape(output, quote=True)
    elif context == "json_api":
        # JSON-Safe machen
        return json.dumps(output)[1:-1]
    elif context == "terminal":
        # ANSI-Escape-Sequenzen entfernen
        return re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", output)
    elif context == "file_write":
        # Gefährliche Datei-Zeichen entfernen
        return re.sub(r"[\x00-\x1f]", "", output)
    else:
        # Generisch: Alle Controls entfernen
        return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", output)
```

---

## 🧪 Praktische Übungen

### Übung 1: Homograph-Erkennung

Schreibe ein Programm, das einen eingegebenen String auf Homograph-Angriffe prüft. Das Programm soll:

1. Unicode-Zeichen erkennen, die wie lateinische Zeichen aussehen
2. Eine Warnung ausgeben, wenn solche Zeichen gefunden werden
3. Die Eingabe normalisieren und die.normalisierten Ergebnis anzeigen

Teste mit: "αpple" (griechisches Alpha), "pаypal" (kyrillisches a), "gοogle.com"

### Übung 2: Sanitisierungspipeline

Entwirf eine Sanitisierungspipeline für User-Inputs in einem AI-Chatbot:

1. Whitespace trimmen
2. Null-Bytes entfernen  
3. Control Characters entfernen
4. Unicode normalisieren (NFKC)
5. HTML-Tags entfernen
6. Maximale Länge auf 10.000 Zeichen begrenzen

Implementiere und teste die Pipeline mit verschiedenen Angriff-Inputs.

### Übung 3: Context-Switch-Bug

Ein Entwickler hat folgenden Code geschrieben:

```python
def process(user_input, context):
    sanitized = html_encode(user_input)  # Sanitisiert für HTML
    
    if context == "html":
        return f"<div>{sanitized}</div>"
    elif context == "js":
        return f"document.write('{sanitized}')"  # Bug!
```

1. Erkläre den Bug
2. Wie könnte ein Angreifer das ausnutzen?
3. Schlage eine Korrektur vor

---

## 📚 Zusammenfassung

Input Sanitization ist ein kritisches Puzzlestück in der Security von AI-Systemen. Verschiedene Techniken — Encoding, Filtering, Normalization — haben各有 Stärken und Schwächen.

Der wichtigste Grundsatz: Kontext matters. Dieselben Daten müssen für unterschiedliche Ausgabekontexte unterschiedlich sanitized werden.

Im nächsten Kapitel werden wir die Implementierung eigener sicherer Tools betrachten.

---

## 🔗 Weiterführende Links

- OWASP XSS Prevention Cheat Sheet
- Unicode Security Guide (unicode.org)
- OWASP Input Validation Cheat Sheet

---

## ❓ Fragen zur Selbstüberprüfung

1. Erkläre den Unterschied zwischen Input-Validation und Input-Sanitization.
2. Was ist Double Encoding und wie defendest du dich dagegen?
3. Warum ist kontext-abhängige Sanitisierung wichtig?

---

---

## 🎯 Selbsttest — Modul 3.2

**Prüfe dein Verständnis!**

### Frage 1: Validation vs. Sanitization
> Erkläre den Unterschied zwischen Input-Validation und Input-Sanitization.

<details>
<summary>💡 Lösung</summary>

**Antwort:** Input-Validation PRÜFT, ob eine Eingabe sicher ist — und lehnt sie entweder ab oder akzeptiert sie. Input-Sanitization TRANSFORMIERT die Eingabe in eine sichere Form — sie bereinigt schädliche Zeichen durch Encoding, Filtering oder Normalization. Sanitization ändert die Daten, Validation entscheidet nur über Annahme/Ablehnung.
</details>

### Frage 2: Double Encoding
> Was ist Double Encoding und wie verteidigst du dich dagegen?

<details>
<summary>💡 Lösung</summary>

**Antwort:** Double Encoding ist eine Angriffstechnik, bei der schädliche Zeichen mehrfach encodiert werden (z.B. `<` → `%3C` → `%253C`), um Filter zu umgehen. Der Filter sieht beim ersten Decode nur `%3C` (kein `<`), lässt es durch, und beim zweiten Decode erscheint das `<`. Die Verteidigung: Mehrmaliges Decodieren BIS SICH NICHTS MEHR ÄNDERT, erst DANN validieren.
</details>

### Frage 3: Kontext-abhängige Sanitisierung
> Warum ist kontext-abhängige Sanitisierung wichtig?

<details>
<summary>💡 Lösung</summary>

**Antwort:** Dieselben Daten müssen in unterschiedlichen Ausgabekontexten unterschiedlich sanitized werden. `&` ist in einer URL harmlos, in HTML aber ein Trennzeichen für Attribute. `'` ist in JavaScript gefährlich (String-Abschluss), in CSV aber normal. Die falsche Sanitisierung macht Daten entweder kaputt (zu aggressiv) oder unsicher (zu permissiv).
</details>

*Lektion 3.2 — Ende*
---

## 🎯 Selbsttest — Modul 3.2

**Prüfe dein Verständnis!**

### Frage 1: Was ist Input Sanitization?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Die Bereinigung von Benutzereingaben bevor sie an Tools oder Models weitergegeben werden. Ziel: Schädliche Zeichen/Sequenzen entfernen oder escapen.
</details>

### Frage 2: Nenne 3 Techniken für Input Sanitization
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) Allowlist (nur erlaubte Zeichen), 2) Deny-List (schädliche Zeichen blockieren), 3) Encoding/Escaping, 4) Length-Limits, 5) Type-Checking
</details>

