# OpenClaw Multi-Agent & Security Research
*Erstellt: 2026-04-07 | Quelle: Web-Recherche*

---

## Quellen

1. **OpenClaw Architecture** – dev.to "I built a team of 36 AI agents"
2. **OWASP AI Agent Security Cheat Sheet** – cheatsheetseries.owasp.org
3. **Microsoft Agent Governance Toolkit** – opensource.microsoft.com/blog
4. **OpenClaw Docs** – docs.openclaw.ai
5. **Multi-Agent Security** – augmentcode.com, gravitee.io

---

## OpenClaw Architektur

### Gateway als Kernel
- Persistenter Daemon verwaltet Agent Lifecycles
- Multi-Channel Routing (Telegram, Slack, Discord, etc.)
- 3 Session-Typen: interactive, background, scheduled

### Agent-Dateien
| Datei | Zweck |
|-------|-------|
| SOUL.md | Identity, Rolle, Reporting-Hierarchy |
| AGENTS.md | Boot-Sequence bei jedem Start |
| USER.md | Context über den Menschen |
| MEMORY.md | Persistentes Wissen |
| IDENTITY.md | Persona für Agent-Kommunikation |

### Memory 4-Layer
```
Session → Daily → Long-term → Shared
```

---

## Security Best Practices (OWASP)

### Top 10 Risks
1. Prompt Injection (Direct & Indirect)
2. Tool Abuse / Privilege Escalation
3. Data Exfiltration
4. Memory Poisoning
5. Goal Hijacking
6. Excessive Autonomy
7. Cascading Failures (Multi-Agent)
8. AI Console Malicious Configuration
9. Denial of Wallet (DoW)
10. Sensitive Data Exposure

### 8 Security Principles
1. **Least Privilege Tools** – Minimal-Tool-Grant pro Agent
2. **Input Validation** – Alle externen Daten als untrusted
3. **Memory Security** – Validierung, TTL, Checksums
4. **Human-in-the-Loop** – Risk-Level Classification
5. **Output Validation** – PII-Filter, Schema-Validation
6. **Monitoring** – Anomaly Detection, Audit Trails
7. **Multi-Agent Isolation** – Trust Boundaries, Circuit Breakers
8. **Data Protection** – Klassifikation, Encryption

### Multi-Agent Trust Levels
- UNTRUSTED (0) → INTERNAL (1) → PRIVILEGED (2) → SYSTEM (3)

---

## Skills & ClawHub
- Skills in `<workspace>/skills/` (per-agent) oder `~/.openclaw/skills/` (shared)
- Skills.entries.*.env injiziert Secrets in Host-Prozess

---

## Monitoring Thresholds (OWASP)
```python
"tool_calls_per_minute": 30
"failed_tool_calls": 5
"injection_attempts": 1
"sensitive_data_access": 3
"cost_per_session_usd": 10.0
```
