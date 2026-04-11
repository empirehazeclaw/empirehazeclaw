# EmpireHazeClaw — Functional Test Report
*Generated: 2026-03-28 15:35 UTC*

---

## SUMMARY

| Component | Status | Notes |
|-----------|--------|-------|
| Lead-Gen (file_lock) | ✅ WORKS | Writes/reads correctly |
| Lead-Gen (CRM CSV) | ✅ WORKS | 24 leads readable |
| Email Sequence | ⚠️ PARTIAL | Loads OK, but template mismatch |
| GOG Token | ❌ BROKEN | Binary path wrong, missing --account |
| SMTP Email | ❌ NOT CONFIGURED | GMAIL_USER/GMAIL_APP_PASSWORD not set |
| Stripe Webhook Handler | ✅ WORKS | Correct event structure required |
| Stripe Env Vars | ❌ NOT SET | STRIPE_SECRET_KEY/WEBHOOK_SECRET missing |
| Memory Files | ✅ WORKS | SYSTEM_CORE.md + REVENUE.md readable |
| Onboarding Queue | ✅ WORKS | Files created correctly |
| Data Files | ⚠️ PARTIAL | Some expected files missing |

---

## 1. LEAD-GEN FLOW TEST

### `locked_write` ✅ WORKS
```bash
python3 -c "from lib.file_lock import locked_write; locked_write('data/test_lead.json', {'test': 'value'})"
```
- **Result:** SUCCESS — data/test_lead.json written and readable
- **Output:** `{"test": "value"}`

### `crm_leads.csv` ✅ WORKS
- 24 leads loaded successfully
- All fields present: company, contact_name, email, phone, website, industry, status, last_contact, notes, source
- Sample: Restaurant Ferron, Il Barista Café & Bistro

### Missing Data Files ⚠️
- `data/sent_leads.json` — **MISSING** (created on first use)
- `data/email_sequence_log.json` — **MISSING** (created on first use)

---

## 2. OUTREACH TEST

### `email_sequence.py` — Loads ✅ | Template ⚠️
- Module loads without errors
- **Issue:** `BODY_STEP1` uses `{name}` placeholder but CRM leads have `contact_name` field
  ```python
  # Template expects:
  BODY_STEP1.format(name=..., ...)  # KeyError: 'name'
  # Leads have:
  {'contact_name': '...', ...}  # wrong key
  ```
- **Fix needed:** Either change template to `{contact_name}` or map `contact_name` → `name` before rendering

### `send_email` → SMTP ❌ NOT CONFIGURED
- Function uses Gmail SMTP (`smtplib`)
- **Missing env vars:** `GMAIL_USER`, `GMAIL_APP_PASSWORD`
- Both are **NOT SET** in environment
- **Error if called:** `GMAIL_APP_PASSWORD not set`

### GOG CLI ❌ BROKEN
- **Old path fails:** `/home/clawbot/archive_old_system/.linuxbrew/Cellar/gogcli/0.12.0/bin/gog` — File not found
- **Working path:** `/home/clawbot/.local/bin/gog`
- **Error:** `missing --account` — no default GOG account configured
- **Fix:** Need `gog auth manage` to set default account, or pass `--account empirehazeclaw@gmail.com`

---

## 3. STRIPE WEBHOOK TEST

### `stripe_webhook.py` ✅ LOADS | ✅ WORKS with correct event structure

**CRITICAL BUG in test approach (not the script):**
- I initially called `handle_checkout_completed(session_object)` directly
- The handler expects `event.get("data", {}).get("object", {})` — i.e., a full Stripe event wrapper
- **Correct usage:** Pass the full `{"type": "...", "data": {"object": {...}}}` event

**Correct call:**
```python
full_event = {
    'type': 'checkout.session.completed',
    'data': {'object': {...session data...}}
}
mod.handle_checkout_completed(full_event)  # ✅ Works
```

**With correct event, results:**
- `customers.json` — ✅ Customer saved with all fields
- `onboarding_queue.json` — ✅ Queue entry created
- `trigger_onboarding` — ✅ Called (logs message, writes to `data/onboarding_pending`)

### Missing Env Vars ❌
- `STRIPE_SECRET_KEY` — NOT SET
- `STRIPE_WEBHOOK_SECRET` — NOT SET
- Webhook server starts on port **5005** (configured)

---

## 4. FULFILLMENT TEST

### Files Created ✅
- `data/customers.json` — ✅ Created, contains customer records
- `data/onboarding_queue.json` — ✅ Created, contains queue entries
- `data/onboarding_pending` — ✅ Created by `trigger_onboarding()`

### Customer Record (from test) ✅
```json
{
  "email": "func_test@example.com",
  "name": "Functional Test User",
  "product": "Managed AI Hosting - Starter",
  "amount": 99.0,
  "currency": "EUR",
  "session_id": "cs_test_func_123",
  "status": "paid",
  "created": "2026-03-28T15:35:31.220649",
  "onboarding_status": "pending"
}
```

---

## 5. MEMORY INTEGRITY TEST

### SYSTEM_CORE.md ✅ READABLE
- File exists at workspace root
- Contains Priority Flags, Nico's profile, business logic
- First 20 lines read successfully

### REVENUE.md ✅ READABLE
- File exists at workspace root
- Contains revenue focus, mission (ERSTER KUNDE), priorities
- First 20 lines read successfully

---

## BOTTLENECK REPORT

| # | Bottleneck | Severity | Fix |
|---|-----------|----------|-----|
| 1 | No `GMAIL_APP_PASSWORD` env var configured | 🔴 CRITICAL | SMTP send won't work; need to configure Gmail app password |
| 2 | GOG CLI default account not set | 🔴 CRITICAL | Outreach emails can't be sent; need `gog auth manage` |
| 3 | Stripe env vars not set | 🔴 CRITICAL | Webhook processing won't work in production |
| 4 | Email template `{name}` vs `contact_name` mismatch | 🟡 MEDIUM | Template renders with KeyError; fix template or map field |
| 5 | Wrong GOG binary path in docs | 🟡 MEDIUM | Docs say `archive_old_system/.linuxbrew/...` but actual is `.local/bin/gog` |

---

## EXACT ERROR MESSAGES

### GOG CLI
```
/home/clawbot/archive_old_system/.linuxbrew/Cellar/gogcli/0.12.0/bin/gog: No such file or directory
```
When using correct path:
```
missing --account (or set GOG_ACCOUNT, set default via `gog auth manage`, or store exactly one token)
```

### SMTP Email
```
(False, 'GMAIL_APP_PASSWORD not set')
```

### Email Template (when using CRM lead data)
```
KeyError: 'name'
```
Leads have `contact_name` but template uses `{name}`.

### Stripe (with wrong event structure)
```
Session object passed directly → returns None but also logs empty values
```
The handler requires `event.get("data", {}).get("object", {})` structure.

---

## RECOMMENDED FIXES (Priority Order)

1. **Configure GOG account:**
   ```bash
   /home/clawbot/.local/bin/gog auth manage
   # Set empirehazeclaw@gmail.com as default
   ```

2. **Fix email template mismatch** in `email_sequence.py`:
   ```python
   # Change BODY_STEP1 from {name} to {contact_name}
   # OR map before calling:
   lead['name'] = lead.get('contact_name', '')
   ```

3. **Set Stripe env vars** (production requirement):
   ```bash
   export STRIPE_SECRET_KEY=sk_live_...
   export STRIPE_WEBHOOK_SECRET=whsec_...
   ```

4. **Update GOG binary path** in all docs/scripts from:
   `/home/clawbot/archive_old_system/.linuxbrew/Cellar/gogcli/0.12.0/bin/gog`
   → `/home/clawbot/.local/bin/gog`

5. **SMTP not configured** — if using GOG for emails, `send_email` via SMTP will fail. Ensure outreach uses GOG CLI directly.
