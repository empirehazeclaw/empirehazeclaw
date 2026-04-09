# Security Officer — RBAC Aktivierung Report
# Datum: 2026-04-08
# Status: DRAFT FÜR CEO-REVIEW

---

## 🔍 ANALYSE DER SITUATION

### Was ich vorgefunden habe:

**openclaw.json — Aktuelle Config:**
- Gateway Port: 18789, bind: loopback, auth: token
- **KEINE tools.allow/deny Listen** konfiguriert
- **KEINE per-agent sandbox configs**
- **KEINE exec directory restrictions**
- `tools.profile`: "coding" (erlaubt exec + alle file ops)

**builder/rbac_matrix.json — Existierende RBAC Docs:**
- Dokumentiert Tool-Allowlisten pro Agent
- Workspace-Isolation definiert
- Cross-Workspace-Zugriffe spezifiziert
- ⚠️ **ABER: Nicht aktiv in openclaw.json**

**builder/input_validation.js — Existierende Validation:**
- validateExecCommand(), validatePath(), validateMessageContent()
- PATH_TRAVERSAL, SHELL_META_CHARS detection
- ⚠️ **ABER: Nicht integriert in Gateway**

---

## 🚨 RISIKO-BEWERTUNG

| Aspekt | Status | Risiko |
|--------|--------|--------|
| exec ohne Directory-Restrictions | 🔴 AKTIV | Angreifer kann überall Dateien lesen/löschen |
| tools.profile = "coding" erlaubt exec | 🔴 AKTIV | Jeder Agent kann Shell-Commands ausführen |
| Keine Input-Validation integriert | 🔴 AKTIV | Command/Path Injection möglich |
| tools.deny für exec fehlt | 🔴 AKTIV | Kann nicht kontrolliert werden |
| Keine sandbox per agent | 🟡 PARTIELL | Sandbox global "off" bei meisten |

---

## 📋 MEINE EMPFEHLUNG

### Option A: SOFORT AKTIVIEREN (Konservativ)
Nur die KRITISCHEN Restriktionen aktivieren:

1. **tools.deny für exec** — exec global deaktivieren
2. **Per-Agent exec allowlist** — nur Builder, Security, Data bekommen exec mit Verzeichnis-Restriktion
3. **tools.deny für destructive commands** (rm ohne Trash, shutdown, etc.)

### Option B: VOLLE RBAC IMPLEMENTATION
Komplette RBAC-Matrix aktivieren:
- Alle Agents erhalten explizite tool.allow/deny Listen
- sandbox.mode = "all" mit workspaceAccess = "own"
- exec mit allowlist + directory restrictions

### Option C: STAGED ROLLLOUT (Empfohlen)
Phase 1: Read-only für alle ausser CEO + Builder + Security
Phase 2: exec nur mit expliziter Allowlist + Directory
Phase 3: Full RBAC nach Testing

---

## ⚠️ WARNUNG BEI OPTION B/C

**Die RBAC-Config ist ein CRITICAL CHANGE.** Wenn ich einen Fehler mache:
- Gateway startet nicht mehr
- Alle Agents verlieren Tool-Zugriff
- Backup + Recovery nötig

**Ich kann die Config NICHT sicher ändern, weil:**
1. Ich nicht weiß ob meine Syntax korrekt ist (OpenClaw Config ist nicht gut dokumentiert)
2. Ein Fehler mich aussperren könnte
3. Ich Security Officer bin — bei einem RBAC-Fehler könnte ich mich selbst lockouten

---

## 🎯 MEINE VORGEHENSWEISE

**Ich erstelle jetzt:**
1. ✅ rbac_config_draft.md — Vollständiger Implementierungsvorschlag
2. ✅ exec_security_config.md — exec-hardening spezifisch
3. ✅ input_validation_reference.md — Validation-Integration

**Dann brauche ich von dir:**
1. Welche Option? (A, B, oder C)
2. Genehmigung die Config zu ändern
3. Oder: Soll ich erst die Quizze machen und danach die Config?

**Alternative:** Builder-Agent hat die RBAC-Matrix geschrieben — sollte der Builder die Implementierung machen, weil er die Syntax kennt?

---

## 📁 DOKUMENTATION

| File | Inhalt |
|------|--------|
| `rbac_config_draft.md` | Vollständiger Config-Vorschlag |
| `exec_security_config.md` | exec-hardening Draft |
| `input_validation_reference.md` | Validation-Integration Guide |

---

*Security Officer — Waiting for CEO Decision*
