# Modul 4 — Lösungsschlüssel: Secure Multi-Agent Kommunikation

**Kurs:** OpenClaw University  
**Modul:** 4 — Secure Multi-Agent Kommunikation  
**Erstellt:** 2026-04-08

---

# TEIL A — Multiple Choice (40 Punkte)

---

## Frage 1 — Lösung

**Richtige Antwort: b**

**Erklärung:** Multi-Agent-Security ist komplizierter, weil es nicht nur eine Grenze zwischen Agent und Außenwelt gibt, sondern viele interne Grenzen zwischen Agenten. Jede Kommunikationsverbindung ist ein potenzieller Angriffsvektor.

---

## Frage 2 — Lösung

**Richtige Antwort: b**

**Erklärung:** Nach dem Empfang einer Nachricht muss Agent B dreifach validieren:
- **Integrität:** Ist die Nachricht unterwegs nicht manipuliert worden?
- **Authentizität:** Kommt sie wirklich von Agent A?
- **Freshness:** Ist die Nachricht aktuell oder ein Replay?

---

## Frage 3 — Lösung

**Richtige Antwort: b**

**Erklärung:** Message Injection bedeutet, dass ein Angreifer sich in den Kommunikationskanal schaltet und bösartige Nachrichten injiziert — er tut so, als wäre er Agent A, obwohl er es nicht ist.

---

## Frage 4 — Lösung

**Richtige Antwort: b**

**Erklärung:** Bei Replay Attacks zeichnet ein Angreifer gültige Nachrichten auf und spielt sie später erneut ab. Das System akzeptiert die Nachricht, weil sie eine gültige Signature hat — aber sie ist nicht mehr aktuell.

---

## Frage 5 — Lösung

**Richtige Antwort: b**

**Erklärung:** Eine Trust-Zone ist ein Bereich im System, in dem alle Komponenten das gleiche Security-Level teilen. Innerhalb einer Zone gelten bestimmte Annahmen über Integrität und Authentizität.

---

## Frage 6 — Lösung

**Richtige Antwort: b**

**Erklärung:** Tampering (T in STRIDE) bedeutet, dass Daten während der Übertragung manipuliert werden. Ein Angreifer fängt eine Nachricht ab, ändert sie, und leitet sie weiter — der Empfänger merkt es nicht.

---

## Frage 7 — Lösung

**Richtige Antwort: b**

**Erklärung:** RBAC bedeutet: Rollen definieren, was ein Agent tun darf. Agenten werden Rollen zugewiesen, nicht einzelne Permissions. Ein Agent kann mehrere Rollen haben — die effektiven Berechtigungen sind die Vereinigung aller Rollen-Berechtigungen.

---

## Frage 8 — Lösung

**Richtige Antwort: b**

**Erklärung:** Least-Privilege besagt, dass jeder Agent nur die Berechtigungen bekommt, die er für seine spezifische Aufgabe braucht — nicht mehr. Das begrenzt den Schaden, wenn ein Agent kompromittiert wird.

---

## Frage 9 — Lösung

**Richtige Antwort: c**

**Erklärung:** Die Encryption Layer verschlüsselt den eigentlichen Inhalt (Payload). Die Authentication Layer signiert nur (HMAC), verschlüsselt aber nicht. Das Envelope enthält Metadaten, und Content ist der eigentliche plaintext-Inhalt.

---

## Frage 10 — Lösung

**Richtige Antwort: b**

**Erklärung:** HMAC (Hash-based Message Authentication Code) wird für Authentifizierung verwendet — es stellt sicher, dass eine Nachricht vom richtigen Absender stammt und nicht manipuliert wurde. Es verschlüsselt NICHT den Inhalt.

---

# TEIL B — True/False (15 Punkte)

---

## Frage 11 — Lösung

**Richtige Antwort: Falsch**

**Erklärung:** In einem Multi-Agent-System muss NICHT jeder Agent jedem anderen vertrauen. Gerade das ist das Problem! Verschiedene Agenten haben verschiedene Trust-Level, und Kommunikation muss explizit validiert werden.

---

## Frage 12 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** Session Hijacking bedeutet, dass ein Angreifer eine bestehende, authentifizierte Session zwischen Agenten übernimmt — er stiehlt das Session-Token und nutzt es, um sich als einer der Agenten auszugeben.

---

## Frage 13 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** RBAC erlaubt, dass ein Agent mehrere Rollen hat. Die effektiven Berechtigungen sind die UNION aller Rollen-Berechtigungen. Das erlaubt flexible Berechtigungsverwaltung.

---

## Frage 14 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** Ein Timestamp ist wichtig für Freshness-Validierung. Ohne Timestamp könnte ein Angreifer gültige Nachrichten aufzeichnen und später erneut senden (Replay Attack). Mit Timestamp kann das System veraltete Nachrichten erkennen.

---

## Frage 15 — Lösung

**Richtige Antwort: Falsch**

**Erklärung:** Authentifizierung und Verschlüsselung sind NICHT dasselbe:
- **Authentifizierung** (HMAC, Signatures): "Wer hat diese Nachricht gesendet?"
- **Verschlüsselung** (AES, RSA): "Kann jemand den Inhalt lesen?"
Eine Nachricht kann authentifiziert aber unverschlüsselt sein (oder umgekehrt).

---

# TEIL C — Zuordnungsfrage (15 Punkte)

---

## Frage 16 — Lösung

| # | Beschreibung | Kategorie | Multi-Agent Beispiel |
|---|-------------|-----------|---------------------|
| A | Identität eines Agenten fälschen | S (Spoofing) | Angreifer gibt sich als CEO Agent aus |
| B | Nachricht unterwegs ändern | T (Tampering) | Man-in-the-Middle ändert Nachrichteninhalt |
| C | Agent leugnet Nachricht gesendet zu haben | R (Repudiation) | Builder behauptet, er habe den Code nicht geschickt |
| D | Vertrauliche Daten durch Kommunikation enthüllen | I (Information Disclosure) | Nachrichten werden an falschen Agenten geleitet |
| E | Kommunikationskanal blockieren | D (Denial of Service) | Angreifer flutet Message Queue mit Requests |
| F | Agent erhält unbefugt mehr Rechte | E (Elevation of Privilege) | Low-Privilege Agent führt Admin-Aktionen aus |

---

# TEIL D — Praxisfragen (30 Punkte)

---

## Frage 17 — Lösung

**Antwort:**

### Teilaufgabe a: Trust-Zonen-Diagramm

```
┌─────────────────────────────────────────────────────────────┐
│                    TRUST ZONE 0 (HÖCHSTES VERTRAUEN)        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    CEO      │  │   Security   │  │    Data     │       │
│  │   Agent     │  │   Officer    │  │   Manager   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                │                │                  │
│         └────────────────┼────────────────┘                  │
│                          │                                   │
│              Shared Secret Store (Trust Boundary)            │
└──────────────────────────┼───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    TRUST ZONE 1 (EXTERNAL/LOWER TRUST)       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Builder    │  │   Research   │  │   External   │       │
│  │   Agent      │  │   Agent      │  │   Services   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Teilaufgabe b: Rollen-Berechtigungen

```python
from enum import Enum

class Permission(Enum):
    READ_FILES = "read:files"
    WRITE_FILES = "write:files"
    DELETE_FILES = "delete:files"
    EXECUTE_CODE = "execute:code"
    ACCESS_SECRETS = "access:secrets"
    READ_MEMORY = "read:memory"
    WRITE_MEMORY = "write:memory"
    AUDIT_LOGS = "audit:logs"

class Role:
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions
    
    def has_permission(self, perm):
        return perm in self.permissions

ROLE_BUILDER = Role("BUILDER", {
    Permission.READ_FILES,      # Code lesen
    Permission.WRITE_FILES,     # Code schreiben
    Permission.DELETE_FILES,    # Code löschen (nur workspace)
    Permission.EXECUTE_CODE,    # Code ausführen (in sandbox)
    Permission.READ_MEMORY,     # Knowledge lesen
    Permission.WRITE_MEMORY,   # Knowledge schreiben
})

ROLE_SECURITY_OFFICER = Role("SECURITY_OFFICER", {
    Permission.READ_FILES,      # Config lesen
    Permission.ACCESS_SECRETS,  # Secrets prüfen
    Permission.AUDIT_LOGS,      # Logs auditen
    Permission.READ_MEMORY,     # Memory für Analyse
})
```

### Teilaufgabe c: Begründung

Der Builder sollte KEINE ACCESS_SECRETS Permission haben, weil:
- **Least-Privilege:** Builder braucht keine Secrets für Coding-Aufgaben
- **Schadensbegrenzung:** Wenn Builder kompromittiert wird, können keine API-Keys oder Passwörter gestohlen werden
- **Separation of Concerns:** Security Officer verwaltet Secrets, Builder nutzt sie nur间接

---

## Frage 18 — Lösung

**Antwort:**

### Teilaufgabe a: Drei Schichten

1. **Envelope** — Metadaten: Absender, Empfänger, Timestamp, Message-ID
2. **Authentication Layer** — Digital Signature (HMAC), Key-ID
3. **Encryption Layer** — Verschlüsselter Payload, IV/Nonce

### Teilaufgabe b: Zweck jeder Schicht

| Schicht | Zweck |
|---------|-------|
| Envelope | Identifiziert Sender/Empfänger, ermöglicht Routing und Logging |
| Authentication | Stellt sicher, dass Nachricht wirklich vom Sender stammt (Integrität + Authentizität) |
| Encryption | Verhindert, dass Dritte den Inhalt lesen können (Confidentiality) |

### Teilaufgabe c: Angriffsvektoren und Schutz

**Was Angreifer mit Message-Queue-Zugang tun könnte:**

| Angriff | Schutz durch |
|---------|-------------|
| Nachrichten abfangen und lesen | Encryption Layer — Inhalt unreadable |
| Nachrichten manipulieren | Authentication Layer — Signature stimmt nicht mehr |
| Alte Nachrichten erneut senden | Timestamp + Freshness-Check — expired Nachrichten rejected |
| Eigene Nachrichten injizieren | Authentication + RBAC — Unauthorized sender rejected |

---

## Frage 19 — Lösung

**Antwort:**

### Teilaufgabe a: Permission-Enum (8 Permissions)

```python
from enum import Enum

class Permission(Enum):
    """Mögliche Berechtigungen im Agenten-System."""
    READ_FILES = "read:files"
    WRITE_FILES = "write:files"
    DELETE_FILES = "delete:files"
    EXECUTE_CODE = "execute:code"
    EXECUTE_SHELL = "execute:shell"
    ACCESS_SECRETS = "access:secrets"
    SEND_TO_AGENT = "send:agent"
    RECEIVE_FROM_AGENT = "receive:agent"
    READ_MEMORY = "read:memory"
    WRITE_MEMORY = "write:memory"
    AUDIT_LOGS = "audit:logs"
    CREATE_AGENT = "create:agent"
```

### Teilaufgabe b: Role-Klasse

```python
class Role:
    """Definiert eine Rolle mit ihren Berechtigungen."""
    
    def __init__(self, name: str, permissions: set):
        self.name = name
        self.permissions = permissions
    
    def has_permission(self, permission: Permission) -> bool:
        """Prüft ob diese Rolle eine Permission hat."""
        return permission in self.permissions
    
    def add_permission(self, permission: Permission):
        self.permissions.add(permission)
    
    def remove_permission(self, permission: Permission):
        self.permissions.discard(permission)
    
    def __repr__(self):
        return f"Role({self.name}, permissions={len(self.permissions)})"
```

### Teilaufgabe c: Einfache RBACEngine

```python
class RBACEngine:
    """Einfache RBAC-Engine für Agent-Systeme."""
    
    def __init__(self):
        self.roles = {}  # role_name -> Role
        self.agent_roles = {}  # agent_name -> set of role_names
    
    def register_role(self, role: Role):
        self.roles[role.name] = role
    
    def assign_role(self, agent: str, role_name: str):
        if role_name not in self.roles:
            raise ValueError(f"Unknown role: {role_name}")
        if agent not in self.agent_roles:
            self.agent_roles[agent] = set()
        self.agent_roles[agent].add(role_name)
    
    def get_permissions(self, agent: str) -> set:
        """Gibt alle Berechtigungen eines Agenten zurück."""
        perms = set()
        for role_name in self.agent_roles.get(agent, set()):
            role = self.roles.get(role_name)
            if role:
                perms.update(role.permissions)
        return perms
    
    def authorize(self, agent: str, permission: Permission) -> bool:
        """Prüft ob ein Agent eine bestimmte Permission hat."""
        agent_perms = self.get_permissions(agent)
        return permission in agent_perms


# Beispiel-Nutzung
engine = RBACEngine()
engine.register_role(ROLE_BUILDER)
engine.assign_role("builder_agent", "BUILDER")

print(engine.authorize("builder_agent", Permission.READ_FILES))  # True
print(engine.authorize("builder_agent", Permission.ACCESS_SECRETS))  # False
```

---

**Ende des Lösungsschlüssels**
