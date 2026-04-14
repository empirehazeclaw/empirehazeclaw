# 🧹 Memory Sanitizer v2 — MAXIMUM LEVEL

**Entfernt sensible Daten aus Memory-Dateien für sicheres Model-Training.**

---

## Was ist neu in v2?

| Feature | v1 | v2 |
|---------|----|----|
| Regex Replacement | ✅ | ✅ |
| Consistent Token Mapping | ❌ | ✅ PERSON_1, PERSON_2 |
| Timestamp Bug gefixt | ❌ | ✅ |
| Whitelist Support | ❌ | ✅ |
| Restore from Mapping | ❌ | ✅ |
| Verification Step | ❌ | ✅ |
| Sensitivity Levels | ❌ | ✅ L1/L2/L3 |
| Audit Trail | ❌ | ✅ |

---

## Sensitivity Levels

| Level | Was | Use Case |
|-------|-----|----------|
| **L1** | API Keys, Tokens, Passwords | Quick fix, max utility |
| **L2** | + Emails, Phones, Names, IDs | Production sanitize |
| **L3** | + Domains, Paths | Full anonymization |

---

## Sensible Daten Kategorien

### 🔴 CRITICAL (Level 1)

| Typ | Token |
|-----|-------|
| API Keys | `{{API_KEY}}` |
| Bot Tokens | `{{BOT_TOKEN}}` |
| JWT Tokens | `{{JWT}}` |
| AWS Keys | `{{AWS_KEY}}` |
| Database URLs | `{{DB_URL}}` |
| Private Keys | `{{PRIVATE_KEY}}` |

### 🟠 HIGH (Level 2)

| Typ | Token |
|-----|-------|
| Emails | `{{EMAIL_1}}`, `{{EMAIL_2}}` |
| Telefon | `{{PHONE_1}}`, `{{PHONE_2}}` |
| Telegram IDs | `{{USER_ID_1}}`, `{{USER_ID_2}}` |
| IP Addresses | `{{IP}}` |

### 🟡 MEDIUM (Level 3)

| Typ | Token |
|-----|-------|
| Domains | `{{PRIMARY_DOMAIN}}` |
| Workspace Paths | `/home/{{USER}}/` |

---

## Usage

```bash
# Preview (dry run)
node index.js --dry-run

# Sanitize Level 2 (default)
node index.js --sanitize

# Sanitize Level 1 only (API keys only)
node index.js --sanitize --level 1

# Sanitize Level 3 (everything)
node index.js --sanitize --level 3

# Verify sanitized output
node index.js --verify

# Show statistics
node index.js --stats

# Show whitelist
node index.js --whitelist

# Show config
node index.js --config

# Restore (manual)
node index.js --restore
```

---

## Features

### Consistent Token Mapping
```javascript
// Instead of replacing ALL names with {{PERSON}}
// v2 uses consistent mapping:
Nico → {{PERSON_1}}
Nico → {{PERSON_1}}  // Same everywhere
John → {{PERSON_2}}
```

### Whitelist Support
```javascript
// Edit _whitelist.json to add terms that should NOT be replaced
["Sir HazeClaw", "EmpireHazeClaw", "German", "KMU"]
```

### Verification
```bash
node index.js --verify
// Returns:
// ✅ VERIFICATION PASSED — No sensitive data found!
// or
// ❌ VERIFICATION FAILED — Sensitive data still present
```

### Audit Trail
```json
{
  "mappings": {
    "empirehazeclaw@gmail.com": "{{EMAIL_1}}",
    "5392634979": "{{USER_ID_1}}"
  },
  "audit": [
    {"original": "...", "token": "...", "timestamp": "..."}
  ]
}
```

---

## Output Structure

```
sanitized_memory/
├── _config.json          # Sanitization config
├── _mapping.json         # Original → Token mapping
├── _whitelist.json       # Whitelisted terms
├── _audit.json          # Audit trail
├── facts.md             # Sanitized files...
├── patterns.md
├── kg/
│   └── knowledge_graph.json
└── ...
```

---

## Workflow

```
1. Backup (optional but recommended)
   cp -r memory memory_backup

2. Dry-run to preview
   node index.js --dry-run

3. Review changes
   Check which files will be affected

4. Sanitize
   node index.js --sanitize --level 2

5. Verify
   node index.js --verify

6. Export for Training
   Use sanitized_memory/ as training data
```

---

## Best Practices (Research-Based)

1. **Konsistenz** — Same entity = Same token across all files
2. **Whitelist** — Terms that shouldn't be replaced
3. **Verification** — Always verify after sanitize
4. **Audit Trail** — Keep mapping for restore/audit
5. **Level wählen** — L2 für meisten Use Cases

---

## Troubleshooting

### "Timestamps werden ersetzt"
→ Fixed in v2! Phone pattern ist jetzt kontext-bewusst.

### "Names nicht ersetzt"
→ Check ob der Name in whitelist ist oder `preserve: true` hat.

### "Restore funktioniert nicht"
→ Restore ist manual via _mapping.json. Automatisches Restore kommt später.

---

*Basierend auf: Arxiv 2411.05978 (Amazon), AWS Comprehend, Tonic.ai Best Practices*
