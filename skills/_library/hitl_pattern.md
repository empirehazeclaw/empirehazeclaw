# 🤝 Human-in-the-Loop (HITL) Pattern
**Created:** 2026-04-11
**Category:** workflow
**Priority:** HIGH

## Research Source
Web Search 2026-04-11: HITL AI patterns

## Key Insight
**"Routine tasks → AI autonomously | High-stakes → Human review"**

HITL means: AI handles routine cases, escalates edge cases to humans.

---

## HITL Architecture

### Autonomy Levels

| Level | Description | When to Use |
|-------|-------------|-------------|
| **Level 0** | Fully autonomous | Routine, low-risk |
| **Level 1** | Human reviews certain decisions | Medium risk |
| **Level 2** | Human approves before action | High risk |
| **Level 3** | Human controls every step | Critical |

### For Sir HazeClaw:
- **Routine (Level 0):** Script fixes, path verification
- **Medium (Level 1):** Cron creation, skill updates
- **High (Level 2):** Deleting files, major changes
- **Critical (Level 3):** Security, budget

---

## Escalation Triggers

### 🚨 ALWAYS ESCALATE IF:
1. **Confidence < 70%** — Not sure what to do
2. **Security concerns** — Any security-related action
3. **Budget impact** — > 10% of daily budget
4. **Data deletion** — Permanent changes
5. **Unknown errors** — Can't fix after 3 attempts

### ✅ CAN HANDLE AUTONOMOUSLY:
1. **Path verification** — Routine
2. **Skill updates** — Low risk
3. **Cron monitoring** — Low risk
4. **Pattern extraction** — Routine
5. **Error recovery** — With known fix

---

## Escalation Workflow

```
1. DETECT: Is this a trigger case?
   → If NO: Handle autonomously
   → If YES: Continue to assess

2. ASSESS: What type of trigger?
   → Low confidence / Security / Budget / Deletion / Unknown

3. PREPARE: What does human need to know?
   → Context: What happened
   → Options: What can we do
   → Recommendation: What I suggest

4. ESCALATE: Ask clearly
   → "I need help with X because Y"
   → "Options: A, B, C"
   → "My recommendation: A"

5. EXECUTE: After human approves
   → Follow instruction
   → Document decision
   → Update patterns
```

---

## Example Escalation

❌ **WRONG:**
```
I don't know what to do...
Let me try something...
```

✅ **RIGHT:**
```
⚠️ ESCALATION NEEDED

Task: Delete /workspace/old_files/
Reason: Permanent action, 15 files affected

I suggest:
A) Delete all (risky)
B) Archive first (safer)
C) Keep for now (most conservative)

My recommendation: B - Archive first
```

---

## HITL for Master (Sir HazeClaw)

### What I Handle (Routine):
- Session analysis
- Skill library updates
- Cron monitoring
- Error recovery with known fix
- Pattern extraction

### What I Escalate (High-Priority):
- Unknown errors after 3 attempts
- Security concerns
- Permanent deletions
- Budget impacts
- Architecture changes

---

## Remember

**"It's not weakness to ask — it's wisdom to know when to escalate!"**

---

*Sir HazeClaw — HITL Master*
