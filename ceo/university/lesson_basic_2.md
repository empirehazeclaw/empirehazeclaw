# Lektion 2: Identity & SOUL.md

## 🎯 Lernziel
Verstehe wie Agenten ihre Identität, Persona und ihren Workflow durch die SOUL.md definieren. Jeder Agent ist einzigartig durch seine SOUL.

---

## 2.1 Was ist SOUL.md?

Die **SOUL.md** ist das Herzstück jedes Agenten. Sie definiert:

1. **Wer** der Agent ist (Identität, Name, Persona)
2. **Was** der Agent kann (Fähigkeiten, Skills)
3. **Wie** der Agent arbeitet (Workflow, Prozesse)
4. **Wann** der Agent was tut (Trigger, Cron, Events)

### SOUL vs. Config
```
Config (openclaw.json)      →  Technische Konfiguration
SOUL.md                     →  Persönlichkeit & Workflow
```

Die Config sagt "wo" der Agent arbeitet, die SOUL sagt "wer" er ist.

---

## 2.2 SOUL.md Struktur

### Beispiel: CEO SOUL.md
```markdown
# SOUL.md - CEO Agent

## 🏛️ SOVEREIGN AGENT ARCHITECTURE

**Ich bin ClawMaster** — der CEO der EmpireHazeClaw Flotte.

**Wichtig:** Ich bin der SOVEREIGN Orchestrator. Andere Agenten sind spezialisierte Worker.

**Kernprinzipien:**
1. NIE direkt Code schreiben — immer an Builder delegieren
2. NIE selbst Security machen — immer an Security Officer
3. Nach jedem Task — QC Officer validiert

---

## 💎 Meine Werte

| Wert | Bedeutung |
|------|-----------|
| Strategie | Immer das große Bild sehen |
| Delegation | Ich delegiere, ich baue nicht selbst |
| Analyse | Erst denken, dann zuweisen |

---

## 🎯 Meine Mission

Die Flotte strategisch leiten und Nico informiert halten.
```

---

## 2.3 Pflichtfelder in SOUL.md

| Feld | Pflicht | Beschreibung |
|------|---------|--------------|
| `## 🏛️ SOVEREIGN ARCHITECTURE` | Ja | Definiert die Rolle |
| Agent-Name | Ja | Wer bin ich |
| Kernprinzipien | Ja | Was sind meine Regeln |
| Werte | Empfohlen | Meine ethischen Leitlinien |
| Mission | Empfohlen | Was ist mein Zweck |
| Workflow | Ja | Wie arbeite ich |
| Delegation-Rules | Ja | Wann delegiere ich |

---

## 2.4 Die Sovereign Architecture

### Das Prinzip

Ein **SOVEREIGN Agent** ist ein Agent der:
1. Andere Agenten orchestriert
2. Nicht selbst implementiert
3. Immer delegiert statt selbst zu bauen

### CEO als Sovereign
```
┌────────────────────────────────────────┐
│           👤 NICO (DER BOSS)           │
└────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│     🦞 CLAWMASTER (ICH) — CEO         │
│                                        │
│  1. Analysiere Anfrage                │
│  2. Route an richtigen Agenten         │
│  3. Validiere via QC Officer           │
│  4. Informiere Nico                    │
└────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │Security │ │ Builder │ │  Data   │
   │Officer  │ │         │ │Manager  │
   └─────────┘ └─────────┘ └─────────┘
```

---

## 2.5 Identität Aufbauen

### IDENTITY.md — Persönliche Details

Zusätzlich zur SOUL.md kann ein Agent eine `IDENTITY.md` haben:

```markdown
# IDENTITY.md - Who Am I?

- **Name:** ClawMaster
- **Creature:** AI Lobster (🦞)
- **Vibe:** Sharp, strategic, decisive
- **Emoji:** 🦞
- **Avatar:** avatars/openclaw.png
```

---

## 2.6 Workflow-Definition

### Der Sovereign Workflow

```markdown
## 🔄 Sovereign Agent Workflow

### Bei eingehender Anfrage:

1. **ANALYSIEREN**
   - Was ist die Anfrage?
   - Ist es Security-relevant?
   - Ist es Data-relevant?
   - Ist es Coding-relevant?
   - Ist es Recherche?

2. **ROUTEN**
   - Security → Security Officer (sessions_send)
   - Data/Memory → Data Manager (sessions_send)
   - Coding → Builder (sessions_send)
   - Recherche → Research (sessions_send)

3. **VALIDIEREN**
   - QC Officer prüft Ergebnis

4. **INFORMIEREN**
   - Zusammenfassung an Nico
```

---

## 2.7 Routing-Entscheidungen

### Decision Matrix

| Anfrage enthält... | Route zu | Tool |
|-------------------|----------|------|
| "Security", "Audit", "Prüfe" | Security Officer | sessions_send |
| "Datenbank", "Memory", "Index" | Data Manager | sessions_send |
| "Code", "Script", "API", "Bau" | Builder | sessions_send |
| "Recherche", "Analysiere", "Finde" | Research | sessions_send |
| "Zusammenfassung", "Bericht" | QC Officer | sessions_send |
| Strategie, Orchestrierung | CEO (selbst) | - |

---

## 2.8 Multi-Agent Kommunikation

### sessions_send Protokoll

```javascript
// Nachricht an anderen Agent senden
sessions_send({
  sessionKey: "agent:security:telegram:direct:5392634979",
  message: "Führe Security Audit durch für...",
  timeoutSeconds: 120
})
```

### Handshake-Protokoll

```
CEO sendet Task an Agent
         │
         ▼
Agent arbeitet (mit eigener SOUL)
         │
         ▼
Agent sendet Ergebnis-Report an CEO
         │
         ▼
CEO leitet an QC Officer
         │
         ▼
QC Officer validiert
         │
         ▼
CEO informiert Nico
```

---

## 2.9 SOUL Injection bei Cron-Jobs

### Problem
Isolierte Cron-Jobs haben keine Identität — sie laufen "blind".

### Lösung: SOUL Injection

```javascript
// Cron-Job mit SOUL Injection
{
  "sessionTarget": "isolated",
  "payload": {
    "message": "DU BIST DER SOVEREIGN SECURITY OFFICER.\n\n" +
              "1. LIES DEINE SOUL.md: cat .../SOUL.md\n" +
              "2. ARBEITSVERZEICHNIS: cd .../workspace/security\n" +
              "3. FÜHRE AUDIT DURCH..."
  }
}
```

---

## 2.10 Workspace und SOUL

### Zusammenspiel

```
~/.openclaw/workspace/
├── ceo/
│   ├── SOUL.md          ← CEO Identität
│   ├── IDENTITY.md      ← Persönliche Details
│   ├── memory/          ← CEO Memory
│   └── work/            ← Aktuelle Tasks
├── builder/
│   ├── SOUL.md          ← Builder Identität
│   └── ...
├── security/
│   ├── SOUL.md          ← Security Officer Identität
│   └── ...
└── data/
    ├── SOUL.md          ← Data Manager Identität
    └── ...
```

---

## ⚠️ Häufige Fehler

### Fehler 1: SOUL.md nicht gelesen
```
Problem: Agent startet ohne seine Identität zu kennen
Lösung: Immer zuerst SOUL.md lesen (cat SOUL.md)
```

### Fehler 2: Direkt implementiert statt delegiert
```
Problem: CEO baut selbst statt zu delegieren
Lösung: Kernprinzip "NIE selbst bauen" befolgen
```

### Fehler 3: Falsches Routing
```
Problem: Security-Task an Builder statt Security Officer
Lösung: Routing-Matrix studieren und anwenden
```

---

## 📝 Zusammenfassung

| Konzept | Beschreibung |
|---------|--------------|
| SOUL.md | Definitions-Datei für Identität, Workflow, Prinzipien |
| Sovereign Agent | Orchestriert andere, implementiert nicht selbst |
| Routing | Anfragen an richtigen Agenten weiterleiten |
| sessions_send | Tool für Agent-zu-Agent Kommunikation |
| SOUL Injection | Identität in isolierte Cron-Jobs einbetten |

---

## ✅ Checkpoint

- [ ] Was ist der Unterschied zwischen SOUL.md und openclaw.json?
- [ ] Wer ist der "Sovereign Orchestrator" in der Flotte?
- [ ] Wann sollte der CEO NICHT direkt antworten, sondern delegieren?
- [ ] Wie heißt das Tool um Nachrichten an andere Agents zu senden?
- [ ] Was bedeutet "SOUL Injection" bei Cron-Jobs?

---

*Lektion 2 — Identity & SOUL.md — Version 1.0*
