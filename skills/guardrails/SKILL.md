# Guardrails Skill

**Purpose:** Prevent over-active inference and hallucinated triggers.

**Components:**
- `input_guardrail.py` — Pre-action trigger validation
- `output_guardrail.py` — Post-action self-check

---

## input_guardrail.py

**Use BEFORE taking any action that wasn't explicitly requested.**

```bash
python3 /home/clawbot/.openclaw/workspace/skills/guardrails/input_guardrail.py --check "<action description>"
```

**Returns:**
- `PASS` (exit 0) — Trigger confirmed, proceed
- `BLOCK` (exit 1) — Inference detected, STOP
- `UNCERTAIN` (exit 2) — No clear trigger, ask first

**Examples:**
```bash
# ✅ PASS — explicit trigger
python3 .../input_guardrail.py --check "Nico wrote 'check crons'"

# 🚫 BLOCK — inference without evidence
python3 .../input_guardrail.py --check "I think Nico might have sent a file"

# ⚠️ UNCERTAIN — no trigger
python3 .../input_guardrail.py --check "the system might be running"
```

**Trigger Keywords:**
`file received`, `message received`, `command received`, `cron completed`, `webhook received`, `explicit request`, `user said`, `check`, `run`, `fix`, `execute`

**Inference Indicators (BLOCKED):**
`maybe`, `probably`, `i think`, `i assume`, `possibly`, `might have`, `seems`, `i noticed`, `perhaps`

---

## output_guardrail.py

**Use AFTER any action to self-verify you had proper trigger.**

```bash
python3 /home/clawbot/.openclaw/workspace/skills/guardrails/output_guardrail.py --action "<what you did>"
```

**Examples:**
```bash
# Self-check after action
python3 .../output_guardrail.py --action "I noticed the cron failed so I fixed it"
# ⚠️ Flags "i noticed" as inference without evidence

# Verify alignment with trigger
python3 .../output_guardrail.py --check-trigger "<action>" "<trigger>"

# Generate corrected version
python3 .../output_guardrail.py --correct "<wrong action>" "<reason>"
```

---

## Log

All interceptions logged to:
`/home/clawbot/.openclaw/workspace/logs/guardrail_interceptions.log`

```json
{"timestamp": "2026-04-14T16:55:00+00:00", "type": "pre-llm", "action": "...", "result": "BLOCK", "reason": "..."}
```

---

## When to Use

| Situation | Guardrail |
|-----------|-----------|
| Before transcribing audio | input_guardrail |
| Before acting on assumed file | input_guardrail |
| Before responding to "assumed" message | input_guardrail |
| After any action with "I noticed..." | output_guardrail |
| Before sending proactive report | output_guardrail |
| When unsure if trigger exists | input_guardrail --check |

---

**Rule:** If you have to think "should I check?" — check.
