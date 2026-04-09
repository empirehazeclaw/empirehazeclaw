# Approval Workflows Specification

**Version:** 1.0.0  
**Date:** 2026-04-08  
**Audit Reference:** Security Audit #4  

---

## 🎯 Purpose

Establish a mandatory approval system for critical actions to prevent accidental or malicious damage.

---

## 🔒 Action Categories

### Category 1: DESTRUCTION (Immediate Block)

**Actions that are COMPLETELY BLOCKED without any approval path:**

| Pattern | Description |
|---------|-------------|
| `rm -rf` | Recursive force delete anywhere |
| `rm -rf /` | Root deletion |
| `chmod 777` | World-readable/writable on system paths |
| `sudo su` / `su -` | Privilege escalation to root |
| `dd` commands | Direct block device operations |
| DELETE on system dirs | Removing /etc, /usr, /var, /boot, /sys |

**Behavior:** Action is rejected, logged, and Nico is immediately notified.

---

### Category 2: ELEVATED (Pre-Execution Approval Required)

**Actions requiring explicit human approval BEFORE execution:**

| Action | Examples |
|--------|----------|
| exec with system changes | `chmod`, `chown`, `apt-get install`, `systemctl stop` |
| Gateway config changes | Modifying `/home/clawbot/.openclaw/gateway/` config files |
| New Cron jobs | Creating/modifying crontab entries |
| API key changes | Modifying stored credentials |
| External messages | Sending to non-whitelisted Telegram IDs/channels |
| File writes to system paths | Writing to /etc, /usr (except user workspaces) |
| process exec with elevated | `exec` tool with `elevated: true` |

**Behavior:** Action is paused, approval request sent to Nico, execution waits for response.

---

### Category 3: MONITORING (Logged Only)

**Actions that are allowed but fully logged:**

| Action | Examples |
|--------|----------|
| Read operations | `read`, `cat`, `ls`, `grep` |
| Web search/fetch | `web_search`, `web_fetch` |
| Normal script execution | Scripts in user workspace without system access |
| Memory operations | `memory_search`, `memory_get` |
| Session listing | `sessions_list`, `sessions_info` |

**Behavior:** Action executes normally, entry written to approval_history.json.

---

## 🔄 Workflow Functions

### checkApprovalRequired(action)

```javascript
/**
 * Checks if an action requires approval
 * @param {Object} action - Action details {type, command, target, userId}
 * @returns {Object} {required: boolean, category: string, reason: string}
 */
```

**Logic:**
1. Check against DESTRUCTION patterns → category: "DESTRUCTION"
2. Check against ELEVATED patterns → category: "ELEVATED"
3. Default → category: "MONITORING"

---

### requestApproval(action, details)

```javascript
/**
 * Sends approval request to Nico via Telegram
 * @param {Object} action - Action to be approved
 * @param {Object} details - Additional context
 * @returns {string} approvalToken - Unique token for this request
 */
```

**Creates Telegram message with:**
- Action description
- Risk level indicator
- Approve/Deny inline buttons

---

### executeApproved(action, approvalToken)

```javascript
/**
 * Executes an action after approval received
 * @param {Object} action - The approved action
 * @param {string} approvalToken - Token from requestApproval
 * @returns {Object} {success: boolean, result: any}
 */
```

**Validation:**
- Verify approvalToken exists and is not expired
- Verify action matches original request
- Log execution

---

### logApproval(action, status)

```javascript
/**
 * Logs all approval decisions to approval_history.json
 * @param {Object} action - Action details
 * @param {string} status - "APPROVED", "DENIED", "BLOCKED", "EXECUTED"
 */
```

---

## 📱 Telegram Approval Schema

```javascript
const approvalButtons = [
  [
    { text: "✅ Genehmigen", callback_data: `approve_${approvalToken}` },
    { text: "❌ Ablehnen", callback_data: `deny_${approvalToken}` }
  ]
];
```

**Approval Message Format:**
```
⚠️ *Genehmigung erforderlich*

📋 *Aktion:* [action description]
🎯 *Kategorie:* [ELEVATED/Heftrisk]
⏰ *Zeit:* [timestamp]

Bitte genehmigen oder ablehnen.
```

---

## 📋 Approval History

**File:** `/home/clawbot/.openclaw/workspace/builder/approval_history.json`

```json
{
  "approvals": [
    {
      "id": "uuid",
      "timestamp": "ISO8601",
      "action": {
        "type": "exec",
        "command": "rm -rf /tmp/test",
        "target": "/tmp"
      },
      "category": "DESTRUCTION",
      "status": "BLOCKED",
      "nicoResponse": null
    },
    {
      "id": "uuid",
      "timestamp": "ISO8601",
      "action": {
        "type": "exec",
        "command": "systemctl restart openclaw"
      },
      "category": "ELEVATED",
      "status": "APPROVED",
      "nicoResponse": { "approved": true, "timestamp": "ISO8601" }
    }
  ]
}
```

---

## 🚨 Alert Thresholds

| Category | Alert Target | Method |
|----------|--------------|--------|
| DESTRUCTION block | Nico + All Agents | Telegram + Memory note |
| 3+ ELEVATED denials in 1 hour | Nico | Telegram |
| 5+ ELEVATED approvals in 1 hour | Nico | Telegram |

---

## ✅ QC Validation Checklist

- [ ] DESTRUCTION patterns actually block execution
- [ ] ELEVATED actions pause and wait for response
- [ ] Approval tokens are unique and time-limited (15 min expiry)
- [ ] History file is append-only and immutable
- [ ] Telegram buttons route to correct handlers
- [ ] Expired tokens are rejected with clear error

---

*Specification v1.0 — Builder Team*
