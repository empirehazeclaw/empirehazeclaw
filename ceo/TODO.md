# TODO.md — Sir HazeClaw

## Priorität: SOFORT

### 1. debug-helper 🟥 HIGH
**Status:** ✅ FERTIG
**Zweck:** Automatic failure analysis
- Parse exception stack traces ✅
- Find similar known issues ✅
- Suggest fixes based on patterns ✅
- Integrate with learning loop ✅
**Output:** /home/clawbot/.openclaw/workspace/skills/debug-helper/
**Getestet:** 2026-04-14 — findet 7 Issues in Logs

#### Gefundene Issues beim Test:
- cron_healer: "Cron list timeout"
- semantic_search.py fehlt
- kg_auto_populate.py fehlt
- sqlite_vacuum.sh fehlt

### 2. hyperparameter-tuner 🟥 HIGH
**Status:** ✅ FERTIG (Suggestions ready)
**Zweck:** Optimize Learning Loop parameters
- Adjust MAB epsilon decay rate ✅
- Tune Thompson sampling priors ✅
- Optimize validation thresholds ✅
**Output:** /home/clawbot/.openclaw/workspace/skills/hyperparameter-tuner/
**Getestet:** 2026-04-14 — 3 Suggestions generiert

#### Current Status:
- Score: 0.7629 | Iteration: 82
- Status: plateau (0.0002 change over last 10)

#### Suggestions (not applied yet):
| Parameter | Current | Suggested |
|-----------|---------|-----------|
| epsilon_start | 0.3 | 0.35 |
| epsilon_decay | 0.01 | 0.013 |
| pattern_decay_rate | 0.05 | 0.07 |

### 3. log-aggregator 🟡 MEDIUM
**Status:** ✅ FERTIG
**Zweck:** Centralize all system logs
- learning_loop.log ✅
- openclaw logs ✅
- cron job logs ✅
- Error patterns over time ✅
- Feed into Learning Loop analysis ✅
**Output:** /home/clawbot/.openclaw/workspace/skills/log-aggregator/
**Getestet:** 2026-04-14 — 16 log sources found, 7-day trend shown

#### Log Sources Found:
- 16 log files in ~/.openclaw/logs/
- Error trend: 2 errors on Apr 13, 0 errors on Apr 14 ✅

#### Usage:
```bash
node index.js --sources  # List all log sources
node index.js --errors   # Show errors today
node index.js --trend 7  # 7-day error trend
node index.js --export learning_loop  # Export for learning loop
```

## Wartend

### 4. PR Reviewer 🟡 MEDIUM
**Status:** Wartend
Auto-review our own PRs via MiniMax

### 5. Batch Processor 🟡 MEDIUM
**Status:** Wartend
Handle multiple files at once

### 6. Integration Test Runner 🟡 MEDIUM
**Status:** Wartend
Run full test suites

### 7. Metrics Dashboard 🟢 LOW
**Status:** Wartend
Live score + iteration tracking

---

_Letzte Aktualisierung: 2026-04-14 14:08 UTC_
