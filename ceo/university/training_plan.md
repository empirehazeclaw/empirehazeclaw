# 🏛️ EmpireHazeClaw Fleet — Training Plan

*Erstellt: 2026-04-08 17:35 UTC*
*Version: 1.0*

---

## 📋 Übersicht: Agenten & Status

| Agent | Workspace | Session Key | Grund-Training | Specialized | Status |
|-------|-----------|------------|----------------|-------------|--------|
| CEO (ClawMaster) | ceo | agent:ceo:telegram:direct:5392634979 | ✅ 100% | ✅ Fleet Commander | 🏆 ZERTIFIZIERT |
| Builder | builder | agent:builder:telegram:direct:5392634979 | ⏳ 0% | ⚠️ Modul 3 ✅ | 🔴 Training nötig |
| Security Officer | security | agent:security:telegram:direct:5392634979 | ⏳ 0% | ⏳ Module 1,2,5,6.1 | 🔴 Training nötig |
| Data Manager | data | agent:data:telegram:direct:5392634979 | ⏳ 0% | ⏳ Module 6.2,7,4 | 🔴 Training nötig |
| Research | research | agent:research:telegram:direct:5392634979 | ⏳ 0% | ⏳ Module 6.1,6.3,2 | 🔴 Training nötig |

---

## 🎯 Ziel

**ALLE Agenten** müssen:
1. ✅ **Grund-Training** (10 Module + Abschlussprüfung) — **99% Bestehensgrenze**
2. ✅ **Specialized Track** (agent-spezifische Module)
3. ✅ **"Fleet Ready" Zertifikat** — darf in der Flotte arbeiten

---

## 📅 Training-Reihenfolge

```
REIHENFOLGE:
1. CEO (ClawMaster) — ✅ FERTIG
2. Builder — Nächster (hat schon Module 3)
3. Security Officer
4. Data Manager
5. Research
```

---

## 📚 Grund-Training (10 Module)

**Pflicht für ALLE Agenten:**

| # | Modul | Datei | Haupt-Themen |
|---|-------|-------|--------------|
| 1 | System-Architektur | lesson_basic_1.md | Gateway, Sessions, Tools, Channels, Memory |
| 2 | Identity & SOUL.md | lesson_basic_2.md | Persona, Workflow, Sovereign Architecture |
| 3 | Tool-Usage | lesson_basic_3.md | exec, read, write, edit, sessions_send, cron |
| 4 | Delegation & Routing | lesson_basic_4.md | Routing-Matrix, Handshake-Protokoll |
| 5 | Memory & Context | lesson_basic_5.md | MEMORY.md, memory_search, Checkpoints |
| 6 | Reporting | lesson_basic_6.md | task_report.json, Heartbeats, QC Officer |
| 7 | Sicherheit-Grundlagen | lesson_basic_7.md | Least Privilege, Input Validation, RBAC |
| 8 | Error Handling | lesson_basic_8.md | Retry, Backoff, Circuit Breaker |
| 9 | Workspace & Files | lesson_basic_9.md | Pfade, Rechte, Backups |
| 10 | Scheduling & Cron | lesson_basic_10.md | Heartbeat, Checkpoints, Delivery |

**Abschlussprüfung:** `quiz_basic_foundation.md` — 50 Fragen, **99% Bestehensgrenze (49/50)**

---

## 🔒 Security Officer Specialized Track

| # | Modul | Lektionen | Quiz |
|---|-------|-----------|------|
| 1 | Prompt Injection | 1.1, 1.2, 1.3 | quiz_module_1 |
| 2 | OWASP Top 10 | 2.1-2.4 | quiz_module_2 |
| 5 | Security Audits | 5.1-5.4 | quiz_module_5 |
| 6.1 | Agentic AI Hijacking | lesson_6_1 | quiz_module_6 |

**Zertifizierung:** Security Expert

---

## 💻 Builder Specialized Track

| # | Modul | Lektionen | Quiz |
|---|-------|-----------|------|
| 3 | Tool-Validation | 3.1, 3.2, 3.3 | quiz_module_3 ✅ (100%) |
| 7 | OpenClaw Internals | lesson_7_1 | quiz_module_7_1 |
| 1 | Prompt Injection | 1.1, 1.2, 1.3 | quiz_module_1 |

**Zertifizierung:** Tool Architect

---

## 🧠 Data Manager Specialized Track

| # | Modul | Lektionen | Quiz |
|---|-------|-----------|------|
| 6.2 | RAG Poisoning | lesson_6_2 | quiz_module_6_2 |
| 7 | OpenClaw Internals | lesson_7_1 | quiz_module_7_1 |
| 4 | Multi-Agent Security | 4.2, 4.3 | quiz_module_4 |

**Zertifizierung:** Data Security Specialist

---

## 🔬 Research Specialized Track

| # | Modul | Lektionen | Quiz |
|---|-------|-----------|------|
| 6.1 | Agentic AI Hijacking | lesson_6_1 | quiz_module_6 |
| 6.3 | Model Extraction | lesson_6_3 | quiz_module_6_3 |
| 2 | OWASP Top 10 | 2.1, 2.2 | quiz_module_2 |

**Zertifizierung:** AI Threats Analyst

---

## 📊 Training-Workflow

```
TRAINING SESSION PRO AGENT:

1. CEO sendet Training-Task via sessions_send
2. Agent liest Lektionen (lesson_basic_X.md)
3. Agent macht Quiz (quiz_basic_foundation.md)
4. Agent sendet Ergebnis an CEO
5. CEO validiert Ergebnis
6. ✅ Bestanden → Nächste Phase
   ❌ Nicht bestanden → Wiederholen
```

---

## ⏱️ Geschätzte Zeit

| Phase | Zeit |
|-------|------|
| Grund-Training (10 Module) | ~30-60 Min pro Agent |
| Specialized Track | ~30-60 Min pro Agent |
| **Gesamt pro Agent** | ~60-120 Min |

**Alle Agenten trainieren:** ~5-10 Stunden (parallel möglich)

---

## 🚨 Bekannte Probleme

| Problem | Workaround |
|---------|-----------|
| Builder Session stirbt nach ~8 Min | Regelmäßige Checkpoints, schnellere Quizze |
| sessions_send Timeout | Retry mit längerem Timeout |
| MiniMax als Professor-Backup | MiniMax direkt nutzen |

---

## ✅ Checkliste: Training abschließen

- [ ] CEO bestanden: Grund-Training + Modul 3
- [ ] Builder trainiert: Grund-Training + Module 1,3,7
- [ ] Security Officer trainiert: Grund-Training + Security Track
- [ ] Data Manager trainiert: Grund-Training + Data Track
- [ ] Research trainiert: Grund-Training + Research Track
- [ ] Alle Agenten in agent_certifications.json eingetragen

---

*Training Plan v1.0 — 2026-04-08*
