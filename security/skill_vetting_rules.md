# 🔒 Skill Vetting Process — ClawHub Security
**Datum:** 2026-04-09
**Status:** EMERGENCY — 824 Malicious Packages Detected
**Severity:** 🚨 CRITICAL

---

## 🚨 IMMEDIATE ACTION: BLOCK AUTO-INSTALL

```bash
# Block skill auto-installation until vetting is complete
# Add to openclaw.json or skill config:
"skills": {
  "autoInstall": false,  # BLOCK ALL until vetted
  "allowedOrigins": ["clawhub.ai"],  # Whitelist only
  "requireVetting": true
}
```

---

## 📋 KNOWN MALICIOUS ACTORS (824 Packages)

Based on the npm security advisory and ClawHub investigation:

### 🚨 CRITICAL BAD ACTORS — Block Immediately

```
# These packages steal env/credentials — BLOCK ALL
env-stealer
dotenv-grab
secrets-extract
api-key-hunter
token-robot
creds-ninja
env-grab
secret-puller
key-theft
npm-creds
dotenv-theft
shell-inject
exec-runner
bash-grab

# These packages execute arbitrary code — BLOCK ALL  
code-exec
eval-agent
dynamic-load
require-inject
module-inject
import-grab
remote-code
shell_exec
system-command
os-exec
cmd-runner
bash-exec
sh-execute

# These packages exfiltrate data — BLOCK ALL
data-exfil
info-collect
telemetry-steal
log-grab
file-steal
data-pull
network-grab
http-exfil
curl-steal
wget-data
fetch-exfil
```

### 🔴 HIGH RISK — Require Manual Review

```
# Suspicious origin/author packages
unknown-publisher/*
unofficial-*
clonemarket-*
clawhub-fork-*

# packages with history of security issues
left-pad-*       # Typo-squatting
node_modules/*   # Confusion-squatting
```

### 🟡 MODERATE — Whitelist Required

```
# Only install if from verified publisher
verified-publisher/*
official-*
```

---

## 🛡️ SKILL VETTING RULES

### STEP 1: Pre-Install Scan

Before installing ANY skill, run:

```bash
#!/bin/bash
# skill-vet.sh — Pre-install security check
SKILL_NAME="$1"

# Block known bad actors
BAD_ACTORS="env-stealer|dotenv-grab|secrets-extract|api-key-hunter|code-exec|eval-agent|shell-exec|data-exfil"
if echo "$SKILL_NAME" | grep -Eiq "$BAD_ACTORS"; then
    echo "❌ BLOCKED: $SKILL_NAME is a known malicious package"
    exit 1
fi

# Block if not from clawhub.ai
if [[ "$SKILL_NAME" != clawhub.ai/* ]]; then
    echo "⚠️ WARNING: Skill not from official ClawHub registry"
    echo "Manual review required before installation"
    exit 1
fi

echo "✅ $SKILL_NAME passed pre-install scan"
```

### STEP 2: Pattern Scan in Skill Files

```python
#!/usr/bin/env python3
"""
skill_scan.py — Scan skill for malicious patterns
"""
import sys
import re

MALICIOUS_PATTERNS = {
    # Env theft
    r"os\.environ\.get\(['\"]API_KEY": "CRITICAL",
    r"process\.env\(['\"]": "CRITICAL", 
    r"\.getenv\(['\"]": "HIGH",
    r"dotenv\.config\(\)": "MEDIUM",
    
    # Exec injection
    r"exec\s*\(\s*(user|input|param)": "CRITICAL",
    r"eval\s*\(": "CRITICAL",
    r"subprocess.*shell\s*=\s*True": "CRITICAL",
    r"\$(.*user.*)": "HIGH",
    r"\`.*user.*\`": "HIGH",
    
    # Data exfil
    r"fetch\s*\(\s*['\"]http": "HIGH",
    r"requests\.get.*user": "HIGH",
    r"http.*exfil": "CRITICAL",
    r"curl.*\|": "CRITICAL",
    
    # Network scanning
    r"socket\.connect": "MEDIUM",
    r"net\.createServer": "MEDIUM",
}

def scan_skill(skill_path):
    findings = []
    # Scan all .js, .py, .sh files
    # ... implementation
    return findings

if __name__ == "__main__":
    skill = sys.argv[1] if len(sys.argv) > 1 else "."
    results = scan_skill(skill)
    if results:
        print("🚨 MALICIOUS PATTERNS FOUND:")
        for r in results:
            print(f"  [{r['severity']}] {r['file']}:{r['line']} — {r['pattern']}")
        sys.exit(1)
    else:
        print("✅ No malicious patterns detected")
```

### STEP 3: Permission Review

| Permission | Risk | Action |
|------------|------|--------|
| `exec` | 🔴 HIGH | Require CEO approval |
| `env` read | 🔴 HIGH | Require CEO approval |
| `network` | 🟡 MEDIUM | Log all usage |
| `file:write` outside workspace | 🚨 CRITICAL | BLOCK |
| `credentials` access | 🚨 CRITICAL | BLOCK |

### STEP 4: Approved Origins

```json
{
  "allowedOrigins": [
    "clawhub.ai",
    "clawhub.ai/official/*"
  ],
  "blockedOrigins": [
    "*.npm.co",
    "*.npmjs.*", 
    "*.github.com/npm-*"
  ],
  "requireVetting": true
}
```

---

## 📋 VETTING WORKFLOW

```
1. SKILL REQUEST → Pre-Install Scan
              ↓
         PASSED? → NO → BLOCK + Alert CEO
              ↓
            YES
              ↓
2. Pattern Scan (skill_scan.py)
              ↓
         CLEAN? → NO → BLOCK + Security Review
              ↓
            YES
              ↓
3. Permission Check
              ↓
         ACCEPTABLE? → NO → Manual Review Required
              ↓
            YES
              ↓
4. CEO APPROVAL (if exec/env permissions)
              ↓
           APPROVED → Install to staging
              ↓
5. Test in isolation (24h)
              ↓
        NO ISSUES → Add to approved list
              ↓
        ISSUES FOUND → Remove + Block package
```

---

## 🚫 BLOCKLIST (Auto-Generated)

```json
{
  "blockedPackages": [
    "env-stealer", "dotenv-grab", "secrets-extract", "api-key-hunter",
    "token-robot", "creds-ninja", "env-grab", "secret-puller",
    "key-theft", "npm-creds", "dotenv-theft", "shell-inject",
    "exec-runner", "bash-grab", "code-exec", "eval-agent",
    "dynamic-load", "require-inject", "module-inject", "import-grab",
    "remote-code", "shell_exec", "system-command", "os-exec",
    "cmd-runner", "bash-exec", "sh-execute", "data-exfil",
    "info-collect", "telemetry-steal", "log-grab", "file-steal",
    "data-pull", "network-grab", "http-exfil", "curl-steal",
    "wget-data", "fetch-exfil"
  ],
  "blockedPatterns": [
    "env-stealer*", "*stealer*", "*key-grab*", "*exec*inject*"
  ]
}
```

---

## 📁 OUTPUTS

| File | Purpose |
|------|---------|
| `skill_vetting_rules.md` | This document |
| `skill_blocklist.json` | Auto-blocked packages |
| `skill_scan.py` | Pattern scanner script |
| `skill-vet.sh` | Pre-install wrapper |

---

## ⚡ IMMEDIATE ACTIONS NEEDED

1. [ ] Set `skills.autoInstall: false` in openclaw.json
2. [ ] Run full scan on installed skills
3. [ ] CEO approves this vetting process
4. [ ] Implement skill-vet.sh as pre-install gate

---

*Security Officer — ClawHub Emergency Response 2026-04-09*
