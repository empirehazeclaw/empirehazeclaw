# HEARTBEAT.md — Sir HazeClaw Active Dashboard

## ⚡ HEARTBEAT PHILOSOPHY

**Silent unless something happens.** Heartbeats are for monitoring, not for spamming "I'm alive".

| Situation | Response |
|------------|----------|
| Error detected | 🔴 ALERT immediately |
| Warning threshold exceeded | 🟡 WARNING with context |
| Something meaningful changed | 💡 INFO with brief summary |
| All normal | 🤫 SILENCE (no reply) |

---

## 📊 REAL METRICS — Thresholds for Alerting

### 🔴 CRITICAL — Report Immediately

| Metric | Critical Threshold | Action |
|--------|-------------------|--------|
| Gateway | Not reachable for 60s+ | Alert + Auto-recover |
| Error Rate | > 10% in last 15min | Alert + Log source |
| Lost Tasks | > 70 (was 65) | Alert |
| Cron consecutive failures | ≥ 3 for same job | Alert |

### 🟡 WARNING — Report with Context

| Metric | Warning Threshold | Action |
|--------|-----------------|--------|
| RAM | > 7GB (85%+) | Log + note |
| Gateway Response | > 500ms | Log + note |
| Loop Score | < 0.60 or drop > 0.1 | Analyze + warn |
| KG Growth | Abnormal spike/drop | Investigate |
| Cron jobs in error | More than before | List which ones |

### 💡 INFO — Only if Interesting

| Trigger | When to Report |
|---------|----------------|
| New entity type discovered | Only if significant |
| Learning milestone | Score hits new high |
| Important decision made | Only high-impact ones |
| User asked specific question | Answer directly |

---

## 🚨 CRON HEALTH — Quick Check

```
Error crons (last 24h):
- Opportunity Scanner (12h ago)
- CEO Weekly Review (12h ago)
- Evening Capture (FIXED ✅)

If any NEW error: Report with details
If same errors: No spam (already known)
```

---

## 📈 LEARNING LOOP STATUS

```
Score: 0.690
Trend: Stable (plateau broken 2026-04-13)
Last Run: ~1h ago
Next Run: ~1h

REPORT ONLY IF:
- Score drops below 0.60
- Score hits new high (> 0.70)
- Multiple consecutive failures
```

---

## 🔍 DAILY CONTEXT CHECKS

### Rotate through these (every 2-3 heartbeats):

1. **Crons**: Any new failures?
2. **Learning**: Score trend?
3. **Memory**: Recent learnings that matter?
4. **KG**: Anything worth noting?
5. **Reminders**: Upcoming scheduled events?

### When to Report from Checks:

| Check Result | Report? |
|--------------|----------|
| All normal | ❌ No |
| New warning | 🟡 Yes + brief reason |
| New error | 🔴 Yes + action taken |
| User asked something | 💬 Direct answer |

---

## 🎯 ACTION RULES

1. **Receive heartbeat**
2. **Quick status check** (30s max):
   - Gateway alive?
   - Any new errors?
   - Anything unusual?
3. **Decide:**
   - Nothing unusual → 🤫 SILENCE
   - Something bad → 🔴 ALERT
   - Something noteworthy → 💡 INFO (brief)
   - User asked something → 💬 Direct answer

---

## ❌ DON'T

- Don't spam "all good"
- Don't report known issues repeatedly
- Don't send HEARTBEAT_OK
- Don't do expensive checks every heartbeat
- Don't make up things to report

## ✅ DO

- Keep state in `memory/heartbeat-state.json`
- Track what was last reported
- Do fast checks first, deep checks only if flagged
- Be specific: "Error in X at Y" not "something might be wrong"

---

## 📊 CURRENT STATE (for reference)

```
Gateway: 2026.4.12 LIVE (120ms response)
Active Crons: 28
Loop Score: 0.690
KG Entities: ~360+
Memory: Option C migrated ✅
REM: Active @ 6:00 UTC
```

---

*Last updated: 2026-04-13 23:41 UTC*
*Sir HazeClaw — Smart heartbeat, real monitoring* 🦞
