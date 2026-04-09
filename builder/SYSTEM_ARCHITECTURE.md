# System Architecture — EmpireHazeClaw Fleet

> **Zweck:** Zeigt wer wofür verantwortlich ist und wie Tasks durch das System fließen.
> **Version:** 1.0 — Erstellt: 2026-04-09

---

## 👥 Agent Roster & Responsibilities

| Agent | Rolle | Kern-Verantwortlichkeiten |
|-------|-------|--------------------------|
| **🦞 CEO (ClawMaster)** | Strategische Leitung | Delegation, Priorisierung, Nico-Kommunikation |
| **💻 Builder** | System-Architekt & Executor | Scripts bauen, Crons, Automatisierung, Integration |
| **🔒 Security Officer** | Security & Compliance Guard | Security Reviews, API-Key Management, Vulnerability Scanning |
| **🧠 Data Manager** | Knowledge & Memory Vault | Memory System, Wiki, Knowledge Graph, Datenqualität |
| **🔬 Research** | Research & Analysis | Markt-Recherche, Tech-Evaluation, Trends |
| **🔍 QC Officer** | Quality Control | Validation, Testing, Reviews |

---

## 🔄 Task Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                     TASK LIFECYCLE                          │
└─────────────────────────────────────────────────────────────┘

  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │RECEIVED  │ ──▶ │  WORKING │ ──▶ │ BLOCKED  │ ──▶ │   DONE   │ ──▶ │VERIFIED │
  └──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
       │                │                │                │                │
       ▼                ▼                ▼                ▼                ▼
   Task kommt      Task wird       Wartet auf        Task ist         CEO/Nico
   rein vom        aktiv           Ressource,        technisch         bestätigt
   CEO/Nico        bearbeitet      Approval oder     fertiggestellt    Ergebnis
                   durch Owner     Klärung                               
```

### State-Übergänge

| Von | Nach | Bedingung |
|-----|------|-----------|
| RECEIVED | WORKING | Owner hat Task angenommen |
| RECEIVED | BLOCKED | Fehlende Info, Ressource oder Approval |
| WORKING | BLOCKED | Blocker tritt auf (Error, Abhängigkeit) |
| WORKING | DONE | Definition of Done erfüllt |
| BLOCKED | WORKING | Blocker behoben |
| DONE | VERIFIED | CEO/Nico bestätigt |
| VERIFIED | — | Task geschlossen |

---

## 🔐 Security-Approval Workflow

**REGEL:** Alle Scripts die Security-relevante APIs/Keys nutzen → MÜSSEN zum Security Officer.

```
┌─────────────────────────────────────────────────────────────┐
│              SECURITY REVIEW WORKFLOW                       │
└─────────────────────────────────────────────────────────────┘

  Builder schreibt Script
          │
          ▼
  ┌───────────────────┐
  │ Security-Relevant? │
  │ (API Keys, Auth,   │
  │  Secrets, Crypto)  │
  └───────────────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
   JA          NEIN
    │           │
    ▼           ▼
 Builder ──▶ Script
 sendet       wird
 an Sec-      direkt
 Officer      deployed
 zur
 Review
    │
    ▼
┌───────────────────────────────────────┐
│       SECURITY OFFICER REVIEW          │
│                                        │
│  Prüft:                               │
│  □ API-Key-Rotation möglich?          │
│  □ Secrets in Config oder Env?        │
│  □ Input-Validation vorhanden?        │
│  □ Command Injection geschützt?        │
│  □ Rate-Limiting考虑?                 │
│                                        │
│  Ergebnis: APPROVED / REJECTED / FIX   │
└───────────────────────────────────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
 APPROVED     REJECTED
    │           │
    ▼           ▼
 Script     ──▶ Fixes
 wird       einbauen
 deployed   + Retry
```

---

## 👔 Approval-Matrix — Wer braucht was?

| Task-Typ |braucht Approval von | Ausnahme |
|----------|-------------------|----------|
| Neues Script mit API-Keys/Secrets | Security Officer | — |
| Änderung an openclaw.json | CEO | Config-Fixes ohne Funktionsänderung |
| Cron-Job Änderung | CEO | — |
| Neue Agenten erstellen | CEO | — |
| Memory/Wiki löschen | Data Manager | Archive/old_* |
| Security-relevante Config-Änderung | Security Officer | — |
| Neue Infrastructure (Server, DNS etc.) | CEO | — |

---

## 📋 Standard Workflows

### Workflow 1: Task von CEO erhalten

```
1. Task erhalten (via sessions_send oder Telegram)
2. Priority + Deadline + Definition of Done notieren
3. In TODOS.md eintragen mit State: RECEIVED
4. Plan erstellen
5. State: WORKING
6. Bauen/Testen
7. State: DONE
8. Report an CEO
9. State: VERIFIED
```

### Workflow 2: Security-Relevantes Script

```
1. Builder baut Script
2. Prüfe: Nutzt Script API-Keys, Secrets, Auth?
   □ JA → Security Officer zur Review
   □ NEIN → Direkt weiter
3. Security Officer reviewed (Feedback: OK/FIX)
4. Script wird deployed
5. Dokumentation in Wiki wenn nötig
```

### Workflow 3: Blocker-Escalation

```
1. Blocker tritt auf (Status: BLOCKED)
2. Notiere: Was ist blockiert? Wer kann helfen?
3. Kontaktiere zuständigen Agent direkt
4. Timeout nach 2h → Escalate an CEO
5. CEO entscheidet
```

---

## 📁 Verantwortlichkeits-Bereiche

### 💻 Builder
- `/workspace/scripts/*.py` — Alle Python Scripts
- `/workspace/builder/` — Builder Workspace
- Crons — Erstellen, Ändern, Monitoring
- openclaw.json — Config (mit CEO Approval)

### 🔒 Security Officer
- `/workspace/security/` — Security Workspace
- API-Key Rotation — Überwachung
- Security Reviews — Freigabe
- Secrets Management — Standards

### 🧠 Data Manager
- `/workspace/memory/` — Memory System
- Wiki — Pflege und Struktur
- Knowledge Graph — Auto-Population
- Datenqualität — Standards

### 🔬 Research
- `/workspace/research/` — Research Workspace
- Markt-Recherche
- Tech-Evaluation
- Konkurrenz-Analyse

### 🔍 QC Officer
- Script/Code Reviews
- Testing
- Validierung von Ergebnissen

---

## 🚨 Eskalations-Pfade

| Situation | Eskalation |
|-----------|-----------|
| Task blockiert >2h | → Direkt zuständigen Agent fragen |
| Agent antwortet nicht | → CEO informieren |
| Security-Issue entdeckt | → Security Officer SOFORT |
| Daten-Verlust | → CEO + Data Manager SOFORT |
| Gateway Down | → CEO SOFORT |

---

## 📊 Dashboard-Übersicht

| System | Status-Script | Cron |
|--------|--------------|------|
| Gateway | health_dashboard.py | — |
| Crons | health_dashboard.py | — |
| Disk/Memory | health_dashboard.py | — |
| Todo-Tracker | TODOS.md | Manuell |
| Wiki | wiki-index.md | Auto via lcm_wiki_sync.py |
| Knowledge Graph | kg_auto_populate.py | 06:00 UTC |

---

## 📝 Definition of Done (Template)

Für jede Task soll definiert sein:

```markdown
## Task: [Titel]

**Priority:** P0/P1/P2/P3
**Deadline:** YYYY-MM-DD HH:MM
**Owner:** [Agent]
**Approver:** [Wer muss freigeben]

**Definition of Done:**
- [ ] [Kriterium 1]
- [ ] [Kriterium 2]
- [ ] [Kriterium 3]

**Blocker:**
- [ ] [Bekannter Blocker]
```

---

*Erstellt: 2026-04-09*
*Version: 1.0*
*Owner: Builder*
*Zuletzt geändert: 2026-04-09*
