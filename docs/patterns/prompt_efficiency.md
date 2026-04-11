# 📝 Prompt Efficiency Skill
**Created:** 2026-04-11
**Category:** efficiency
**Priority:** HIGH

## Problem
Prompts werden zu lang → Tokens verschwendet → Kosten steigen

## Solution
**Kurz, präzise, strukturiert**

---

## Prompt Efficiency Rules

### 1. Start Minimal
```
❌ "You are a helpful AI assistant that should..."
✅ "Help me with: [task]"
```

### 2. Context Only When Needed
```
❌ Context in EVERY message
✅ Only when relevant
```

### 3. Structured over Verbose
```
❌ "I would like you to please... and then..."
✅ "Do X → Y → Z"
```

### 4. Bullet Points over Paragraphs
```
❌ Long paragraphs
✅ Concise bullet list
```

### 5. Example-Driven
```
❌ Many examples (token-heavy)
✅ 1-2 good examples max
```

---

## Prompt Templates

### Short Task
```
Task: [one line]
Context: [if needed]
Output: [expected format]
```

### Medium Task
```
Goal: [what]
Constraints: [limits]
Steps: [if multi-step]
Output: [format]
```

### Complex Task
```
Goal: [clear]
Sub-goals: [list]
Dependencies: [if any]
Output: [format]
Deadline: [if any]
```

---

## Token Budget

| Prompt Type | Budget |
|-------------|--------|
| Simple question | < 100 tokens |
| Task with context | < 300 tokens |
| Complex multi-step | < 500 tokens |
| System prompt | < 1000 tokens |

---

## Anti-Patterns

❌ **WRONG:**
- Long intros ("As an AI...")
- Repeated context
- Verbose error explanations
- Redundant confirmations

✅ **RIGHT:**
- Direct task statement
- Minimal context
- Concise responses
- Structured output

---

## Sir HazeClaw Rules

1. **First message: Short** — don't overload
2. **Add context only when needed** — don't assume
3. **Use structured formats** — markdown, JSON
4. **Concise responses** — no filler

---

## Metrics

**Prompt Efficiency:**
```
(task_completion / tokens_used) × 100
```

---

*Sir HazeClaw — Prompt Efficiency Master*
