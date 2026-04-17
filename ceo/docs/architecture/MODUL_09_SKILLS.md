# MODUL 09: Skills System

**Modul:** Skills — OpenClaw Capabilities
**Status:** ✅ Dokumentiert
**Letztes Update:** 2026-04-17

---

## 9.1 OVERVIEW

Skills erweitern die **Fähigkeiten** von Sir HazeClaw. Es gibt 28 installierte Skills.

### Skills Location

```
/workspace/skills/
├── _library/
├── backend-api/
├── backup-advisor/
├── bug-hunter/
├── capability-evolver/
├── code-review/
├── coding/
├── content-creator/
├── debug-helper/
├── frontend/
├── git-manager/
├── guardrails/
├── hyperparameter-tuner/
├── log-aggregator/
├── loop-prevention/
├── memory-sanitizer/
├── prompt-coach/
├── qa-enforcer/
├── repo-analyzer/
├── research/
├── self-improvement/
├── semantic-search/
├── system-manager/
├── test-generator/
├── voice-agent/
└── youtube-transcript/
```

---

## 9.2 ACTIVE SKILLS

### 🔒 Security & Safety

| Skill | Zweck | Status |
|-------|-------|--------|
| `guardrails/` | Pre/Post LLM Checks | ✅ Aktiv |
| `loop-prevention/` | Infinite Loop Detection | ✅ Aktiv |
| `qa-enforcer/` | Quality Assurance | ✅ Aktiv |

---

### 🐛 Debug & Fix

| Skill | Zweck | Status |
|-------|-------|--------|
| `bug-hunter/` | Bug Scanner | ✅ Aktiv |
| `debug-helper/` | Debug Assistant | ✅ Aktiv |
| `self-improvement/` | Self-Improvement | ✅ Aktiv |

---

### 📝 Code & Development

| Skill | Zweck | Status |
|-------|-------|--------|
| `coding/` | Code Generation | ✅ Aktiv |
| `code-review/` | Code Review | ✅ Aktiv |
| `test-generator/` | Test Creation | ✅ Aktiv |
| `repo-analyzer/` | Repository Analysis | ✅ Aktiv |
| `git-manager/` | Git Operations | ✅ Aktiv |

---

### 📚 Research & Knowledge

| Skill | Zweck | Status |
|-------|-------|--------|
| `research/` | Research Tasks | ✅ Aktiv |
| `semantic-search/` | Hybrid Search | ✅ Aktiv |
| `capability-evolver/` | Capability Evolution | ✅ Aktiv |

---

### 🤖 System Management

| Skill | Zweck | Status |
|-------|-------|--------|
| `system-manager/` | System Operations | ✅ Aktiv |
| `backup-advisor/` | Backup Empfehlungen | ✅ Aktiv |
| `hyperparameter-tuner/` | HPO | ✅ Aktiv |

---

### 📱 Content & Media

| Skill | Zweck | Status |
|-------|-------|--------|
| `content-creator/` | Content Creation | ✅ Aktiv |
| `voice-agent/` | Voice Agent | ✅ Aktiv |
| `youtube-transcript/` | YouTube Transcripts | ✅ Aktiv |
| `frontend/` | Frontend Dev | ✅ Aktiv |

---

### 🔧 Infrastructure

| Skill | Zweck | Status |
|-------|-------|--------|
| `backend-api/` | API Development | ✅ Aktiv |
| `log-aggregator/` | Log Aggregation | ✅ Aktiv |

---

## 9.3 SKILL REGISTRY

Skills werden in OpenClaw registriert:

```bash
# Check registered skills
openclaw skills list
```

### Skill Structure

```
skill_name/
├── SKILL.md           # Skill Definition
├── PROMPT.md          # Skill Prompt
├── TOOLS.md           # Tool Usage
└── ...                # Skill-spezifische Files
```

---

## 9.4 GUARDRAILS SKILL

**Location:** `/workspace/skills/guardrails/`

**Zweck:** Pre/Post LLM Checks für Safety

**Checks:**
- Input Validation
- Output Sanitization
- Rate Limiting
- Content Filtering

**Konfiguration:**
```bash
/workspace/skills/guardrails/
├── pre_check.py       # Pre-LLM checks
├── post_check.py      # Post-LLM checks
└── config.py          # Configuration
```

---

## 9.5 CAPABILITY EVOLVER

**Location:** `/workspace/skills/capability-evolver/`

**Zweck:** Automatische Capability Evolution

**Was es tut:**
1. Analysiert System Capabilities
2. Identifiziert Lücken
3. Evolvet Fähigkeiten
4. Evaluiert Results

---

## 9.6 SELF-IMPROVEMENT SKILL

**Location:** `/workspace/skills/self-improvement/`

**Zweck:** Kontinuierliche Selbstverbesserung

**Integration:**
- Learning Loop Integration
- Performance Tracking
- Decision Optimization

---

## 9.7 MEMORY SANITIZER

**Location:** `/workspace/skills/memory-sanitizer/`

**Zweck:** Sensible Daten aus Memory entfernen

**Was es tut:**
1. Scannt Memory Files
2. Erkennt PII/Sensitive Data
3. Redacted/Entfernt
4. Logt Changes

---

## 9.8 BUG HUNTER SKILL

**Location:** `/workspace/skills/bug-hunter/`

**Cron:** Every 30 minutes

**Was es tut:**
1. Scannt alle Logs
2. Pattern Matching für Bugs
3. False Positive Filter
4. Report Generation

---

## 9.9 HYPERPARAMETER TUNER

**Location:** `/workspace/skills/hyperparameter-tuner/`

**Zweck:** Automatische HPO

**Was es tut:**
1. Evaluiert aktuelle Params
2. Testet Variationen
3. Optimiert Performance
4. Dokumentiert Changes

---

## 9.10 CUSTOM SKILLS

### Agent-Specific Skills

**Location:** `/workspace/ceo/skills/`

Enthält Skills speziell für Sir HazeClaw.

---

## 9.11 SKILLS INDEX

**File:** `/workspace/SKILLS_INDEX.md`

Enthält:
- Skill Name
- Category
- Purpose
- Status
- Last Used

---

## 9.12 SKILLS AUDIT

**File:** `/workspace/ceo/SKILLS_AUDIT.md`

Letzter Audit: 2026-04-15

**Ergebnis:**
- 28 Skills installiert
- 24 aktiv
- 4 deprecated/disabled

---

## 9.13 BEKANNTE ISSUES

| Issue | Status | Notes |
|-------|--------|-------|
| Skill duplicates | ℹ️ | voice-call duplicate plugin |
| Some skills unused | 🟡 | Könnten archiviert werden |

---

## 9.14 SKILL AKTIVIERUNG

Skills werden via AGENTS.md aktiviert:

```markdown
## Skills
- skill:guardrails
- skill:bug-hunter
- skill:capability-evolver
```

---

*Modul 09 — Skills | Sir HazeClaw 🦞*
