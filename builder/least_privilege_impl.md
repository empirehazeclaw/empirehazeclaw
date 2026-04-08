# Least Privilege Implementation Guide
**EmpireHazeClaw Fleet — RBAC Implementation**
*Erstellt: 2026-04-08 | Builder Agent*

---

## 📋 Übersicht

Dieses Dokument beschreibt die Implementierung von **Least Privilege** für die EmpireHazeClaw Flotte basierend auf der RBAC-Matrix in `rbac_matrix.json`.

---

## 🎯 Ziel

Jeder Agent erhält nur die **minimal notwendigen Rechte**:
- ❌ NICHT alle Agents haben vollen Zugriff
- ✅ Jeder Agent hat nur Zugriff auf seinen Workspace + notwendige Ressourcen
- ✅ Security Officer hat Lese-Zugriff auf alle Logs

---

## 📁 Phase 1: Verzeichnis-Rechte ändern

### Aktuelle Situation
Alle Workspaces sind unter `/home/clawbot/.openclaw/workspace/` mit `drwxr-xr-x` (755) Rechten — alle Agents können alles lesen.

### Neue Verzeichnis-Struktur

```bash
# Workspace-Verzeichnisse
ceo/           → clawbot:clawbot 750 (nur ceo + gruppe)
security/      → clawbot:clawbot 750 (nur security + gruppe)  
data/          → clawbot:clawbot 750 (nur data + gruppe)
builder/       → clawbot:clawbot 750 (nur builder + gruppe)
qc/            → clawbot:clawbot 750 (nur qc + gruppe)
research/      → clawbot:clawbot 750 (nur research + gruppe)
uni-*/         → clawbot:clawbot 750 (nur jeweiliger uni-agent + gruppe)

# Spezielle Verzeichnisse mit Zugriff
logs/          → clawbot:clawbot 750 (ceo + security lesen)
memory/        → clawbot:clawbot 750 (ceo + data lesen/schreiben)
scripts/       → clawbot:clawbot 750 (ceo + builder lesen)
skills/        → clawbot:clawbot 750 (ceo + builder lesen)
```

### Befehle zur Umsetzung

```bash
# 1. Haupt-Workspace Verzeichnis-Rechte
chmod 750 /home/clawbot/.openclaw/workspace/{ceo,security,data,builder,qc,research}
chmod 750 /home/clawbot/.openclaw/workspace/uni-*

# 2. Spezielle Verzeichnisse
chmod 750 /home/clawbot/.openclaw/workspace/logs      # CEO + Security
chmod 750 /home/clawbot/.openclaw/workspace/memory   # CEO + Data
chmod 750 /home/clawbot/.openclaw/workspace/scripts  # CEO + Builder
chmod 750 /home/clawbot/.openclaw/workspace/skills   # CEO + Builder

# 3. WICHTIG: openclaw-Verzeichnis selbst muss lesbar bleiben
chmod 755 /home/clawbot/.openclaw
```

---

## 🔧 Phase 2: OpenClaw Config Settings

### Tool-Scopes in der OpenClaw Config

Die OpenClaw Config muss Tool-Scopes pro Agent definieren:

```json
// Beispiel: agent_config.json
{
  "agents": {
    "ceo": {
      "toolScopes": ["*"],
      "workspaceAccess": ["ceo", "uni-*", "logs", "memory", "scripts", "skills"]
    },
    "security": {
      "toolScopes": ["read", "write", "exec", "web_fetch", "web_search"],
      "workspaceAccess": ["security", "logs", "memory"],
      "execAllowedDirectories": ["/home/clawbot/.openclaw/workspace/security/"]
    },
    "data": {
      "toolScopes": ["read", "write", "edit", "exec", "memory_*"],
      "workspaceAccess": ["data", "memory"]
    },
    "builder": {
      "toolScopes": ["read", "write", "edit", "exec"],
      "workspaceAccess": ["builder", "scripts", "skills"],
      "execAllowedDirectories": ["/home/clawbot/.openclaw/workspace/scripts/"]
    },
    "qc": {
      "toolScopes": ["read", "write"],
      "workspaceAccess": ["qc", "memory"]
    },
    "research": {
      "toolScopes": ["read", "write", "web_search", "web_fetch"],
      "workspaceAccess": ["research"]
    },
    "uni-curriculum": {
      "toolScopes": ["read", "write", "edit"],
      "workspaceAccess": ["uni-curriculum"]
    },
    "uni-examiner": {
      "toolScopes": ["read", "write", "edit"],
      "workspaceAccess": ["uni-examiner"]
    },
    "uni-research": {
      "toolScopes": ["read", "write", "web_search", "web_fetch"],
      "workspaceAccess": ["uni-research"]
    }
  }
}
```

### Wo konfigurierbar (falls OpenClaw das unterstützt)

1. **openclaw config** → `/home/clawbot/.openclaw/config/`
2. **Agent-spezifische Configs** → `/home/clawbot/.openclaw/config/agents/`
3. **Tool-Restrictions** → `/home/clawbot/.openclaw/config/tool_scopes.json`

---

## 🛠️ Phase 3: Tool-Scope Einschränkungen

### exec Tool — Wichtigste Einschränkung (ALLOWLIST statt DENYLIST)

```bash
# WICHTIG: Pattern-Matching auf Strings ist umgehbar!
# Statt deniedCommands (容易被绕过 / easily bypassed)
# -> Verzeichnis-basierter Allowlist (SECURE)

# Beispiel: exec_config.json
{
  "exec": {
    "builder": {
      "allowedDirectories": ["/home/clawbot/.openclaw/workspace/scripts/"],
      "description": "Builder darf NUR Scripts in /scripts/ ausführen",
      "timeout": 60
    },
    "security": {
      "allowedDirectories": ["/home/clawbot/.openclaw/workspace/security/"],
      "description": "Security darf NUR Audit-Scripts in /security/ ausführen",
      "timeout": 30
    },
    "data": {
      "allowedDirectories": ["/home/clawbot/.openclaw/workspace/data/"],
      "description": "Data Manager darf NUR Scripts in /data/ ausführen",
      "timeout": 60
    }
  }
}
```

**Sicherheitsvorteil:**
- ❌ `deniedCommands: ["chmod 777"]` → kann umgangen werden mit `chmod 0777`, `chmod +x`, etc.
- ✅ `allowedDirectories: ["/scripts/"]` → exec funktioniert NUR in diesem Verzeichnis

### Andere Tool-Einschränkungen

| Tool | CEO | Security | Builder | Data | QC | Research |
|------|-----|----------|---------|------|----|----|
| read | ✅ | ✅ Logs only | ✅ Builder only | ✅ | ✅ | ✅ |
| write | ✅ | ❌ | ✅ Builder only | ✅ | ✅ | ✅ |
| edit | ✅ | ❌ | ✅ Builder only | ✅ | ❌ | ❌ |
| exec | ✅ | ✅ Read-only | ✅ Scripts only | ✅ Limited | ❌ | ❌ |
| web_search | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| web_fetch | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| message | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🚀 Phase 4: Konkrete Implementierungs-Schritte

### Schritt 1: Backup erstellen
```bash
sudo cp -r /home/clawbot/.openclaw/workspace /home/clawbot/.openclaw/workspace.backup.$(date +%Y%m%d)
```

### Schritt 2: Verzeichnis-Rechte anpassen
```bash
# Alle Workspace-Dirs auf 750 setzen
for dir in ceo security data builder qc research uni-curriculum uni-examiner uni-research; do
  chmod 750 /home/clawbot/.openclaw/workspace/$dir
done

# Spezielle Verzeichnisse
chmod 750 /home/clawbot/.openclaw/workspace/logs
chmod 750 /home/clawbot/.openclaw/workspace/memory
chmod 750 /home/clawbot/.openclaw/workspace/scripts
chmod 750 /home/clawbot/.openclaw/workspace/skills
```

### Schritt 3: OpenClaw Config prüfen/anpassen
```bash
# OpenClaw Config Location finden
find /home/clawbot/.openclaw -name "*.json" -type f | grep -i config

# Bestehende Configs anzeigen
cat /home/clawbot/.openclaw/config/agents.json 2>/dev/null || echo "No agents.json found"
```

### Schritt 4: RBAC Matrix deployen
```bash
# RBAC Matrix in Builder Workspace
cp /home/clawbot/.openclaw/workspace/builder/rbac_matrix.json \
   /home/clawbot/.openclaw/config/rbac_matrix.json
```

### Schritt 5: Test nach Änderungen
```bash
# Test: Kann Security Officer auf CEO-Workspace zugreifen? (Sollte fehlschlagen)
sudo -u clawbot -g clawbot ls /home/clawbot/.openclaw/workspace/ceo/

# Test: Kann Builder auf Security-Workspace schreiben? (Sollte fehlschlagen)
sudo -u clawbot -g clawbot touch /home/clawbot/.openclaw/workspace/security/test.txt
```

---

## ⚠️ Wichtige Hinweise

### Was NICHT geändert werden sollte
1. **exec NICHT komplett entziehen** — Builder braucht es für Script-Ausführung
2. **CEO behält Admin-Rechte** — Delegation muss funktionieren
3. **Security Officer braucht Lese-Zugriff auf alle Logs** — für Audits

### Vor dem Deployment
- [ ] Backup aller Workspaces erstellen
- [ ] In Test-Umgebung zuerst testen
- [ ] Sicherstellen dass CEO-Sessions nicht unterbrochen werden
- [ ] Rollback-Plan bereit haben

### Rollback bei Problemen
```bash
# Rollback zu Backup
sudo cp -r /home/clawbot/.openclaw/workspace.backup.20260408/* \
   /home/clawbot/.openclaw/workspace/

# Rechte zurücksetzen
chmod -R 755 /home/clawbot/.openclaw/workspace/*
```

---

## 📊 RBAC Matrix Referenz

Die vollständige RBAC-Matrix liegt in:
`/home/clawbot/.openclaw/workspace/builder/rbac_matrix.json`

---

*Implementierung durch: Builder Agent*
*Status: Bereit für CEO Review & Security Audit*
*Datum: 2026-04-08*
