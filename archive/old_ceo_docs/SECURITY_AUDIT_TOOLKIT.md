# SECURITY AUDIT TOOLKIT — Learnings von security-audit-toolkit

**ClawHub Skill:** security-audit-toolkit
**Security Status:** CLEAN (aber Warnings vorhanden)
**License:** MIT-0
**Hinweis:** Wir lernen davon — nicht installieren, nur Pattern übernehmen.

---

## 🎯 WAS WIR LERNEN KÖNNEN

### 1. Dependency Scanning Commands

```bash
# Node.js
npm audit --audit-level=high

# Python
pip install pip-audit
pip-audit

# Go
go install golang.org/x/vuln/cmd/govulncheck@latest
govulncheck ./..

# Universal (beste Option!)
trivy fs .  # Dateisystem scannen
trivy fs --scanners vuln --severity HIGH,CRITICAL .
```

### 2. Secret Detection Patterns

```bash
# AWS Keys
grep -rn 'AKIA[0-9A-Z]\{16\}' --include='*.{js,py,go,env,yml,json}'

# Generic API Keys
grep -rn -i 'api[_-]?key\|api[_-]?secret\|access[_-]?token' --include='*.{js,py,go,env}'

# Private Keys
grep -rn 'BEGIN.*PRIVATE KEY' .

# JWT Tokens
grep -rn 'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.' --include='*.{js,py,log,json}'

# Passwords in Config
grep -rn -i 'password\s*[:=]' --include='*.{env,yml,yaml,json}'
```

### 3. OWASP Top 10 Patterns

#### Injection Detection
```bash
# SQL Injection (string concatenation in queries)
grep -rn "query\|execute\|cursor" --include='*.{py,js,go}' . | \
  grep -i "f\"\|format(\|%s\|\${{" | \
  grep -iv "parameterized\|placeholder"
```

#### XSS Patterns
```bash
# Dangerous DOM operations
grep -rn "innerHTML\|dangerouslySetInnerHTML\|v-html" --include='*.{js,html}'

# eval with user input
grep -rn "eval(\|new Function(\|setTimeout.*string" --include='*.js'
```

#### Command Injection
```bash
grep -rn "exec(\|spawn(\|system(\|popen(\|subprocess\|os\.system" --include='*.{py,js,go}'
```

### 4. SSL/TLS Verification

```bash
# Certificate prüfen
openssl s_client -connect example.com:443 -servername example.com < /dev/null 2>/dev/null | \
  openssl x509 -noout -subject -dates

# SSL Bypass detection
grep -rn "verify\s*=\s*False\|rejectUnauthorized.*false\|InsecureSkipVerify" \
  --include='*.{py,js,yml}'
```

### 5. File Permission Audit

```bash
# World-writable files finden
find . -type f -perm -o=w -not -path '*/node_modules/*' -not -path '*/.git/*'

# SUID/SGID bits
find / -type f \( -perm -4000 -o -perm -2000 \) 2>/dev/null

# SSH permissions (sollte 700 für ~/.ssh sein)
ls -la ~/.ssh/
```

---

## 🛠️ WAS WIR NACHBAUEN KÖNNEN

### security-audit.sh — Unser eigenes Audit Script

```bash
#!/bin/bash
# Sir HazeClaw Security Audit Script
# Basierend auf security-audit-toolkit Pattern

PROJECT_DIR="${1:-/home/clawbot/.openclaw/workspace}"

echo "========================================="
echo "Sir HazeClaw Security Audit"
echo "========================================="

ISSUES=0

# 1. Secret Detection
echo "[1] Secret Detection..."
grep -rn 'AKIA[0-9A-Z]\{16\}' "$PROJECT_DIR" 2>/dev/null && ISSUES=$((ISSUES+1))
grep -rn 'BEGIN.*PRIVATE KEY' "$PROJECT_DIR" 2>/dev/null && ISSUES=$((ISSUES+1))
grep -rn 'sk-[A-Za-z0-9]\{20,\}' "$PROJECT_DIR" 2>/dev/null && ISSUES=$((ISSUES+1))

# 2. Dependency Audit
echo "[2] Dependency Audit..."
cd "$PROJECT_DIR"
[ -f package.json ] && npm audit --audit-level=high 2>/dev/null
[ -f requirements.txt ] && pip-audit 2>/dev/null

# 3. File Permissions
echo "[3] File Permissions..."
find "$PROJECT_DIR" -type f -perm -o=w 2>/dev/null | head -5 && ISSUES=$((ISSUES+1))

# 4. SSL Bypass Detection
echo "[4] SSL Verification..."
grep -rn "verify\s*=\s*False\|rejectUnauthorized.*false" "$PROJECT_DIR" 2>/dev/null && ISSUES=$((ISSUES+1))

echo ""
echo "========================================="
echo "Audit complete. Issues: $ISSUES"
echo "========================================="
```

---

## 📋 SECURITY CHECKLISTE

### Täglich (Auto)
- [ ] Crons laufen ohne Fehler
- [ ] Gateway stabil
- [ ] Disk Space OK

### Wöchentlich
- [ ] npm audit / pip-audit
- [ ] Secret Detection Pattern check
- [ ] File Permission check

### Monatlich
- [ ] Vollständiges Security Audit
- [ ] SSL Zertifikate prüfen
- [ ] Backup testen

---

## 🔍 WICHTIGE GREP PATTERNS (für uns)

```bash
# Findet alle API Keys
grep -rn 'api[_-]?key\|sk-\|token\|password' --include='*.{py,js,sh,env}' \
  /home/clawbot/.openclaw/workspace 2>/dev/null | \
  grep -v 'example\|test\|mock\|xxxx\|placeholder'

# Findet alle exec() calls (Command Injection Risk!)
grep -rn 'exec(\|spawn(\|system(\|subprocess' \
  /home/clawbot/.openclaw/workspace/scripts 2>/dev/null

# Findet alle eval() (XSS Risk!)
grep -rn 'eval(\|new Function(' \
  /home/clawbot/.openclaw/workspace/scripts 2>/dev/null
```

---

*Erlernt von: security-audit-toolkit (ClawHub) — 2026-04-10*
*Wir installieren NICHT — nur Pattern lernen + nachbauen*
