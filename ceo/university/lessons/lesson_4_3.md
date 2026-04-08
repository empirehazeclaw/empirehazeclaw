# Lektion 4.3: Sichere Nachrichtenkanäle implementieren

**Modul:** 4 — Secure Multi-Agent Kommunikation  
**Dauer:** 60 Minuten  
**Schwierigkeit:** ⭐⭐⭐⭐  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## 🎯 Lernziele

Am Ende dieser Lektion kannst du:

- ✅ Sichere Kommunikationsprotokolle zwischen Agenten implementieren
- ✅ Nachrichten-Authentifizierung und Integrität gewährleisten
- ✅ Encryption für Agenten-Nachrichten implementieren
- ✅ Replay-Angriffe verhindern

---

## 📖 Inhalt

### 1. Die Anatomie einer sicheren Agent-Nachricht

Eine sichere Agent-Nachricht besteht aus mehreren Schichten:

```
┌─────────────────────────────────────────┐
│            ENVELOPE                      │
│  - Absender                             │
│  - Empfänger                            │
│  - Timestamp                            │
│  - Message-ID                           │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         AUTHENTICATION LAYER             │
│  - Digital Signature (HMAC)              │
│  - Certificate/Key-ID                    │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│           ENCRYPTION LAYER               │
│  - Encrypted Payload                     │
│  - Encryption Algorithm                  │
│  - IV/Nonce                             │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│             CONTENT                      │
│  - Action                               │
│  - Parameters                            │
│  - Context                              │
└─────────────────────────────────────────┘
```

### 2. Message Format und Signing

```python
import json
import hmac
import hashlib
import secrets
import time
from dataclasses import dataclass, asdict
from typing import Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key

@dataclass
class SecureMessage:
    """Eine sicher verpackte Agent-Nachricht."""
    
    # Envelope
    message_id: str
    sender: str
    recipient: str
    timestamp: float
    expires_at: float
    
    # Authentication
    key_id: str
    signature: str
    
    # Encrypted Content
    encrypted_payload: str
    iv: str
    
    # Metadata
    message_type: str
    conversation_id: Optional[str] = None
    
    def to_json(self) -> str:
        """Serialisiert die Nachricht als JSON."""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, data: str) -> "SecureMessage":
        """Deserialisiert eine Nachricht aus JSON."""
        return cls(**json.loads(data))
    
    def is_expired(self) -> bool:
        """Prüft, ob die Nachricht abgelaufen ist."""
        return time.time() > self.expires_at


class MessageSigner:
    """
    Signiert Nachrichten mit HMAC oder asymmetrischer Kryptographie.
    """
    
    def __init__(self, shared_secret: Optional[bytes] = None):
        self.shared_secret = shared_secret or secrets.token_bytes(32)
        self.fernet = Fernet(Fernet.generate_key())  # Placeholder
    
    def sign(self, message: dict) -> str:
        """
        Erstellt eine HMAC-Signature für eine Nachricht.
        """
        # Normalisiere die Nachricht für konsistentes Signing
        canonical = json.dumps(message, sort_keys=True, separators=(',', ':'))
        
        signature = hmac.new(
            self.shared_secret,
            canonical.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify(self, message: dict, signature: str) -> bool:
        """
        Verifiziert eine Signatur.
        """
        expected = self.sign(message)
        return hmac.compare_digest(expected, signature)


class SecureMessageBuilder:
    """
    Baul Nachrichten sicher zusammen.
    """
    
    def __init__(self, sender: str, signing_key: bytes, encryption_key: bytes):
        self.sender = sender
        self.signer = MessageSigner(signing_key)
        self.cipher = Fernet(encryption_key)
        self.message_ttl = 300  # 5 Minuten
    
    def build_message(
        self,
        recipient: str,
        action: str,
        payload: dict,
        message_type: str = "command"
    ) -> SecureMessage:
        """
        Baut eine vollständig sichere Nachricht.
        """
        # 1. Erstelle Envelope-Daten
        message_id = secrets.token_urlsafe(16)
        timestamp = time.time()
        expires_at = timestamp + self.message_ttl
        
        # 2. Erstelle Content-Dictionary für Signing
        content = {
            "action": action,
            "payload": payload,
            "timestamp": timestamp
        }
        
        # 3. Signiere den Content
        content_json = json.dumps(content, sort_keys=True)
        signature = self.signer.sign(content)
        
        # 4. Encrypt den Content
        iv = secrets.token_bytes(16)
        encrypted = self._encrypt(content_json.encode('utf-8'), iv)
        
        # 5. Baue das SecureMessage-Objekt
        return SecureMessage(
            message_id=message_id,
            sender=self.sender,
            recipient=recipient,
            timestamp=timestamp,
            expires_at=expires_at,
            key_id="key_v1",  # In der Praxis: Key-ID aus Key-Management
            signature=signature,
            encrypted_payload=encrypted.decode('utf-8'),
            iv=iv.decode('utf-8'),
            message_type=message_type
        )
    
    def _encrypt(self, data: bytes, iv: bytes) -> bytes:
        """Vereinfachte Encryption mit Fernet."""
        key = Fernet.generate_key()  # In der Praxis: aus dem Key-Management
        return Fernet(key).encrypt(data)
```

### 3. Nachrichtenvalidierung

```python
class MessageValidator:
    """
    Validiert eingehende sichere Nachrichten.
    """
    
    def __init__(self, known_keys: dict[str, bytes]):
        """
        known_keys: Mapping von key_id -> shared_secret
        """
        self.known_keys = known_keys
        self.recent_message_ids: set[str] = set()  # Für Replay-Schutz
        self.replay_window = 3600  # 1 Stunde
    
    def validate(self, message: SecureMessage) -> tuple[bool, str]:
        """
        Validiert eine eingehende Nachricht.
        
        Returns: (is_valid, error_message)
        """
        # 1. Check: Ist die Nachricht abgelaufen?
        if message.is_expired():
            return False, "Message expired"
        
        # 2. Check: Replay-Angriff?
        if not self._check_replay(message.message_id):
            return False, "Replay detected"
        
        # 3. Check: Key-ID bekannt?
        if message.key_id not in self.known_keys:
            return False, f"Unknown key_id: {message.key_id}"
        
        # 4. Check: Signature verifizieren
        key = self.known_keys[message.key_id]
        signer = MessageSigner(key)
        
        # Rekonstruiere den Content für Signature-Verification
        content = {
            "action": self._decrypt_action(message.encrypted_payload, message.iv),
            "timestamp": message.timestamp
        }
        
        if not signer.verify(content, message.signature):
            return False, "Invalid signature"
        
        # 5. Check: Recipient ist korrekt (dieser Agent)?
        # (Wird vom aufrufenden Code geprüft)
        
        return True, "Valid"
    
    def _check_replay(self, message_id: str) -> bool:
        """
        Prüft auf Replay-Angriffe.
        """
        if message_id in self.recent_message_ids:
            return False
        
        # Alte Message-IDs aufräumen
        self.recent_message_ids.add(message_id)
        if len(self.recent_message_ids) > 10000:
            # Behalte nur die neuesten
            self.recent_message_ids = set(list(self.recent_message_ids)[-5000:])
        
        return True
    
    def _decrypt_action(self, encrypted: str, iv: str) -> str:
        """Entschlüsselt den Action-Teil (vereinfacht)."""
        # In der Praxis: echte Decryption
        return "redacted_for_validation"


class AgentMessageHandler:
    """
    Verarbeitet eingehende Nachrichten für einen Agenten.
    """
    
    def __init__(self, agent_name: str, validator: MessageValidator):
        self.agent_name = agent_name
        self.validator = validator
    
    def handle_message(self, raw_message: str) -> tuple[bool, dict, str]:
        """
        Verarbeitet eine eingehende Nachricht.
        
        Returns: (accepted, parsed_payload, error_message)
        """
        # 1. Parse JSON
        try:
            message = SecureMessage.from_json(raw_message)
        except (json.JSONDecodeError, TypeError) as e:
            return False, {}, f"Invalid JSON: {e}"
        
        # 2. Prüfe Recipient
        if message.recipient != self.agent_name:
            return False, {}, f"Message not for me (got {message.recipient})"
        
        # 3. Validiere die Nachricht
        is_valid, error = self.validator.validate(message)
        if not is_valid:
            return False, {}, f"Validation failed: {error}"
        
        # 4. Entschlüssle den Payload
        try:
            payload = self._decrypt_payload(message)
        except Exception as e:
            return False, {}, f"Decryption failed: {e}"
        
        return True, payload, ""
    
    def _decrypt_payload(self, message: SecureMessage) -> dict:
        """Entschlüsselt den Nachrichtenpayload."""
        # In der Praxis: echte Decryption mit dem richtigen Key
        encrypted_bytes = message.encrypted_payload.encode('utf-8')
        iv = message.iv.encode('utf-8')
        
        # Placeholder: Hier echte Decryption implementieren
        # decrypted = cipher.decrypt(encrypted_bytes)
        # return json.loads(decrypted)
        
        return {"action": "decrypted", "status": "placeholder"}
```

### 4. Sicherer Message Queue

```python
import queue
import threading
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class QueuedMessage:
    """Eine Nachricht in der Queue."""
    secure_message: SecureMessage
    received_at: float
    attempts: int = 0


class SecureMessageQueue:
    """
    Eine threadsichere Message Queue mit Security-Features.
    """
    
    def __init__(self, max_size: int = 1000):
        self.queue = queue.Queue(maxsize=max_size)
        self.lock = threading.Lock()
        self.handlers: dict[str, Callable] = {}
    
    def register_handler(self, message_type: str, handler: Callable):
        """Registriert einen Handler für einen Nachrichtentyp."""
        self.handlers[message_type] = handler
    
    def enqueue(self, message: SecureMessage) -> bool:
        """
        Fügt eine Nachricht zur Queue hinzu.
        """
        try:
            queued = QueuedMessage(
                secure_message=message,
                received_at=time.time()
            )
            self.queue.put_nowait(queued)
            return True
        except queue.Full:
            log_security_event("QUEUE_FULL", {
                "message_id": message.message_id,
                "queue_size": self.queue.qsize()
            })
            return False
    
    def process_messages(self, validator: MessageValidator):
        """
        Verarbeitet Nachrichten aus der Queue.
        Sollte in einem eigenen Thread laufen.
        """
        while True:
            try:
                queued = self.queue.get(timeout=1)
                message = queued.secure_message
                
                # Validierung
                is_valid, error = validator.validate(message)
                if not is_valid:
                    log_security_event("INVALID_MESSAGE", {
                        "message_id": message.message_id,
                        "error": error
                    })
                    continue
                
                # Handler aufrufen
                handler = self.handlers.get(message.message_type)
                if handler:
                    try:
                        handler(message)
                    except Exception as e:
                        log_security_event("HANDLER_ERROR", {
                            "message_id": message.message_id,
                            "error": str(e)
                        })
                else:
                    log_security_event("NO_HANDLER", {
                        "message_type": message.message_type
                    })
                
            except queue.Empty:
                continue
            except Exception as e:
                log_security_event("QUEUE_ERROR", {"error": str(e)})
```

---

## 🧪 Praktische Übungen

### Übung 1: Nachrichten-Signing implementieren

Implementiere ein vollständiges Message-Signing-System:

1. Erstelle eine `sign_message()` Funktion, die:
   - Eine Nachricht als Dictionary nimmt
   - Einen HMAC-SHA256 Signature erstellt
   - Timestamp und Message-ID hinzufügt

2. Erstelle eine `verify_message()` Funktion, die:
   - Die Nachricht und Signature nimmt
   - Verifiziert, dass sie nicht manipuliert wurde
   - Das Timestamp prüft (nicht älter als 5 Minuten)

3. Teste mit mindestens 3 Szenarien:
   - Valide Nachricht
   - Manipulierte Nachricht
   - Abgelaufene Nachricht

### Übung 2: Replay-Schutz implementieren

Implementiere einen Replay-Schutz für Nachrichten:

1. Nutze ein Set oder eine Redis-ähnliche Datenstruktur
2. Speichere alle Message-IDs der letzten Stunde
3. Prüfe bei jeder Nachricht, ob die ID bereits verwendet wurde
4. Entferne automatisch alte Einträge

### Übung 3: End-to-End encrypted Channel

Entwirf und implementiere einen einfachen end-to-end encrypted Kanal zwischen zwei Agenten:

```
Agent A                          Agent B
   |                                |
   |-------- Key Exchange --------->|
   |                                |
   |------- Encrypted Msg -------->|
   |<------ Encrypted Reply --------|
```

Nutze Python's `cryptography` Bibliothek für RSA oder AES.

---

## 📚 Zusammenfassung

Sichere Nachrichtenkanäle sind das Rückgrat jeder Multi-Agent-Kommunikation. Die Kernkomponenten:

1. **Authentifizierung** — Wer hat die Nachricht wirklich geschickt?
2. **Integrität** — Wurde die Nachricht unterwegs manipuliert?
3. **Verschlüsselung** — Können Dritte den Inhalt lesen?
4. **Frische** — Ist die Nachricht aktuell oder ein Replay?

Ohne diese Properties ist jede Agent-Kommunikation ein Risiko.

Im nächsten Modul werden wir uns mit praktischen Security Audits beschäftigen.

---

## 🔗 Weiterführende Links

- HMAC Specification (RFC 2104)
- Fernet Encryption (cryptography library)
- Signal Protocol für Ende-zu-Ende Verschlüsselung

---

## ❓ Fragen zur Selbstüberprüfung

1. Warum ist ein Timestamp in einer sicheren Nachricht wichtig?
2. Erkläre den Unterschied zwischen Authentication und Encryption.
3. Wie verhindert man Replay-Angriffe bei Nachrichten?

---

---

## 🎯 Selbsttest — Modul 4.3

**Prüfe dein Verständnis!**

### Frage 1: Timestamp in sicheren Nachrichten
> Warum ist ein Timestamp in einer sicheren Nachricht wichtig?

<details>
<summary>💡 Lösung</summary>

**Antwort:** Ein Timestamp ermöglicht die Prüfung auf **Frische (Freshness)** — ist die Nachricht aktuell oder wurde sie很久之前 gesendet und ist vielleicht ein Replay-Angriff? Es ermöglicht auch **Time-to-Live (TTL)** — Nachrichten können ablaufen (z.B. nach 5 Minuten), umReplay-Angriffe zu verhindern. Ohne Timestamp könnte ein Angreifer aufgezeichnete, gültige Nachrichten erneut abspielen.
</details>

### Frage 2: Authentication vs. Encryption
> Erkläre den Unterschied zwischen Authentication und Encryption.

<details>
<summary>💡 Lösung</summary>

**Antwort:** **Authentication** (Authentifizierung) beantwortet die Frage: "Wer hat das geschickt?" — Sie verifiziert die Identität des Absenders (z.B. via HMAC-Signatur, Zertifikate). **Encryption** (Verschlüsselung) beantwortet die Frage: "Können Dritte den Inhalt lesen?" — Sie macht den Inhalt für Unbefugte unlesbar. Beide sind unabhängig voneinander notwendig: Man kann authentifiziert aber unverschlüsselt kommunizieren (Integrität ja, Privatsphäre nein) oder verschlüsselt aber nicht authentifiziert (Privatsphäre ja, aber Angreifer könnte eigene Nachrichten einschleusen).
</details>

### Frage 3: Replay-Angriffe verhindern
> Wie verhindert man Replay-Angriffe bei Nachrichten?

<details>
<summary>💡 Lösung</summary>

**Antwort:** **1) Message-ID-Tracking** — Jede Nachricht hat eine eindeutige ID; das System speichert alle IDs der letzten Stunde und lehnt Duplikate ab. **2) Timestamps + TTL** — Nachrichten haben ein Ablaufdatum und werden nach Ablauf abgelehnt. **3) Nonce/Challenge-Response** — Der Empfänger schickt eine Zufallszahl, die in die nächste Nachricht eingebaut werden muss. **4) Sequenznummern** — Nachrichten haben steigende Sequenznummern; ältere werden verworfen.
</details>

*Lektion 4.3 — Ende*
---

## 🎯 Selbsttest — Modul 4.3

**Prüfe dein Verständnis!**

### Frage 1: Was ist ein HMAC und wofür wird es bei Agent-Kommunikation verwendet?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** HMAC (Hash-based Message Authentication Code) wird verwendet um die Authentizität und Integrität von Nachrichten zu garantieren. Der Absender signiert mit einem geheimen Schlüssel, der Empfänger prüft mit dem gleichen Schlüssel.
</details>

### Frage 2: Warum reicht HTTPS nicht aus für Agent-to-Agent Security?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** HTTPS verschlüsselt die Verbindung, aber ein Man-in-the-Middle könnte trotzdem Nachrichten abfangen und manipulieren bevor sie verschlüsselt werden. Außerdem bietet HTTPS keine Message-Signatur.
</details>

