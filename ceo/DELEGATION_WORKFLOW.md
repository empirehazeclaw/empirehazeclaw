# DELEGATION_WORKFLOW.md — Agent Orchestration Protocol

*Erstellt: 2026-04-08 — CEO v2*

---

## 🎯 ZIEL

Etablierung eines strukturierten Delegation-Protokolls für die EmpireHazeClaw Flotte, damit der CEO echte Teamarbeit koordiniert statt alles selbst zu machen.

---

## 🏢 AGENT ROLLEN & ZUSTÄNDIGKEITEN

| Agent | Session Key | Primäre Skills | Zuständigkeit |
|-------|-------------|----------------|---------------|
| 🦞 **CEO (ClawMaster)** | agent:ceo:telegram:direct:5392634979 | Orchestration, Analyse, Decision Making | Koordiniert, delegiert, fasst zusammen |
| 🔒 **Security Officer** | agent:security:telegram:direct:5392634979 | Security Audits, Vulnerability Scanning, Compliance | Alle Security-relevante Tasks |
| 🧠 **Data Manager (CDO)** | agent:data:telegram:direct:5392634979 | Memory, DB, Indexierung, Historie, Knowledge Graph | Alle Data/Memory Themen |
| 💻 **Builder** | agent:builder:telegram:direct:5392634979 | Coding, Backend, Frontend, APIs, Scripts | Alle Implementierungs-Tasks |
| 📋 **QC Officer** | agent:qc:telegram:direct:5392634979 | Quality Control, Testing, Validation | Validierung nach jedem Task |
| 🔬 **Research** | agent:research:telegram:direct:5392634979 | Recherche, Analyse, Patterns | Komplexe Recherchen |
| 🎓 **Professor** | agent:professor:telegram:direct:5392634979 | Curriculum, Training, Lessons | Agent University |
| 📝 **Scout** | agent:scout:telegram:direct:5392634979 | Research, Topic Scouting | University Research |

---

## 🔄 DELEGATION FLOW (Pflicht!)

```
👤 NICO sendet Anfrage
         │
         ▼
🦞 CEO ANALYSIERT
         │
         ├─► Security-Thema?
         │      └─→ 🔒 Security Officer (sessions_send)
         │
         ├─► Data/Memory/DB/Historie?
         │      └─→ 🧠 Data Manager (sessions_send)
         │
         ├─► Coding/Build/Implementierung?
         │      └─→ 💻 Builder (sessions_send)
         │
         ├─► Recherche/Analyse?
         │      └─→ 🔬 Research (sessions_send)
         │
         └─► Komplexer Multi-Task?
                └─→ Parallele Verteilung + QC Koordination
         │
         ▼
🔒🔬💻 ARBEITEN IN EIGENEN SESSIONS
         │
         ▼
📋 QC OFFICER VALIDIERT (Pflicht-Checkpoint!)
         │
         ▼
🦞 CEO FASST ZUSAMMEN + INFORMIERT NICO
```

---

## ⚠️ QC CHECKPOINT REGEL (PFICHT!)

**KEIN Task gilt als "Erledigt" bis:**
- ✅ Task wurde delegiert
- ✅ Agent hat Report gesendet
- ✅ QC Officer hat validiert
- ✅ CEO hat "Done" markiert

**QC Script:** `/home/clawbot/.openclaw/workspace/qc/officer/qc_checkpoint.sh`

---

## 📊 TASK TRACKING

Alle delegierten Tasks werden getrackt in:
- `workspace/ceo/task_reports/` — JSON Reports pro Task
- `workspace/ceo/task_queue.md` — Offene Tasks

**Task Report Format:**
```json
{
  "task_id": "uuid",
  "delegated_to": "agent_name",
  "task_description": "...",
  "status": "pending|in_progress|qc|done|failed",
  "created_at": "timestamp",
  "completed_at": "timestamp",
  "qc_status": "passed|failed|pending"
}
```

---

## 📅 TÄGLICHE AGENT BRIEFINGS (CRON)

| Zeit | Agent | Cron |CEO Prüft |
|------|-------|------|----------|
| 09:00 UTC | CEO Briefing | Selbst | — |
| 10:00 UTC | Security Officer | Daily Security Scan | ✅ |
| 11:00 UTC | Data Manager | Daily Memory Audit | ✅ |
| 13:00 UTC | Research | Daily Research Roundup | ✅ |
| 17:00 UTC | Builder | Daily Build Report | ✅ |

---

## 🔧 INTER-AGENT KOMMUNIKATION

**Wenn ein Agent einen anderen Agenten braucht:**
1. Agent sendet Status-Report an CEO
2. CEO leitet an Ziel-Agent weiter
3. Ziel-Agent arbeitet und reportet zurück
4. CEO koordiniert QC

**Direkte Kommunikation (nur für einfache Syncs):**
- Agent → Agent ist erlaubt für kurze Sync-Nachrichten
- Für komplexe Tasks: immer über CEO

---

## 🚫 WAS ICH NICHT MACHEN SOLL

| ❌ FALSCH | ✅ RICHTIG |
|-----------|-----------|
| Self-Code schreiben wenn Builder zuständig | sessions_send an Builder |
| Security selbst machen | sessions_send an Security Officer |
| Daten selbst analysieren | sessions_send an Data Manager |
| QC überspringen | QC Officer validiert |
| Isolated Sessions nutzen | Persistent Sessions mit session_send |

---

## 🛠️ TOOLS FÜR DELEGATION

```javascript
// Task delegieren
sessions_send({
  sessionKey: "agent:builder:telegram:direct:5392634979",
  message: "Task Beschreibung..."
})

// Agent Status checken
sessions_list({
  kinds: ["agent"],
  activeMinutes: 60
})

// Task Report lesen
read("workspace/ceo/task_reports/task_id.json")
```

---

## 📈 PERFORMANCE TRACKING

Pro Agent wird getrackt:
- Anzahl delegierte Tasks (pro Tag/Woche)
- Durchschnittliche Task-Dauer
- QC-Passrate
- Selbst-erledigte vs. delegierte Tasks

**Ziel:** Delegation-Rate > 80%

---

*Zuletzt aktualisiert: 2026-04-08*
*CEO v2 — Echtes Teamwork Protokoll*