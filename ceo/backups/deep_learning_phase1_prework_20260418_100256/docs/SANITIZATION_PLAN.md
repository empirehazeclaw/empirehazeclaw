# 🧹 Memory Sanitization Plan

## Ziel
Alle sensiblen Daten aus Memories, Decisions, etc. entfernen → nur "rohe Daten" für Model-Training übrig.

---

## Was muss ersetzt werden

### 🔴 KRITISCH (Secret/Data Loss Risk)

| Pattern | Beispiel | Ersetzen mit |
|---------|----------|--------------|
| API Keys | `sk-1234567890abcdef` | `{{API_KEY_1}}` |
| Bot Tokens | `8397...oH9Y` | `{{TELEGRAM_BOT_TOKEN}}` |
| Database Passwords | `mypassword123` | `{{DB_PASSWORD}}` |
| AWS Keys | `AKIAIOSFODNN7EXAMPLE` | `{{AWS_ACCESS_KEY}}` |
| Stripe Keys | `sk_live_...` | `{{STRIPE_KEY}}` |
| MiniMax Keys | `Bearer eyJhbG...` | `{{MINIMAX_KEY}}` |

### 🟠 SENSITIV (Privacy Risk)

| Pattern | Beispiel | Ersetzen mit |
|---------|----------|--------------|
| Namen | "Nico", "Sir HazeClaw" | `{{USER_NAME}}`, `{{AGENT_NAME}}` |
| Emails | `empirehazeclaw@gmail.com` | `{{USER_EMAIL}}` |
| Telegram IDs | `5392634979` | `{{USER_TELEGRAM_ID}}` |
| Telefon-Nummern | `+49 123 456789` | `{{PHONE_NUMBER}}` |
|Addresses | Bertha... | `{{ADDRESS}}` |
| Domain Namen | `empirehazeclaw.com` | `{{PRIMARY_DOMAIN}}` |

### 🟡 KONTEXT (Identifying Context)

| Pattern | Beispiel | Ersetzen mit |
|---------|----------|--------------|
| Agent-Namen | "Sir HazeClaw", "CEO Agent" | `{{AGENT_COORDINATOR}}` |
| Skill-Namen | "capability-evolver" | `{{SKILL_ANALYZER}}` |
| Script-Pfade | `/home/clawbot/.openclaw/...` | `{{WORKSPACE_ROOT}}` |
| Cron Job Namen | "Learning Loop v3" | `{{CRON_LEARNING}}` |
| Workspace Name | "ceo" | `{{AGENT_ID}}` |

---

## Was bleibt (Training-Relevant)

```
✅ Business Logik (Pricing, KMU-Targeting)
✅ Technical Patterns (Error handling, Timeouts)
✅ Workflows (Morning routine, Task execution)
✅ Decision Criteria (Was来判断是个好主意)
✅ Learnings (Was hat nicht funktioniert)
✅ Prozesse (Wie plant, executed, validated)
✅ Memory Struktur (Wie Erinnerungen organisiert)
```

---

## Output Struktur

```
sanitized_memory/
├── facts.md              # Anonymisierte Fakten
├── decisions.md          # Entscheidungen ohne IDs
├── patterns.md           # Erkannte Patterns
├── workflows.md          # Prozesse
├── skills.md             # Skill-Struktur
├── kg/
│   └── knowledge_graph.json  # Entitäten ohne Namen
└── _mapping.json         # Original → Sanitized Mapping
```

---

## Tool: memory-sanitizer

**Usage:**
```bash
node memory-sanitizer.js --dry-run    # Preview was passiert
node memory-sanitizer.js --sanitize   # Tatsächlich sanitizen
node memory-sanitizer.js --restore   # Restore aus mapping
```

---

## Workflow

```
1. Backup erstellen
2. Dry-run: Was wird ersetzt?
3. Review der Ersetzungen
4. Sanitize
5. Verify: Keine sensiblen Daten mehr?
6. Export als JSON für Training
```
