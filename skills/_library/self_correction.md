# 🔧 Self-Correction Protocol Skill
**Created:** 2026-04-11
**Category:** workflow
**Priority:** CRITICAL

## Based on Research
**"Build Self-Correcting Agents That Actually Finish Tasks"** — dev.to

## The Problem
If something fails, my instinct is to retry immediately.
If that fails, I retry again.
This creates loops!

## The Solution
**STOP → ANALYZE → FIX → VERIFY**

---

## Self-Correction Loop (Sir HazeClaw Edition)

```
┌─────────────────────────────────────────────────────────┐
│                    FAILURE HAPPENS                      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 1: STOP                                          │
│  "Something went wrong"                                │
│  → Don't retry immediately                            │
│  → Don't panic                                        │
│  → STOP & ANALYZE                                      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 2: ANALYZE                                       │
│  "What exactly went wrong?"                            │
│  → Read error message                                  │
│  → Check logs/context                                  │
│  → Identify ROOT CAUSE                                │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 3: FIX                                           │
│  "How do I fix the root cause?"                        │
│  → Apply fix                                           │
│  → If unknown: Ask master or document & skip          │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 4: VERIFY                                        │
│  "Did the fix work?"                                    │
│  → Test immediately                                    │
│  → If success: Continue                               │
│  → If failure: Max 2 more attempts, then escalate     │
└─────────────────────────────────────────────────────────┘
```

---

## Rules

### 🚨 CRITICAL RULES:

1. **MAX 3 CORRECTIONS per task**
   - After 3 failures: STOP, document, escalate

2. **ROOT CAUSE before retry**
   - Never retry without knowing why it failed

3. **Document before escalating**
   - What did I try?
   - What was the error?
   - What do I think the cause is?

---

## Anti-Patterns

❌ **WRONG:**
```
Error! Retry...
Error! Retry again...
Error! Retry again...
Error! Give up frustrated
```

✅ **RIGHT:**
```
Error! STOP
Analyze: Missing file
Fix: Create file
Verify: Works!
Continue
```

---

## Quick Reference

| Situation | Action |
|-----------|--------|
| Tool fails | STOP → Analyze → Fix → Verify |
| Same error twice | Root cause analysis mode |
| Unknown error | Document → Ask master |
| After 3 failures | Escalate (stop trying) |

---

## Success Criteria

✅ **Self-Correction successful if:**
1. I can explain WHY something failed
2. I fixed the ROOT CAUSE (not just symptoms)
3. I verified the fix works
4. I documented what I learned

❌ **Self-Correction failed if:**
1. I don't know why it failed
2. I retried without analysis
3. I gave up after too many attempts
4. I didn't document anything

---

## Remember

**"It's not about not failing — it's about failing smarter!"**

---

*Sir HazeClaw — Self-Correction Master*
