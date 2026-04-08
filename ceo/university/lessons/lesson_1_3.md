# Lektion 1.3: Defense — Input Validation Patterns

**Modul:** 1 — Prompt Injection & Jailbreaking  
**Dauer:** 60 Minuten  
**Schwierigkeit:** ⭐⭐⭐ Fortgeschritten  
**Zuletzt aktualisiert:** 2026-04-08

---

## 🎯 Lernziele

Am Ende dieser Lektion kannst du:

- ✅ Die verschiedenen Arten von Input-Validation-Strategien unterscheiden und anwenden
- ✅ Whitelist- vs. Blacklist-basierte Validierung verstehen und wissen, wann welche Methode sinnvoll ist
- ✅ Strukturierte Validation-Patterns für Agent-Systeme implementieren
- ✅ Kontext-Isolation zwischen User-Input und System-Prompt korrekt umsetzen
- ✅ Ein mehrschichtiges Input-Validation-System entwerfen und implementieren

---

## 📖 Inhalt

### 1. Die Grundlagen: Warum Input-Validation kritisch ist

Input-Validation ist die erste und wichtigste Verteidigungslinie gegen Prompt Injection und Jailbreaking. Die Grundidee ist einfach: Bevor irgendeine Benutzereingabe verarbeitet wird, muss sie auf potenzielle Angriffe geprüft und gegebenenfalls bereinigt oder abgelehnt werden.

Das Problem bei AI-Systemen ist, dass traditionelle Input-Validation-Ansätze nicht ausreichen. Bei einer Web-Anwendung können Sie prüfen, ob eine E-Mail-Adresse das richtige Format hat oder ob eine Zahl innerhalb eines erwarteten Bereichs liegt. Bei einem AI-System ist die "Validierung" weitaus komplexer, weil natürliche Sprache keine festen Formate hat und dieselbe Bedeutung auf unendlich viele Arten ausgedrückt werden kann.

Ein weiteres Problem ist der Kontext. Ein und dieselbe Eingabe kann je nach Kontext harmlos oder bösartig sein. "Zeig mir die Passwörter" ist harmlos, wenn es in einem Passwort-Manager-Tool eingegeben wird, aber bösartig, wenn es als Prompt-Injection in einem AI-Chatbot verwendet wird. Ihre Validation muss daher kontextabhängig sein.

### 2. Blacklist vs. Whitelist: Zwei Philosophien

Die Diskussion zwischen Blacklist- und Whitelist-basierter Validierung ist fundamental für das Verständnis von Input-Validation.

**Blacklist-basierte Validierung** ist der Ansatz, bei dem bekannte schädliche Muster blockiert werden. Sie definieren eine Liste von "verbotenen" Wörtern, Phrasen oder Patterns, und jede Eingabe, die eines dieser Muster enthält, wird abgelehnt oder bereinigt. Dieser Ansatz hat den Vorteil, dass er einfach zu implementieren ist und sofort vor bekannten Angriffen schützt. Der große Nachteil ist, dass er nie vollständig sein kann — es wird immer neue Angriffsmuster geben, die nicht auf der Blacklist stehen.

Ein typisches Blacklist-Beispiel:
```python
BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "disregard your programming",
    "you are now a",
    "[system]:",
    "developer mode",
]

def blacklist_validate(text):
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in text.lower():
            return False, f"Blocked pattern detected: {pattern}"
    return True, None
```

**Whitelist-basierte Validierung** ist der gegenteilige Ansatz. Anstatt zu definieren, was verboten ist, definieren Sie, was erlaubt ist. Nur Eingaben, die dem erlaubten Muster entsprechen, werden akzeptiert. Alles andere wird abgelehnt. Dieser Ansatz ist sicherer, weil er auch vor unbekannten Angriffen schützt, aber er ist auch restriktiver und kann schwieriger zu implementieren sein.

Ein typisches Whitelist-Beispiel:
```python
import re

# Nur erlaubt: Buchstaben, Zahlen, Leerzeichen, Punkte, Kommas, Fragezeichen
ALLOWED_PATTERN = re.compile(r'^[a-zA-Z0-9\s.,?!äöüÄÖÜß]+$')

def whitelist_validate(text):
    if ALLOWED_PATTERN.match(text):
        return True, None
    return False, "Input contains disallowed characters"
```

**Hybride Ansätze** kombinieren beide Methoden. Die Whitelist definiert das grundsätzliche Format, das akzeptiert wird, und die Blacklist fängt bekannte Angriffsmuster ab, die otherwise durch die Whitelist fallen könnten.

### 3. Strukturiertes Validation-Framework für Agent-Systeme

Für AI-Agent-Systeme empfehlen wir ein mehrschichtiges Validation-Framework, das aus fünf Stufen besteht.

**Stufe 1: Syntax-Validation**

Die erste Stufe prüft grundlegende syntaktische Eigenschaften. Dazu gehören Zeichensatz-Validierung (nur erlaubte Zeichen), Längenbegrenzungen (maximale Input-Länge) und Formatprüfungen (z.B. ob der Input einem erwarteten Schema entspricht).

```python
def syntax_validate(input_text: str) -> tuple[bool, str]:
    """Stufe 1: Grundlegende Syntax-Validierung."""
    errors = []
    
    # Zeichensatz-Validierung
    if not re.match(r'^[\w\s.,!?;:\-\'\"]+$', input_text):
        errors.append("Invalid character set")
    
    # Längen-Validierung
    if len(input_text) > 10000:
        errors.append("Input exceeds maximum length")
    if len(input_text) < 1:
        errors.append("Input is empty")
    
    # Wiederholungs-Validierung (Verdächtige Wiederholungen deuten auf Angriffe hin)
    if has_suspicious_repetition(input_text):
        errors.append("Suspicious repetition detected")
    
    return len(errors) == 0, "; ".join(errors) if errors else None
```

**Stufe 2: Semantik-Validierung**

Die zweite Stufe analysiert die Bedeutung des Inputs. Dies umfasst die Prüfung auf bekannte Angriffsmuster, die Analyse der Kontext-Kontinuität (passt der Input zum bisherigen Gespräch?) und die Sentiment-Analyse (ist das Sentiment auffällig aggressiv oder manipulativ?).

```python
import re

ATTACK_PATTERNS = [
    (r"ignore\s+(all\s+)?(previous\s+)?(system\s+)?(instructions|commands)", "Instruction Override"),
    (r"(disregard|forget)\s+(your|all)", "Instruction Override"),
    (r"\[(system|developer|admin|root)\]", "Privilege Escalation"),
    (r"you\s+are\s+now\s+(a\s+)?", "Role Manipulation"),
    (r"(pretend|act\s+like)\s+you\s+are", "Role Manipulation"),
    (r"(real|true)\s+(ai|model)\s+without", "Restriction Bypass"),
    (r"(bypass|disable|remove)\s+(safety|filter|restriction)", "Safety Bypass"),
]

def semantic_validate(input_text: str) -> tuple[bool, list[dict]]:
    """Stufe 2: Semantische Validierung auf Angriffsmuster."""
    findings = []
    text_lower = input_text.lower()
    
    for pattern, attack_type in ATTACK_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            findings.append({
                "type": attack_type,
                "pattern": pattern,
                "matches": matches
            })
    
    return len(findings) == 0, findings
```

**Stufe 3: Kontext-Validierung**

Die dritte Stufe prüft den Input im Kontext des gesamten Gesprächs. Dies ist besonders wichtig, weil viele Angriffe auf vorherigen Konversationen aufbauen. Die Kontext-Validierung erkennt plötzliche Themenwechsel, gebrochene Kontinuität und verdächtige Muster über mehrere Nachrichten hinweg.

```python
class ContextValidator:
    """Stufe 3: Kontext-basierte Validierung."""
    
    def __init__(self, conversation_history: list[dict]):
        self.history = conversation_history
        self.topic_stability = self._analyze_topic_stability()
    
    def _analyze_topic_stability(self) -> float:
        """Berechnet, wie stabil das Thema im Gespräch ist."""
        if len(self.history) < 2:
            return 1.0
        
        # Einfache Analyse: Wie viele Wörter kommen in aufeinanderfolgenden 
        # Nachrichten wieder vor?
        overlaps = 0
        for i in range(1, len(self.history)):
            prev_words = set(self.history[i-1]["content"].lower().split())
            curr_words = set(self.history[i]["content"].lower().split())
            if prev_words & curr_words:  # Intersection
                overlaps += 1
        
        return overlaps / (len(self.history) - 1)
    
    def validate_with_context(self, new_input: str) -> tuple[bool, str]:
        """Validiert Input unter Berücksichtigung des Kontexts."""
        # Plötzlicher Themenwechsel?
        if self.topic_stability > 0.5 and len(self.history) > 3:
            # Thema war stabil, aber neue Input könnte ein Angriff sein
            if self._is_sudden_topic_change(new_input):
                return False, "Sudden topic change detected after stable conversation"
        
        # Verdächtige Input-Länge im Vergleich zum bisherigen Gespräch?
        avg_length = sum(len(m["content"]) for m in self.history) / len(self.history)
        if len(new_input) > avg_length * 5:
            return False, "Unusual input length compared to conversation history"
        
        return True, None
    
    def _is_sudden_topic_change(self, new_input: str) -> bool:
        """Erkennt plötzliche Themenwechsel."""
        if not self.history:
            return False
        
        last_topic_words = set(self.history[-1]["content"].lower().split())
        new_words = set(new_input.lower().split())
        
        # Wenige gemeinsame Wörter = wahrscheinlich Themenwechsel
        overlap = len(last_topic_words & new_words)
        return overlap < 3
```

**Stufe 4: Kontext-Isolation**

Die vierte Stufe ist technisch gesehen keine "Validierung", sondern eine architektonische Sicherheitsmaßnahme. Das Prinzip ist einfach: User-Input und System-Prompts werden niemals in demselben String zusammengeführt. Stattdessen werden sie als separate strukturierte Parameter übergeben.

```python
# UNSICHER (NIEMALS SO):
def unsafe_process(user_input, system_prompt):
    full_prompt = f"{system_prompt}\n\nUser: {user_input}"
    return call_llm(full_prompt)

# SICHER:
def safe_process(user_input, user_context):
    structured_params = {
        "user_message": sanitize(user_input),
        "session_id": user_context["session_id"],
        "user_role": user_context["role"],
        "allowed_actions": user_context["allowed_actions"],
        "max_data_access": user_context.get("max_data_access", "none")
    }
    # System-Prompt wird separat und sicher gehalten
    return call_llm_structured(
        system_prompt=get_system_prompt(),  # Niemals User-Input hier
        user_params=structured_params
    )
```

**Stufe 5: Output-Validation**

Die fünfte Stufe validiert die Ausgaben des LLM, bevor sie an den Benutzer oder an nachgelagerte Systeme zurückgegeben werden. Dies ist wichtig, weil ein LLM trotz Input-Validation bösartige Ausgaben generieren könnte — sei es durch halluzinierte Inhalte oder durch raffinierte Umgehungsversuche.

```python
SENSITIVE_PATTERNS = [
    (r"password[:\s]+\S+", "Password Exposure"),
    (r"passwort[:\s]+\S+", "Password Exposure (German)"),
    (r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b", "Credit Card Number"),
    (r"\d{3}[\s\-]?\d{2}[\s\-]?\d{4}", "SSN/Sozialversicherungsnummer"),
    (r"sk-\S{20,}", "API Key"),
    (r"ghp_\S{20,}", "GitHub Token"),
]

def validate_output(output: str) -> tuple[bool, list[dict]]:
    """Validiert LLM-Output auf sensible Daten."""
    findings = []
    
    for pattern, data_type in SENSITIVE_PATTERNS:
        matches = re.findall(pattern, output, re.IGNORECASE)
        if matches:
            findings.append({
                "type": "Sensitive Data",
                "data_type": data_type,
                "count": len(matches)
            })
    
    return len(findings) == 0, findings
```

### 4. Praktische Implementierung: Das SecureAgent-Framework

Das folgende Framework integriert alle fünf Validierungsstufen in ein kohärentes System:

```python
from dataclasses import dataclass
from typing import Optional
import logging

@dataclass
class ValidationResult:
    is_valid: bool
    stage: str
    message: Optional[str]
    details: Optional[list] = None

class SecureInputProcessor:
    """
    Mehrschichtiges Input-Validation-System für Agent-Systeme.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize validators
        self.max_input_length = config.get("max_input_length", 10000)
        self.allowed_chars = config.get("allowed_chars", r"^[\w\s.,!?;:\-\'\"]+$")
    
    def validate(self, user_input: str, context: dict) -> ValidationResult:
        """
        Führt alle fünf Validierungsstufen durch.
        """
        # Stufe 1: Syntax
        result = self._syntax_validation(user_input)
        if not result.is_valid:
            return result
        
        # Stufe 2: Semantik
        result = self._semantic_validation(user_input)
        if not result.is_valid:
            return result
        
        # Stufe 3: Kontext
        result = self._context_validation(user_input, context)
        if not result.is_valid:
            return result
        
        # Stufe 4 & 5: Input-Bereinigung und Prepared Output
        sanitized = self._sanitize(user_input)
        
        return ValidationResult(
            is_valid=True,
            stage="all",
            message="Input passed all validation stages",
            details={"sanitized": sanitized}
        )
    
    def _syntax_validation(self, text: str) -> ValidationResult:
        """Stufe 1: Syntax-Validierung."""
        if len(text) > self.max_input_length:
            return ValidationResult(False, "syntax", f"Input exceeds {self.max_input_length} chars")
        
        if not re.match(self.allowed_chars, text):
            return ValidationResult(False, "syntax", "Input contains disallowed characters")
        
        return ValidationResult(True, "syntax", None)
    
    def _semantic_validation(self, text: str) -> ValidationResult:
        """Stufe 2: Semantische Validierung."""
        text_lower = text.lower()
        
        for pattern, description in ATTACK_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                self.logger.warning(f"Attack pattern detected: {description}")
                return ValidationResult(
                    False, "semantic", 
                    f"Blocked: {description}",
                    details=[{"pattern": pattern, "type": description}]
                )
        
        return ValidationResult(True, "semantic", None)
    
    def _context_validation(self, text: str, context: dict) -> ValidationResult:
        """Stufe 3: Kontext-Validierung."""
        # Placeholder für kontextabhängige Validierung
        # In echter Implementierung: conversation_history analysieren
        return ValidationResult(True, "context", None)
    
    def _sanitize(self, text: str) -> str:
        """Bereinigt Input für sichere Verarbeitung."""
        # Entferne potenzielle Escape-Sequenzen
        sanitized = text.replace("[", "").replace("]", "")
        sanitized = sanitized.replace("{", "").replace("}", "")
        sanitized = sanitized.replace("\\", "")
        return sanitized.strip()
```

### 5. Best Practices und häufige Fehler

**Best Practices:**

1. **Defense in Depth:** Verwende immer mehrere Validierungsschichten. Keine einzelne Schicht ist perfekt.

2. **Fail-Secure:** Wenn die Validierung einen Fehler feststellt, lehne den Input ab — vertraue nicht darauf, dass das LLM den Angriff "schon erkennen wird".

3. **Log everything:** Protokolliere alle Validierungsfehler für spätere Analyse und Penetration Testing.

4. **Regelmäßige Pattern-Updates:** Aktualisiere deine Blacklists regelmäßig basierend auf neuen Angriffsmustern.

5. **User-Feedback:** Zeige Benutzern eine generische Fehlermeldung, nicht die Details deiner Validierungslogik.

**Häufige Fehler:**

1. **Zu einfache Patterns:** "ignore" zu blockieren ist nicht ausreichend — "disregard", "disregard all prior", "from now on" etc. werden übersehen.

2. **Case-Sensitive Matching:** Viele Angriffe funktionieren auch in Großbuchstaben oder gemischter Schreibweise.

3. **Keine Längenbegrenzung:** Lange Inputs können Buffer-Overflow-ähnliche Probleme verursachen.

4. **Vertrauen in Output:** Auch validierter Input kann zu bösartigem Output führen.

---

## 🧪 Praktische Übungen

### Übung 1: Validation erweitern

Erweitere das SecureAgent-Framework um eine vierte semantische Validierungsschicht:

1. Füge ein Pattern für "Base64-encodete Angriffe" hinzu
2. Implementiere eine Unicode-Normalisierung, die homographische Angriffe erkennt
3. Füge eine Prüfung für excessive capitalization hinzu (kann auf Aggression hindeuten)

### Übung 2: Whitelist-Validator implementieren

Implementiere einen Whitelist-basierten Validator, der nur Eingaben akzeptiert, die:

- Nur erlaubte Wörter aus einem definierten Dictionary enthalten
- Maximal 5 Wörter lang sind
- Nur aus einem bestimmten Satz von Fragetypen bestehen ("was", "wie", "wo", "wer", "warum")

### Übung 3: Penetrationstest durchführen

Führe einen Penetrationstest gegen die Implementierung aus dieser Lektion durch:

1. Finde 5 Eingaben, die alle Validation-Stufen bestehen, aber einen Angriff darstellen
2. Dokumentiere, warum diese Eingaben problematisch sind
3. Schlage Verbesserungen vor, die diese Eingaben blockieren würden

---

## 📚 Zusammenfassung

Input-Validation ist die fundamentalste Verteidigungsmaßnahme gegen Prompt Injection und Jailbreaking. Ein mehrschichtiger Ansatz mit fünf Stufen — Syntax, Semantik, Kontext, Isolation und Output-Validierung — bietet den robustesten Schutz.

Die wichtigsten Prinzipien sind: Vertraue niemals direktem User-Input, implementiere Defense in Depth, und aktualisiere deine Patterns regelmäßig. Keine einzelne Maßnahme ist ausreichend, aber in Kombination reduzieren sie das Risiko erheblich.

Im nächsten Modul werden wir uns die OWASP Top 10 für AI Agents im Detail ansehen und lernen, wie diese Risiken in der Praxis bewertet und mitigiert werden.

---

## 🔗 Weiterführende Links

- OWASP Input Validation Cheat Sheet
- NIST Guidelines for Input Validation
- karpathy/llmsecurity: Security Patterns

---

## ❓ Fragen zur Selbstüberprüfung

1. Was ist der Unterschied zwischen Blacklist- und Whitelist-basierter Validierung, und wann sollte man welche verwenden?
2. Erklären Sie die fünf Stufen des strukturierten Validation-Frameworks.
3. Warum ist Kontext-Validierung wichtig, wenn einzelne Eingaben unauffällig erscheinen?
4. Was bedeutet "Fail-Secure" im Kontext von Input-Validation?
5. Nennen Sie drei häufige Fehler bei der Implementierung von Input-Validation.

---

*Lektion 1.3 — Ende*
---

## 🎯 Selbsttest — Modul 1.3

**Prüfe dein Verständnis!**

### Frage 1: Nenne 3 Verteidigungsstrategien gegen Prompt Injection
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) Input-Validation & Sanitization, 2) Kontext-Isolation (User-Input separat verarbeiten), 3) Prompt/Ausgabe-Filtering, 4) Least Privilege für Tool-Nutzung
</details>

### Frage 2: Was ist der wichtigste Grundsatz bei der Agent-Konfiguration?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Least Privilege — Agents sollten nur die minimal nötigen Rechte haben. So wird der Schaden bei einer erfolgreichen Injection minimiert.
</details>

