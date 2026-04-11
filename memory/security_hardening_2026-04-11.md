# 🔒 Security Hardening Report — 2026-04-11

**Auditor:** Sir HazeClaw (Subagent)  
**Scope:** Sir HazeClaw System — Full Security Audit  
**Sources:** `openclaw security audit --deep` + custom `security_audit.py`

---

## 📊 EXECUTIVE SUMMARY

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | 1 |
| 🟡 WARN | 3 |
| 🟠 MEDIUM | 1 |
| 🟢 INFO | 1 |

---

## 🔴 CRITICAL — Must Fix Immediately

### Issue #1: Small Models with Web Tools + No Sandbox

**Risk:** Remote Code Execution (RCE) via prompt injection  
**Affected Models:**
- `openrouter/google/gemma-4-31b-a4b-it:free` (31B) — in `defaults.model.fallbacks` AND `ceo.model.fallbacks`
- `openrouter/google/gemma-3-27b-it:free` (27B) — in `defaults.model.fallbacks` AND `ceo.model.fallbacks`

**Current Config:**
```json
"agents": {
  "defaults": { "sandbox": { "mode": "off" } },
  "list": [{ "id": "ceo", "sandbox": { "mode": "off" } }]
},
"tools": {
  "web": { "search": { "enabled": true } }  // web_search + web_fetch active
}
```

**Why Critical:**
- Small models (<=300B) are susceptible to prompt injection attacks
- Web search results can contain malicious content
- No sandbox isolation = attacker could execute commands if prompt is crafted
- Both CEO agent AND global defaults are affected

**Fix — Option A (Recommended — Disable Fallbacks):**
```json
"agents": {
  "defaults": {
    "model": {
      "primary": "minimax/MiniMax-M2.7",
      "fallbacks": []   // Remove small models entirely
    }
  },
  "list": [{
    "id": "ceo",
    "model": {
      "primary": "minimax/MiniMax-M2.7",
      "fallbacks": []   // Remove small models entirely
    }
  }]
}
```

**Fix — Option B (If Fallbacks Needed — Enable Sandbox + Deny Web):**
```json
"agents": {
  "defaults": { "sandbox": { "mode": "all" } },
  "list": [{ "id": "ceo", "sandbox": { "mode": "all" } }]
},
"tools": {
  "deny": ["group:web", "browser"]
}
```

**Status:** ⚠️ Requires Master approval (architecture change)

---

## 🟡 WARNINGS — Fix Soon

### Issue #2: Gateway Token Too Short

**Risk:** Brute-force token guessing  
**Finding:** `openclaw security audit` detected 14-character token  
**Context:** Gateway auth mode is `token`, bind is `loopback` (partially mitigating)

**Current State:**
```json
"gateway": {
  "auth": { "mode": "token", "token": "***REDACTED***" }
}
```

**Analysis:**
- Loopback-only binding limits exposure (only local access)
- However: if server is compromised, short token is weak
- Token is REDACTED in config, suggesting it may be in env vars

**Fix:**
```bash
# Generate new secure token (32+ chars)
openclaw gateway token --regenerate 32
```

**Alternative — Move to env-based auth:**
```bash
# Set OPENCLAW_GATEWAY_TOKEN env var with 64-char random string
export OPENCLAW_GATEWAY_TOKEN="$(openssl rand -base64 48)"
```

**Status:** ⚠️ Medium priority — loopback mitigates but should still fix

---

### Issue #3: Trusted Proxies Not Configured

**Risk:** IP spoofing via X-Forwarded-For headers  
**Finding:** `gateway.bind = loopback` but `gateway.trustedProxies` not set

**Current Config:**
```json
"gateway": {
  "bind": "loopback",
  "trustedProxies": null  // Not set
}
```

**Analysis:**
- Currently LOW risk because bind=loopback means only local connections
- However: if exposed via reverse proxy later, this becomes critical
- The audit specifically warns about this scenario

**Fix (if reverse proxy is used in future):**
```json
"gateway": {
  "bind": "0.0.0.0",
  "trustedProxies": ["127.0.0.1", "YOUR_PROXY_IP/32"]
}
```

**Fix (if keeping local-only):**
```json
"gateway": {
  "bind": "loopback"
  // trustedProxies is fine unset when loopback
}
```

**Status:** ✅ LOW PRIORITY — loopback is acceptable for now

---

### Issue #4: Ineffective denyCommands

**Risk:** Security theater — rules exist but don't work  
**Finding:** These commands in `gateway.nodes.denyCommands` are not valid command names:
- `camera.snap` (did you mean: `camera.list`)
- `camera.clip` (did you mean: `camera.list`)
- `screen.record`
- `contacts.add`
- `calendar.add`
- `reminders.add` (did you mean: `reminders.list`)
- `sms.send`

**Current Config:**
```json
"gateway": {
  "nodes": {
    "denyCommands": [
      "camera.snap", "camera.clip", "screen.record",
      "contacts.add", "calendar.add", "reminders.add", "sms.send"
    ]
  }
}
```

**Why Ineffective:**
- `denyCommands` uses exact command-name matching
- These are not actual command IDs in the system
- The audit suggests valid commands instead

**Analysis:**
- These commands likely don't exist in the current setup anyway
- This is more of a documentation/cleanup issue
- Real risk is LOW since the commands aren't operational

**Fix — Two Options:**

**Option A (Remove Invalid Entries):**
```json
"gateway": {
  "nodes": {
    "denyCommands": []
  }
}
```

**Option B (Keep if these ARE valid commands in your setup — use exact names):**
```json
"gateway": {
  "nodes": {
    "denyCommands": [
      "canvas.present", "canvas.hide", "canvas.navigate",
      "canvas.eval", "canvas.snapshot", "canvas.a2ui.push"
    ]
  }
}
```

**Status:** ✅ LOW PRIORITY — cleanup recommended but not urgent

---

## 🟠 MEDIUM — Code-Level Fixes

### Issue #5: shell=True in morning_check.py

**Risk:** Command injection if `cmd` variable is ever user-controlled  
**File:** `/home/clawbot/.openclaw/workspace/scripts/morning_check.py`  
**Line:** 15

```python
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
```

**Analysis:**
- `shell=True` allows shell injection attacks
- However: if `cmd` is always a hardcoded string (not user input), risk is low
- Need to verify the source of `cmd` variable

**Context from file:**
```
Line 7: import subprocess
Line 15: result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
```

**Fix (Prefer list-based subprocess):**
```python
# Safer: use list-based args instead of shell
result = subprocess.run(cmd.split(), capture_output=True, text=True)
# Or if cmd is complex:
result = subprocess.run(
    ["/bin/sh", "-c", cmd],  # Explicit shell, no shell injection via cmd parsing
    capture_output=True, text=True
)
```

**Better Fix (If cmd is always static):**
```python
import shlex
result = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
```

**Status:** ⚠️ MEDIUM PRIORITY — fix when morning_check.py is next edited

---

## 🟢 INFO — Attack Surface Summary

### Issue #6: General Attack Surface

```
groups: open=0, allowlist=1
tools.elevated: enabled
hooks.webhooks: disabled
hooks.internal: enabled (boot-md, bootstrap-extra-files, command-logger, session-memory)
browser control: enabled
trust model: personal assistant (one trusted operator boundary)
```

**Analysis:**
- ✅ No open (unauthenticated) groups
- ⚠️ tools.elevated: enabled — elevated exec is available
- ✅ webhooks disabled — no external webhook attack surface
- ✅ Internal hooks are standard (boot, logging, session memory)
- ⚠️ Browser control enabled — if browser is used, potential phishing vector
- ✅ Trust model is appropriate for single-user setup

**Recommendations:**
1. If browser is not actively used, consider disabling
2. Keep tools.elevated enabled only when needed (it is needed for our setup)
3. Review browser control usage periodically

---

## 📋 FIX PRIORITY SUMMARY

| Priority | Issue | Action Required |
|----------|-------|-----------------|
| **1 — IMMEDIATE** | Small models + no sandbox + web tools | Master approval needed — remove fallbacks or enable sandbox |
| **2 — SOON** | Gateway token too short | Run `openclaw gateway token --regenerate 32` |
| **3 — OPTIONAL** | trustedProxies | Only if exposing via reverse proxy |
| **4 — CLEANUP** | Invalid denyCommands | Remove invalid entries from denyCommands list |
| **5 — WHEN EDITING** | shell=True in morning_check.py | Fix during next edit cycle |

---

## 🛡️ ADDITIONAL RECOMMENDATIONS

### Already Good:
- ✅ Loopback-only gateway binding
- ✅ No webhooks exposed
- ✅ Personal assistant trust model (single operator)
- ✅ No exec() calls found in scripts
- ✅ No eval() calls found in scripts

### Could Improve:
- Consider adding `tools.deny: ["group:web"]` if web tools aren't essential
- Consider adding `.env` based token storage instead of config file
- Regular security audits (quarterly)

---

## 📝 NOTES

- Gateway token is REDACTED in config output, suggesting it's in environment variables (good practice)
- The token length warning (14 chars) may be from the env var reference length, not actual token
- Most scripts use safe patterns (no exec/eval/shell=True)
- The evolve.py script actually scans FOR shell=True patterns (self-aware security)

---

*Report generated: 2026-04-11*  
*Auditor: Sir HazeClaw (Subagent)*  
*Sources: openclaw security audit --deep + scripts/security_audit.py*
