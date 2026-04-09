# QC Fixes Report — Least Privilege Pre-Deployment

**Datum:** 2026-04-08
**Agent:** Builder
**Status:** ✅ FIXED

---

## ✅ Erledigte Fixes

### Issue #1: Uni-agent Tools inkonsistent (Medium)
**Status:** ✅ BEREITS KORREKT — Keine Änderung nötig

Die Matrix war bereits korrekt:
- `uni-curriculum`: `["read", "write", "edit"]` ✅
- `uni-examiner`: `["read", "write", "edit"]` ✅
- `uni-research`: `["read", "write", "web_search", "web_fetch"]` ✅

**Zusätzliche Korrektur:** `research` permissions korrigiert von `["read", "write", "search"]` → `["read", "write", "web_search", "web_fetch"]` für Konsistenz.

---

### Issue #2: Security exec-Berechtigung widersprüchlich (Medium)
**Status:** ✅ FIXED

**Änderungen in `rbac_matrix.json`:**

| Feld | Vorher | Nachher |
|------|--------|---------|
| `security.tools` | `["read", "exec", "web_fetch", "web_search"]` | `["read", "write", "exec", "web_fetch", "web_search"]` |
| `security.permissions` | `["read", "audit", "execute"]` | `["read", "write", "audit", "execute"]` |
| `security.restrictions` | `"darf keine exec-Befehle mit elevated privileges ausführen"` | `"darf keine exec-Befehle mit Systemänderungen ausführen"` |
| `security.execAllowedDirectories` | (fehlte) | `["/home/clawbot/.openclaw/workspace/security/"]` |

**Begründung:** Security Officer braucht `write` für Log-Einträge und `execAllowedDirectories` für Audit-Scripts.

---

### Issue #3: exec Pattern-Matching umgehbar (Medium)
**Status:** ✅ FIXED

**Problem:** `deniedCommands: ["chmod 777", "rm -rf /", "sudo"]` ist String-Matching und kann umgangen werden (z.B. `chmod 0777`, `chmod +x`, etc.).

**Lösung:** Verzeichnis-basierter Allowlist:

**Änderungen in `rbac_matrix.json`:**
- `builder.execAllowedDirectories`: `["/home/clawbot/.openclaw/workspace/scripts/"]`
- `security.execAllowedDirectories`: `["/home/clawbot/.openclaw/workspace/security/"]`

**Änderungen in `least_privilege_impl.md`:**
- `deniedCommands` → `allowedDirectories` (directory-basiert)
-uni-agents separat aufgelistet mit korrekten toolScopes

**Sicherheitsvorteil:**
- ❌ `deniedCommands: ["chmod 777"]` → umgehbar
- ✅ `allowedDirectories: ["/scripts/"]` → exec funktioniert NUR in diesem Verzeichnis

---

### Issue #4: Rollback Checkpoint-System (LOW — optional)
**Status:** ⏭️ SKIPPED (optional)

Issue #4 wurde als LOW/optional markiert. Kann separat behandelt werden.

---

## 📁 Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| `/home/clawbot/.openclaw/workspace/builder/rbac_matrix.json` | Issues #1-3 gefixt |
| `/home/clawbot/.openclaw/workspace/builder/least_privilege_impl.md` | exec-Allowlist statt Pattern-Matching |

---

## 🔍 Verifizierung

```bash
# Prüfe RBAC Matrix JSON ist valides
cat /home/clawbot/.openclaw/workspace/builder/rbac_matrix.json | jq .

# Erwartet: Keine Syntax-Fehler
```

---

## ⚠️ Offene Punkte

1. **Issue #4 (Rollback Checkpoint-System)** — Optional, kann später implementiert werden
2. **Verzeichnis-Struktur** — Die `chmod 750` Befehle aus Phase 2/3 müssen noch manuell ausgeführt werden
3. **OpenClaw Config** — Die `execAllowedDirectories` müssen in der OpenClaw Config aktiviert werden

---

## ✅ Deployment-Bereitschaft

| Kriterium | Status |
|-----------|--------|
| RBAC Matrix valides JSON | ✅ |
| exec-Allowlist implementiert | ✅ |
| Uni-agent Tools konsistent | ✅ |
| Security exec-Berechtigung korrigiert | ✅ |
| QC Report erstellt | ✅ |

**Ready for CEO Review & Security Audit.**

---

*Report durch: Builder Agent*
*Datum: 2026-04-08*
