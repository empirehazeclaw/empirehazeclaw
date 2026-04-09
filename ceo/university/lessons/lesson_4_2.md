# Lektion 4.2: RBAC für Agent-Systeme

**Modul:** 4 — Secure Multi-Agent Kommunikation  
**Dauer:** 60 Minuten  
**Schwierigkeit:** ⭐⭐⭐⭐  
**Zuletzt aktualisiert:** 2026-04-08 (CEO)

---

## 🎯 Lernziele

Am Ende dieser Lektion kannst du:

- ✅ Role-Based Access Control (RBAC) für Agent-Systeme verstehen
- ✅ Rollen und Permissions für eine Agent-Flotte definieren
- ✅ RBAC-Policies implementieren und durchsetzen
- ✅ Das Least-Privilege-Prinzip auf Agenten anwenden

---

## 📖 Inhalt

### 1. RBAC-Grundlagen für Agenten

RBAC (Role-Based Access Control) ist ein etabliertes Security-Modell, das auch für AI-Agent-Systeme essentiell ist. Das Grundprinzip: Nicht einzelne Agenten erhalten Rechte, sondern Rollen — und Agenten werden Rollen zugewiesen.

In einem AI-Agent-System bedeutet das:
- **Roles** definieren, was ein Agent tun darf
- **Permissions** sind die spezifischen Aktionen, die erlaubt sind
- **Assignments** verbinden Agenten mit Rollen

### 2. Rollen-Definition für die OpenClaw-Flotte

```python
from enum import Enum
from typing import Set, Dict, List
import json

class Permission(Enum):
    """Mögliche Berechtigungen im Agenten-System."""
    # Lesen
    READ_FILES = "read:files"
    READ_MEMORY = "read:memory"
    READ_CONFIG = "read:config"
    READ_LOGS = "read:logs"
    
    # Schreiben
    WRITE_FILES = "write:files"
    WRITE_MEMORY = "write:memory"
    WRITE_CONFIG = "write:config"
    WRITE_LOGS = "write:logs"
    
    # Löschen
    DELETE_FILES = "delete:files"
    DELETE_MEMORY = "delete:memory"
    
    # Execution
    EXECUTE_CODE = "execute:code"
    EXECUTE_SHELL = "execute:shell"
    EXECUTE_TOOL = "execute:tool"
    
    # Agent-Kommunikation
    SEND_TO_AGENT = "send:agent"
    RECEIVE_FROM_AGENT = "receive:agent"
    DELEGATE_TASK = "delegate:task"
    
    # Security
    AUDIT_LOGS = "audit:logs"
    ACCESS_SECRETS = "access:secrets"
    ROTATE_KEYS = "rotate:keys"
    
    # Admin
    CREATE_AGENT = "create:agent"
    DESTROY_AGENT = "destroy:agent"
    MODIFY_RBAC = "modify:rbac"


class Role:
    """Definiert eine Rolle mit ihren Berechtigungen."""
    
    def __init__(self, name: str, permissions: Set[Permission], description: str = ""):
        self.name = name
        self.permissions = permissions
        self.description = description
    
    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "permissions": [p.value for p in self.permissions],
            "description": self.description
        }


# vordefinierte Rollen für die OpenClaw-Flotte

ROLE_SYSTEM = Role(
    name="SYSTEM",
    permissions={
        Permission.READ_FILES, Permission.WRITE_FILES,
        Permission.READ_MEMORY, Permission.WRITE_MEMORY,
        Permission.READ_CONFIG, Permission.WRITE_CONFIG,
        Permission.READ_LOGS, Permission.WRITE_LOGS,
        Permission.DELETE_FILES, Permission.DELETE_MEMORY,
        Permission.EXECUTE_CODE, Permission.EXECUTE_SHELL, Permission.EXECUTE_TOOL,
        Permission.SEND_TO_AGENT, Permission.RECEIVE_FROM_AGENT, Permission.DELEGATE_TASK,
        Permission.AUDIT_LOGS, Permission.ACCESS_SECRETS, Permission.ROTATE_KEYS,
        Permission.CREATE_AGENT, Permission.DESTROY_AGENT, Permission.MODIFY_RBAC,
    },
    description="System-Rolle mit uneingeschränkten Rechten"
)

ROLE_CEO = Role(
    name="CEO",
    permissions={
        Permission.READ_FILES, Permission.READ_MEMORY, Permission.READ_CONFIG, Permission.READ_LOGS,
        Permission.WRITE_LOGS,
        Permission.SEND_TO_AGENT, Permission.RECEIVE_FROM_AGENT, Permission.DELEGATE_TASK,
        Permission.AUDIT_LOGS,
    },
    description="CEO - orchestriert die Flotte, delegiert Tasks"
)

ROLE_SECURITY_OFFICER = Role(
    name="SECURITY_OFFICER",
    permissions={
        Permission.READ_FILES, Permission.READ_CONFIG, Permission.READ_LOGS,
        Permission.WRITE_LOGS,
        Permission.AUDIT_LOGS, Permission.ACCESS_SECRETS, Permission.ROTATE_KEYS,
        Permission.SEND_TO_AGENT, Permission.RECEIVE_FROM_AGENT,
    },
    description="Security Officer - führt Audits durch, verwaltet Secrets"
)

ROLE_DATA_MANAGER = Role(
    name="DATA_MANAGER",
    permissions={
        Permission.READ_FILES, Permission.WRITE_FILES,
        Permission.READ_MEMORY, Permission.WRITE_MEMORY, Permission.DELETE_MEMORY,
        Permission.READ_CONFIG,
        Permission.READ_LOGS, Permission.WRITE_LOGS,
        Permission.SEND_TO_AGENT, Permission.RECEIVE_FROM_AGENT,
    },
    description="Data Manager - verwaltet Memory und Datenbanken"
)

ROLE_BUILDER = Role(
    name="BUILDER",
    permissions={
        Permission.READ_FILES, Permission.WRITE_FILES, Permission.DELETE_FILES,
        Permission.READ_CONFIG,
        Permission.EXECUTE_CODE, Permission.EXECUTE_SHELL,
        Permission.READ_LOGS, Permission.WRITE_LOGS,
        Permission.SEND_TO_AGENT, Permission.RECEIVE_FROM_AGENT,
    },
    description="Builder - coded und implementiert"
)

ROLE_RESEARCH = Role(
    name="RESEARCH",
    permissions={
        Permission.READ_FILES, Permission.READ_MEMORY,
        Permission.READ_CONFIG, Permission.READ_LOGS,
        Permission.WRITE_FILES,
        Permission.SEND_TO_AGENT, Permission.RECEIVE_FROM_AGENT,
    },
    description="Research - Recherchiert und analysiert"
)

ROLE_QC_OFFICER = Role(
    name="QC_OFFICER",
    permissions={
        Permission.READ_FILES, Permission.READ_MEMORY, Permission.READ_CONFIG, Permission.READ_LOGS,
        Permission.WRITE_LOGS,
        Permission.SEND_TO_AGENT, Permission.RECEIVE_FROM_AGENT,
    },
    description="QC Officer - validiert Ergebnisse"
)
```

### 3. RBAC-Policy Engine

```python
from dataclasses import dataclass
from typing import Optional
import hashlib
import time

@dataclass
class RBACRequest:
    """Eine RBAC-Anfrage."""
    requesting_agent: str
    target_resource: str
    action: Permission
    context: dict  # Zusätzlicher Kontext (z.B. file path)
    timestamp: float
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass 
class RBACResponse:
    """Eine RBAC-Antwort."""
    allowed: bool
    reason: str
    evaluated_at: float
    
class RBACEngine:
    """
    Die zentrale RBAC-Engine für das Agenten-System.
    """
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.agent_roles: Dict[str, Set[str]] = {}  # agent -> set of roles
        self.session_keys: Dict[str, str] = {}  # session key -> agent
        
        # Registriere alle Rollen
        for role in [ROLE_SYSTEM, ROLE_CEO, ROLE_SECURITY_OFFICER, 
                     ROLE_DATA_MANAGER, ROLE_BUILDER, ROLE_RESEARCH, ROLE_QC_OFFICER]:
            self.register_role(role)
    
    def register_role(self, role: Role):
        """Registriert eine neue Rolle."""
        self.roles[role.name] = role
    
    def assign_role(self, agent: str, role_name: str):
        """Weist einem Agenten eine Rolle zu."""
        if role_name not in self.roles:
            raise ValueError(f"Role {role_name} not found")
        
        if agent not in self.agent_roles:
            self.agent_roles[agent] = set()
        
        self.agent_roles[agent].add(role_name)
    
    def revoke_role(self, agent: str, role_name: str):
        """Entfernt eine Rolle von einem Agenten."""
        if agent in self.agent_roles:
            self.agent_roles[agent].discard(role_name)
    
    def get_agent_permissions(self, agent: str) -> Set[Permission]:
        """Gibt alle Berechtigungen eines Agenten zurück (aggregiert über alle Rollen)."""
        permissions = set()
        for role_name in self.agent_roles.get(agent, set()):
            role = self.roles.get(role_name)
            if role:
                permissions.update(role.permissions)
        return permissions
    
    def authorize(self, request: RBACRequest) -> RBACResponse:
        """
        Autorisiert eine Anfrage.
        
        Dies ist die Kernmethode der RBAC-Engine.
        """
        # Hole Agenten-Berechtigungen
        agent_permissions = self.get_agent_permissions(request.requesting_agent)
        
        # Prüfe, ob die Berechtigung vorhanden ist
        if request.action not in agent_permissions:
            return RBACResponse(
                allowed=False,
                reason=f"Agent {request.requesting_agent} does not have permission {request.action.value}",
                evaluated_at=time.time()
            )
        
        # Resource-spezifische Prüfungen
        if request.action == Permission.READ_FILES or request.action == Permission.WRITE_FILES:
            # Prüfe, ob der Pfad erlaubt ist
            if not self._check_path_access(request.requesting_agent, request.action, request.context.get("path", "")):
                return RBACResponse(
                    allowed=False,
                    reason=f"Path {request.context.get('path')} not accessible for {request.action.value}",
                    evaluated_at=time.time()
                )
        
        # Prüfe auf Zeitrahmen (optional)
        if not self._check_time_constraints(request):
            return RBACResponse(
                allowed=False,
                reason="Request outside allowed time window",
                evaluated_at=time.time()
            )
        
        return RBACResponse(
            allowed=True,
            reason=f"Permission {request.action.value} granted to {request.requesting_agent}",
            evaluated_at=time.time()
        )
    
    def _check_path_access(self, agent: str, action: Permission, path: str) -> bool:
        """
        Prüft Pfad-baiserte Berechtigungen.
        Erweitere dies für granulare Path-Permissions.
        """
        # Für Builder: nur /workspace/builder und /workspace/common
        if agent == "builder":
            allowed_paths = ["/workspace/builder", "/workspace/common", "/tmp"]
            return any(path.startswith(p) for p in allowed_paths)
        
        # Für Data Manager: nur /workspace/memory und /workspace/data
        if agent == "data":
            allowed_paths = ["/workspace/memory", "/workspace/data"]
            return any(path.startswith(p) for p in allowed_paths)
        
        # CEO darf alles lesen
        if action == Permission.READ_FILES:
            return True
        
        return False
    
    def _check_time_constraints(self, request: RBACRequest) -> bool:
        """
        Prüft Zeit-basierte Constraints.
        Für kritische Operationen könnte man Zeitfenster definieren.
        """
        # Vereinfacht: Erlaube alles
        return True
```

### 4. RBAC in der Agent-Kommunikation

```python
class SecureAgentChannel:
    """
    Ein sicherer Kommunikationskanal zwischen Agenten mit RBAC.
    """
    
    def __init__(self, rbac_engine: RBACEngine):
        self.rbac = rbac_engine
    
    def send_message(self, from_agent: str, to_agent: str, message: dict, 
                    action: Permission = Permission.SEND_TO_AGENT) -> bool:
        """
        Sendet eine sichere Nachricht zwischen Agenten.
        """
        # Prüfe, ob der Sender die Berechtigung hat
        request = RBACRequest(
            requesting_agent=from_agent,
            target_resource=f"agent:{to_agent}",
            action=action,
            context={"to": to_agent, "message_type": message.get("type")},
            timestamp=time.time()
        )
        
        response = self.rbac.authorize(request)
        if not response.allowed:
            log_security_event("RBAC_DENIED", {
                "from": from_agent,
                "to": to_agent,
                "reason": response.reason
            })
            return False
        
        # Nachricht senden (hier vereinfacht)
        log_inter_agent_message(from_agent, to_agent, message)
        return True
    
    def request_action(self, from_agent: str, target_agent: str, 
                       action: Permission, resource: dict) -> bool:
        """
        Ein Agent fordert einen anderen auf, eine Aktion auszuführen.
        """
        # Erst: Prüfe ob der anfordernde Agent das darf
        request = RBACRequest(
            requesting_agent=from_agent,
            target_resource=f"action:{action.value}",
            action=Permission.DELEGATE_TASK,
            context={"target": target_agent, "action": action.value, "resource": resource},
            timestamp=time.time()
        )
        
        response = self.rbac.authorize(request)
        if not response.allowed:
            log_security_event("ACTION_DENIED", {
                "from": from_agent,
                "target": target_agent,
                "action": action.value,
                "reason": response.reason
            })
            return False
        
        # Dann: Prüfe ob der Zielagent die Aktion ausführen darf
        target_request = RBACRequest(
            requesting_agent=target_agent,
            target_resource=resource.get("path", resource.get("name", "unknown")),
            action=action,
            context=resource,
            timestamp=time.time()
        )
        
        target_response = self.rbac.authorize(target_request)
        if not target_response.allowed:
            log_security_event("TARGET_DENIED", {
                "from": from_agent,
                "target": target_agent,
                "action": action.value,
                "reason": target_response.reason
            })
            return False
        
        return True
```

---

## 🧪 Praktische Übungen

### Übung 1: RBAC-Design

Entwirf ein RBAC-System für folgendes Szenario:

Ein AI-System besteht aus:
- **Orchestrator:** Koordiniert alle anderen Agenten
- **WebSearcher:** Sucht im Internet
- **CodeWriter:** Schreibt und bearbeitet Code
- **FileManager:** Verwaltet Dateien
- **DatabaseQuerier:** Fragt Datenbanken ab

**Aufgaben:**
1. Definiere mindestens 5 Rollen mit sinnvollen Permissions
2. Ordne jeden Agenten einer Rolle zu
3. Implementiere die Rollen in Python mit dem Framework aus dieser Lektion
4. Teste mindestens 5 Szenarien mit der RBAC-Engine

### Übung 2: RBAC-Audit

Bei einem Security-Audit fallen folgende Probleme auf:

1. Der WebSearcher hat DELETE_FILES Permission
2. Der DatabaseQuerier kann Code ausführen
3. Der CodeWriter kann auf Secrets zugreifen
4. Es gibt keine Zeit-basierten Einschränkungen

**Aufgaben:**
1. Erkläre für jedes Problem, welches Least-Privilege-Prinzip verletzt wird
2. Schlage Korrekturen vor
3. Implementiere die Fixes

---

## 📚 Zusammenfassung

RBAC ist das Fundament für sichere Multi-Agent-Systeme. Ohne strukturiertes Permission-Management entsteht Chaos — und Sicherheitslücken.

Die wichtigsten Principles:
1. **Least Privilege** — Jeder Agent bekommt nur die Permissions, die er wirklich braucht
2. **Role Aggregation** — Agenten können mehrere Rollen haben
3. **Defense in Depth** — RBAC ist eine Schicht, nicht die einzige Sicherheitsmaßnahme
4. **Audit Everything** — Alle RBAC-Entscheidungen werden geloggt

Im nächsten Kapitel werden wir uns mit der Implementierung sicherer Nachrichtenkanäle beschäftigen.

---

## 🔗 Weiterführende Links

- NIST RBAC Standard
- OWASP RBAC Cheat Sheet
- Zero Trust Network Architecture

---

## ❓ Fragen zur Selbstüberprüfung

1. Erkläre den Unterschied zwischen Role und Permission.
2. Warum ist es wichtig, dass RBAC entscheidungen geloggt werden?
3. Wie würdest du RBAC implementieren, wenn Agenten dynamisch erstellt werden?

---

---

## 🎯 Selbsttest — Modul 4.2

**Prüfe dein Verständnis!**

### Frage 1: Role vs. Permission
> Erkläre den Unterschied zwischen Role und Permission.

<details>
<summary>💡 Lösung</summary>

**Antwort:** Eine **Permission** (Berechtigung) ist eine spezifische Aktion, die erlaubt oder verboten ist — z.B. `READ_FILES`, `EXECUTE_CODE`, `DELETE_MEMORY`. Eine **Role** (Rolle) ist eine SAMMLUNG von Permissions, die einem logischen Aufgabenbereich zugeordnet wird — z.B. die Rolle "BUILDER"包含 `READ_FILES`, `WRITE_FILES`, `EXECUTE_CODE`, aber NICHT `ACCESS_SECRETS`. Agenten werden Rollen zugewiesen, nicht einzelne Permissions.
</details>

### Frage 2: RBAC Logging
> Warum ist es wichtig, dass RBAC-Entscheidungen geloggt werden?

<details>
<summary>💡 Lösung</summary>

**Antwort:** RBAC-Logs sind essentiell für: **1) Incident Response** — Bei einem Sicherheitsvorfall kann man rekonstruieren, wer welche Aktionen durchgeführt hat; **2) Compliance** — Regulatorische Anforderungen (DSGVO, SOX etc.) erfordern oft Nachweisbarkeit; **3) Anomalie-Erkennung** — Ungewöhnliche Zugriffsmuster werden erst durch Logs sichtbar; **4) Audit** — Security-Auditors müssen nachweisen können, dass das RBAC-System korrekt funktioniert.
</details>

### Frage 3: Dynamic RBAC für Agenten
> Wie würdest du RBAC implementieren, wenn Agenten dynamisch erstellt werden?

<details>
<summary>💡 Lösung</summary>

**Antwort:** Für dynamische Agenten: **1)** Vordefinierte Role-Templates nutzen (ROLE_BUILDER, ROLE_SECURITY etc.); **2)** Bei Agent-Erstellung muss eine Rolle explizit zugewiesen werden (kein Agent ohne Rolle); **3)** Ein "default-deny" für neue Agents — nur lesende Rechte, bis explizit mehr gewährt; **4)** Ein Security-Audit für jeden neuen Agenten-Typ; **5)** RBAC-Engine muss `register_role()` und `assign_role()` auch zur Laufzeit unterstützen.
</details>

*Lektion 4.2 — Ende*
---

## 🎯 Selbsttest — Modul 4.2

**Prüfe dein Verständnis!**

### Frage 1: Was bedeutet RBAC und wie unterscheidet es sich von traditioneller Access Control?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Role-Based Access Control vergibt Rechte an Rollen statt an Individuen. Für Agents bedeutet das: statt einzelne Agents zu berechtigen, definiert man Rollen (CEO, Builder, Security) und weist Rechte an Rollen zu.
</details>

### Frage 2: Was ist das Principle of Least Privilege?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Jeder Agent/User erhält nur die minimalen Rechte die nötig sind um seine spezifische Aufgabe zu erledigen. Keine überflüssigen Permissions.
</details>

