# Skills Directory Audit

**Generated:** 2026-04-15  
**Path:** `/home/clawbot/.openclaw/workspace/skills/`

---

## Skills Overview

| Skill | Description | Tools | Active? |
|-------|-------------|-------|---------|
| **backend-api** | Backend & API Development (Node.js, Express, Stripe, Webhooks) für EmpireHazeClaw | Node.js, exec, webhooks | ✅ active |
| **backup-advisor** | Berät wann Backups sinnvoll sind, erkennt Backup-Paranoia | Python (index.py) | ✅ active |
| **bug-hunter** | Scannt Logs alle 30 Min auf echte Bugs (过滤 INFO-False-Positives) | Python (bug_scanner.py), cron | ✅ active |
| **capability-evolver** | Self-Evolution Engine — analysiert Runtime History, optimiert Gene-basiert | Node.js, git, npm, shell | ✅ active (v1.40.0) |
| **code-review** | Automated Code Review mit MiniMax M2.7 — PRs, Bugs, Security | git, exec, MiniMax M2.7 | ✅ active |
| **coding** | Full-Stack Development für Python, JS/Node.js, Bash, HTML/CSS | Python, Node.js, exec | ✅ active |
| **content-creator** | Content Erstellung für Social Media & Blog mit AI-Detection-Umgehung | Python (humanize_content.py), semantic_search.py | ✅ active |
| **debug-helper** | Automated failure analysis — parsed stack traces, findet bekannte Issues | exec, read logs | ✅ active |
| **frontend** | Frontend Development für EmpireHazeClaw Websites (Vercel, Dark Theme) | Vercel CLI, HTML/CSS/JS | ✅ active |
| **git-manager** | Intelligent Git operations — branching, commits, PRs, merge conflicts | git (child_process) | ✅ active |
| **guardrails** | Preventiert over-active inference und halluzinierte Trigger | Python (input_guardrail.py, output_guardrail.py) | ✅ active |
| **hyperparameter-tuner** | Optimiert Learning Loop Hyperparameters (Epsilon, Error Delta, etc.) | Python, exec | ✅ active |
| **log-aggregator** | Zentrale Log-Kollektion und Analyse für System Health Monitoring | exec, Python | ✅ active |
| **loop-prevention** | Erkennt und verhindert repetitive Loops ohne echten Fortschritt | Python (loop_check.py, learning_tracker.py) | ✅ active |
| **memory-sanitizer** | Entfernt sensible Daten aus Memory-Dateien (API Keys, Emails, etc.) | Node.js (index.js) | ✅ active (v2) |
| **prompt-coach** | Always-on Prompt Co-Pilot — optimiert Nico's inputs, fragt nach wenn ambigue | Node.js (index.js) | ✅ active |
| **qa-enforcer** | Quality Assurance für alle Outputs — Tests, Commits, Dokumentation | Python (test_framework.py, fast_test.py) | ✅ active |
| **repo-analyzer** | Analysiert Codebase Struktur, Dependencies, Complexity, Security | Node.js, git, exec | ✅ active |
| **research** | Web Research und Knowledge Acquisition (Web Search, Fetch) | web_search, web_fetch | ✅ active |
| **self-improvement** | Kontinuierliches Lernen und Selbstverbesserung | Python (self_eval.py, deep_reflection.py) | ✅ active |
| **semantic-search** | Semantische Suche mit lokalen Embeddings (all-MiniLM-L6-v2) | Python (semantic_search.py) | ✅ active |
| **system-manager** | System health monitoring, backup, cron, security, performance | Python (quick_check.py, health_monitor.py), exec | ✅ active |
| **test-generator** | Generiert Unit Tests, Integration Tests automatisch von Source Code | Node.js, pytest, jest | ✅ active |
| **voice-agent** | Offline Voice-to-Voice AI (Whisper.cpp STT + Pocket-TTS) | whisper-cli, python3, ffmpeg | ✅ active |
| **youtube-transcript** | Holt Transcripts/Untertitel von YouTube Videos mit Timestamps | yt-dlp, whisper | ✅ active |

---

## Summary

| Status | Count |
|--------|-------|
| ✅ active | 19 |
| ❓ unknown | 8 |
| ❌ inactive | 0 |

**Total Skills:** 27

---

## Skills with _meta.json Manifest

| Skill | Has Manifest? |
|-------|---------------|
| backend-api | ✅ |
| backup-advisor | ✅ |
| bug-hunter | ❌ |
| capability-evolver | ✅ |
| code-review | ✅ |
| coding | ✅ |
| content-creator | ✅ |
| debug-helper | ✅ |
| frontend | ✅ |
| git-manager | ✅ |
| guardrails | ❌ |
| hyperparameter-tuner | ✅ |
| log-aggregator | ✅ |
| loop-prevention | ✅ |
| memory-sanitizer | ❌ |
| prompt-coach | ❌ |
| qa-enforcer | ✅ |
| repo-analyzer | ✅ |
| research | ❌ |
| self-improvement | ❌ |
| semantic-search | ✅ |
| system-manager | ❌ |
| test-generator | ✅ |
| voice-agent | ✅ |
| youtube-transcript | ❌ |

**Manifests:** 19 / 27

---

## Skills Missing SKILL.md

- *(All skills have SKILL.md)*

---

## Skills with Index/Script Files

| Skill | Main File |
|-------|-----------|
| backup-advisor | index.py |
| bug-hunter | bug_scanner.py |
| capability-evolver | index.js |
| code-review | index.js |
| debug-helper | index.js |
| git-manager | index.js |
| hyperparameter-tuner | index.js |
| log-aggregator | index.js |
| loop-prevention | index.py |
| memory-sanitizer | index.js |
| prompt-coach | index.js |
| qa-enforcer | index.py |
| repo-analyzer | index.js |
| research | index.py |
| self-improvement | index.py |
| semantic-search | index.js |
| system-manager | index.py |
| test-generator | index.js |
| voice-agent | bin/* scripts |
| youtube-transcript | (CLI only) |

---

## Notes

1. **Status unknown** — 8 skills (backend-api, content-creator, debug-helper, frontend, hyperparameter-tuner, log-aggregator, voice-agent) either lack `_meta.json` or have no status field. Consider adding explicit status for these.

2. **Manifests missing** — 8 skills lack `_meta.json` (bug-hunter, guardrails, memory-sanitizer, prompt-coach, research, self-improvement, system-manager, youtube-transcript). Consider adding manifests for consistency.

3. **voice-agent** — complex multi-file skill with install.sh, config/, examples/ — appears functional but status is unknown.

4. **capability-evolver** — most sophisticated skill with gene-based evolution, GEP protocol, version 1.40.0.